from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, Field
import os
from dotenv import load_dotenv
from typing import List

from services.ai_service import (
    summarize_text, 
    generate_social_post, 
    generate_visual_post
)
from services.youtube_service import (
    is_youtube_url, 
    get_youtube_transcript
)

load_dotenv()

app = FastAPI(
    title="Content Repurposer API",
    description="API for summarizing text, generating social media posts, and creating visuals from content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Input text that cannot be empty")

class SummarizeRequest(TextInput):
    length: str = "medium"
    tone: str = "neutral"

class SocialPostRequest(TextInput):
    platform: str = "linkedin"
    tone: str = "professional"

class YouTubeTranscriptRequest(BaseModel):
    url: HttpUrl

class VisualPostRequest(TextInput):
    pass

class TranscriptResponse(BaseModel):
    transcript: str

class SummarizeResponse(BaseModel):
    summary: str

class SocialPostResponse(BaseModel):
    post: str

class VisualPostResponse(BaseModel):
    image_data_list: List[str]


#API Endpoints
@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/api/health", tags=["Utility"])
async def health_check():
    return {"status": "ok"}

@app.post("/api/youtube-transcript", 
            response_model=TranscriptResponse, 
            tags=["Content Input"],
            summary="Fetch YouTube Transcript")
async def fetch_youtube_transcript(request: YouTubeTranscriptRequest):
    """Fetches the transcript from a valid YouTube video URL"""
    url_str = str(request.url)
    print(f"Received request for YouTube transcript: {url_str}")

    if not is_youtube_url(url_str):
        print(f"Validation failed: {url_str} is not a YouTube URL according to regex.")
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        print(f"Attempting to fetch transcript for: {url_str}")
        transcript = await get_youtube_transcript(url_str)
        print(f"Successfully fetched transcript for: {url_str}")
        return TranscriptResponse(transcript=transcript)
    except Exception as e:
        print(f"ERROR fetching transcript for {url_str}: {type(e).__name__} - {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/summarize", 
            response_model=SummarizeResponse, 
            tags=["Content Generation"],
            summary="Generate Text Summary")
async def generate_summary(request: SummarizeRequest):
    """Generates a text summary based on input text, length, and tone"""
    try:
        summary = summarize_text(request.text, request.length, request.tone)
        return SummarizeResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social-post", 
            response_model=SocialPostResponse, 
            tags=["Content Generation"],
            summary="Generate Social Media Post")
async def generate_social_media_post(request: SocialPostRequest):
    """Generates a social media post tailored for a specific platform and tone"""
    try:
        post = generate_social_post(request.text, request.platform, request.tone)
        return SocialPostResponse(post=post)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/visual-post", 
            response_model=VisualPostResponse, 
            tags=["Content Generation"],
            summary="Generate Visual Content")
async def generate_visuals(request: VisualPostRequest):
    """Generates Matplotlib charts or a DALL-E infographic based on text analysis"""
    try:
        print(f"Received request for visual post generation.")
        image_uris = await generate_visual_post(request.text)
        if not image_uris:
            print("Visual generation returned no images.")
            raise HTTPException(status_code=500, detail="Failed to generate visuals")
        print("Visual post generation successful.")
        return VisualPostResponse(image_data_list=image_uris)
    except Exception as e:
        print(f"ERROR in generate_visuals: {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=str(e))

#Run on reload
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting API server on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)