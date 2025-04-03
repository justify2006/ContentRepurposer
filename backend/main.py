from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from services.ai_service import summarize_text, generate_social_post
from services.youtube_service import is_youtube_url, get_youtube_transcript


load_dotenv()


app = FastAPI(title="Content Repurposer API")

# Allow frontend domains, set this properly after deployment
frontend_urls = [
    "https://your-frontend-url.vercel.app",  # Update this with your Vercel domain
    "http://localhost:3000",  # For local development
]

#initializes Cross-Origin resource sharing to allow front-end to talk to the back-end no matter what the origin, method, or header is
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


class SummarizeRequest(BaseModel):
    text: str
    length: Optional[str] = "medium"  #these are the default lengths, tones, platforms when the user doesnt select anything
    tone: Optional[str] = "neutral"   

class SocialPostRequest(BaseModel):
    text: str
    platform: Optional[str] = "linkedin"  
    tone: Optional[str] = "professional"  

class YouTubeTranscriptRequest(BaseModel):
    url: str
    
class TranscriptResponse(BaseModel):
    transcript: str

class SummarizeResponse(BaseModel):
    summary: str

class SocialPostResponse(BaseModel):
    post: str


#FastAPI endpoints that define the root, health, summarize, youtube, and social-post in REST API
@app.get("/", response_class=HTMLResponse)

async def root():
    """redirects to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/api/health")

async def health_check():
    """checks if the API is running"""
    return {"status": "ok", "message": "Content Repurposer API is running"}

@app.post("/api/youtube-transcript", response_model=TranscriptResponse)

async def youtube_transcript(request: YouTubeTranscriptRequest):
    """extracts transcript from a YouTube video URL"""
    if not request.url:
        raise HTTPException(400, "No URL provided")
    
    if not is_youtube_url(request.url):
        raise HTTPException(400, "Invalid YouTube URL")
    
    transcript = await get_youtube_transcript(request.url)
    return TranscriptResponse(transcript=transcript)

@app.post("/api/summarize", response_model=SummarizeResponse)

async def summarize(request: SummarizeRequest):
    """generates a summary of the provided text"""
    if not request.text:
        raise HTTPException(400, "No text provided")
    
    summary = summarize_text(request.text, request.length, request.tone)
    return SummarizeResponse(summary=summary)

@app.post("/api/social-post", response_model=SocialPostResponse)

async def social_post(request: SocialPostRequest):
    """generates a social media post based on the provided text"""
    if not request.text:
        raise HTTPException(400, "No text provided")
    
    post = generate_social_post(request.text, request.platform, request.tone)
    return SocialPostResponse(post=post)

#runs when uvicorn is reloaded -- and on render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)