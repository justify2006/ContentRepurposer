import os
import base64
import io
import json
import asyncio
from typing import List, Dict, Any, Literal
import google.generativeai as genai
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GEMINI_MODEL_NAME = 'gemini-1.5-flash' 
DALLE_MODEL_NAME = "dall-e-3"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Warning: OPENAI_API_KEY not found. DALL-E generation will fail")
    
# --- Text Transformation Services ---

def summarize_text(text: str, length: str = 'medium', tone: str = 'neutral') -> str:
    """Generates a summary using the Gemini model"""
        
    length_map = {'short': '2-3 sentences', 'medium': '4-6 sentences', 'long': '7-10 sentences'}
    prompt = f"""
    Summarize the following text in {length_map.get(length, '4-6 sentences')} with a {tone} tone.
    Maintain the key points and main message.
    Text: {text}
    """
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_social_post(text: str, platform: str = 'linkedin', tone: str = 'professional') -> str:
    """Generates a social media post using the Gemini model"""
    if not GEMINI_API_KEY:
        raise ConnectionError("Gemini API key not configured")
        
    platform_guides = {
        'linkedin': {'style': 'professional, engaging', 'elements': 'hook, key insights, conclusion, 3-5 hashtags'},
        'twitter': {'style': 'concise, engaging', 'elements': 'hook, key points, takeaway, 1-2 hashtags'},
        'facebook': {'style': 'conversational', 'elements': 'opener, main point, call to action'}
    }
    config = platform_guides.get(platform.lower(), platform_guides['linkedin'])
    prompt = f"""
    Create a {tone} {platform} post based on this content.
    Style: {config['style']}. Include: {config['elements']}.
    Content: {text}
    """
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt, generation_config={"temperature": 0.7})
    return response.text.strip()

# --- Visual Generation Services ---

ContentType = Literal["stats-based", "descriptive", "unknown"]

def _determine_content_type(text: str) -> ContentType:
    """Classifies content as 'stats-based' or 'descriptive' via Gemini"""
    if not GEMINI_API_KEY:
        return "unknown"

    prompt = f"""
    Is the primary focus of the following text quantifiable data/statistics OR descriptive narrative/concepts?
    Respond ONLY with the word "stats-based" or "descriptive".
    Text: {text}
    """
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    content_type = response.text.strip().lower()
    return content_type if content_type in ["stats-based", "descriptive"] else "unknown"

def _extract_chart_definitions(text: str) -> List[Dict[str, Any]]:
    """Extracts up to 3 chart definitions from text via Gemini"""
    if not GEMINI_API_KEY:
        return []
        
    prompt = f"""
    Analyze text, find up to 3 distinct data sets for a bar or pie chart.
    Respond ONLY with a JSON list (max 3 items). Each item = {{ "chart_type": "bar"|"pie", "data": {{"labels": [], "values": []}}, "title": "", "y_axis_label": "" (only for bar) }}.
    If none found, respond only with [].
    Text: {text}
    """
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    response_text = response.text.strip().strip('```json').strip('```')
    
    try:
        definitions = json.loads(response_text)
        if not isinstance(definitions, list):
            return []

        return [
            d for d in definitions[:3]
            if isinstance(d, dict)
            and d.get('chart_type') in ['bar', 'pie']
            and isinstance(d.get('data'), dict)
            and isinstance(d.get('data', {}).get('labels'), list)
            and isinstance(d.get('data', {}).get('values'), list)
        ]
    except json.JSONDecodeError:
        return []

def _create_chart_image(chart_definition: Dict[str, Any]) -> bytes:
    """Creates PNG bytes for a single chart definition using Matplotlib"""
    chart_type = chart_definition.get('chart_type')
    data = chart_definition.get('data', {})
    title = chart_definition.get('title', f"Generated {chart_type.capitalize() if chart_type else ''} Chart")
    labels = data.get('labels', [])
    values = data.get('values', [])
    
    if not labels or not values or len(labels) != len(values):
        raise ValueError(f"Invalid data for {chart_type} chart")

    numeric_values = [float(v) for v in values]
    figure, axes = plt.subplots(figsize=(8, 5) if chart_type == 'bar' else (6, 6))
    
    try:
        if chart_type == 'bar':
            y_label = chart_definition.get('y_axis_label', 'Values')
            axes.bar(labels, numeric_values)
            axes.set_ylabel(y_label)
            axes.set_title(title)
            axes.tick_params(axis='x', rotation=45, labelsize='small')
            plt.subplots_adjust(bottom=0.25) 
        elif chart_type == 'pie':
            if sum(numeric_values) <= 0:
                raise ValueError("Invalid pie chart values")
            axes.pie(numeric_values, labels=labels, autopct='%1.1f%%', startangle=90)
            axes.axis('equal') 
            axes.set_title(title)
            plt.tight_layout()
        else:
            raise ValueError("Unsupported chart type")

        image_buffer = io.BytesIO()
        plt.savefig(image_buffer, format='png')
        image_buffer.seek(0)
        return image_buffer.getvalue()
    finally:
        plt.close(figure)

async def _generate_dalle_infographic(text: str) -> bytes:
    """Generates PNG image bytes using DALL-E 3 based on text"""
    if not openai_client:
        raise ConnectionError("OpenAI client not configured")

    dalle_prompt = f"Create a simple, clean infographic visualizing the key points of this text: {text[:1000]}"
    response = await asyncio.to_thread(
        openai_client.images.generate,
        model=DALLE_MODEL_NAME,
        prompt=dalle_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json"
    )
    
    if not response.data or not response.data[0].b64_json:
        raise ValueError("Failed to generate image")
        
    return base64.b64decode(response.data[0].b64_json)

def _encode_image_to_data_uri(image_bytes: bytes) -> str:
    """Encodes PNG image bytes into a base64 data URI"""
    return f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

async def generate_visual_post(text: str) -> List[str]:
    """Generates visual representations (charts or infographic) based on text content"""
    content_type = _determine_content_type(text)
    generated_images = []

    if content_type == "stats-based":
        chart_definitions = _extract_chart_definitions(text)
        if not chart_definitions:
            raise ValueError("No chart data found in content")
             
        for definition in chart_definitions:
            try:
                chart_bytes = _create_chart_image(definition)
                generated_images.append(chart_bytes)
            except Exception:
                continue
                
        if not generated_images:
            raise ValueError("Failed to generate any charts")
             
    elif content_type == "descriptive":
        infographic_bytes = await _generate_dalle_infographic(text)
        generated_images.append(infographic_bytes)
    else:
        raise ValueError("Content type not suitable for visualization")

    return [_encode_image_to_data_uri(img_bytes) for img_bytes in generated_images]