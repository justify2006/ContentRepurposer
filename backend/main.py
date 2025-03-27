from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from services.ai_service import summarize_text, generate_social_post


load_dotenv()


app = FastAPI(title="Content Repurposer API")

#initializes Cross-Origin resource sharing to allow front-end to talk to the back-end no matter what the origin, method, or header is
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Define request models
class SummarizeRequest(BaseModel):
    text: str
    length: Optional[str] = "medium"  #these are the default lengths, tones, platforms when the user doesnt select anything
    tone: Optional[str] = "neutral"   

class SocialPostRequest(BaseModel):
    text: str
    platform: Optional[str] = "linkedin"  
    tone: Optional[str] = "professional"  

class SummarizeResponse(BaseModel):
    summary: str

class SocialPostResponse(BaseModel):
    post: str


#FastAPI endpoints that define the root, health, and social-post in REST API
@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/api/health")
async def health_check():
    """Check if the API is running"""
    return {"status": "ok", "message": "Content Repurposer API is running"}

@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """Generate a summary of the provided text"""
    if not request.text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        summary = summarize_text(request.text, request.length, request.tone)
        return SummarizeResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/social-post", response_model=SocialPostResponse)
async def social_post(request: SocialPostRequest):
    """Generate a social media post based on the provided text"""
    if not request.text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        post = generate_social_post(request.text, request.platform, request.tone)
        return SocialPostResponse(post=post)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#runs when uvicorn is reloaded
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)