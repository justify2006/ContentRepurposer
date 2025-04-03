import re
from urllib.parse import urlparse, parse_qs
import httpx
from youtube_transcript_api import YouTubeTranscriptApi

def is_youtube_url(url: str) -> bool:
    """Check if the provided string is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    youtube_match = re.match(youtube_regex, url)
    return bool(youtube_match)

def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL."""
    if 'youtu.be' in url:
        # Handle shortened URLs like https://youtu.be/VIDEO_ID
        path = urlparse(url).path
        return path.strip('/')
    else:
        # Handle regular URLs like https://www.youtube.com/watch?v=VIDEO_ID
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('v', [''])[0]

def format_transcript(transcript_items):
    """Format transcript items into plain text."""
    return ' '.join(item['text'] for item in transcript_items)

async def get_youtube_transcript(url: str) -> str:
    """Fetch the transcript of a YouTube video using YouTube's transcript API."""
    if not is_youtube_url(url):
        raise ValueError("The provided URL is not a valid YouTube URL")
    
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Could not extract video ID from the URL")
    
    try:
        # Get the transcript using the YouTube Transcript API
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript as plain text
        transcript_text = format_transcript(transcript_list)
        
        # If the transcript is too long, truncate it to a reasonable size
        max_length = 15000  # Approximately 10-15 minutes of video
        if len(transcript_text) > max_length:
            transcript_text = transcript_text[:max_length] + "...\n[Transcript truncated due to length]"
            
        return transcript_text
    except Exception as e:
        raise Exception(f"Error fetching YouTube transcript: {str(e)}") 