import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def summarize_text(text: str, length: str = 'medium', tone: str = 'neutral') -> str:
    
    #options regarding length of summary
    length_guide = {
        'short': '2-3 sentences',
        'medium': '4-6 sentences',
        'long': '7-10 sentences'
    }
    
    # Gemini prompt input
    prompt = f"""
    Summarize the following text in {length_guide[length]} with a {tone} tone.
    Maintain the key points and main message while preserving the original intent and ideas.
    
    Text to summarize:
    {text}
    """
    
    try:
       
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # honestly kinda just asked chat gpt what good configs would be. Told me it should be a lower temperature
        generation_config = {
            "temperature": 0.2,  
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Generate the summary
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        
        return response.text.strip()
    except Exception as e:
        
        print(f"Error generating summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")

def generate_social_post(text: str, platform: str = 'linkedin', tone: str = 'professional') -> str:
    
    # Configuartions based on the type of post you do on each platform
    platform_guide = {
        'linkedin': {
            'length': '1250-1600 characters',
            'style': 'professional with paragraph breaks',
            'elements': 'engaging hook, key insights, thoughtful conclusion, 3-5 relevant hashtags'
        },
        'twitter': {
            'length': '100-280 characters',
            'style': 'concise and engaging',
            'elements': 'compelling hook, key points, actionable takeaway, 1-2 relevant hashtags'
        },
        'facebook': {
            'length': '250-500 characters',
            'style': 'conversational',
            'elements': 'interesting opener, main point, question or call to action'
        }
    }
    
    platform_config = platform_guide.get(platform.lower(), platform_guide['linkedin'])
    
  
    prompt = f"""
    Create a {tone} {platform} post based on the following content.
    The post should be {platform_config['style']} and include {platform_config['elements']}.
    Keep the post to {platform_config['length']}.
    
    Original content:
    {text}
    """
    
    try:
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Higher temperature because its a more creative post?
        generation_config = {
            "temperature": 0.7,  
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
       
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
      
        return response.text.strip()
    except Exception as e:
     
        print(f"Error generating social post: {str(e)}")
        raise Exception(f"Failed to generate social post: {str(e)}")