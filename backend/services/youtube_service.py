import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def is_youtube_url(url: str) -> bool:
    """Checks if the inputed text is a youtube link or not"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    youtube_match = re.match(youtube_regex, url)
    return bool(youtube_match)

def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL"""
    # Handle shortened URL
    if 'youtu.be' in url:
        path = urlparse(url).path
        return path.strip('/')
    # Handle regular URLs
    else:
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('v', [''])[0]

def format_transcript(transcript_items):
    """Turns returned transcript items in regular readable text"""
    return ' '.join(item['text'] for item in transcript_items)

async def get_youtube_transcript(url: str) -> str:
    """Fetches transcript of a YouTube video using YouTube's transcript API"""
    if not is_youtube_url(url):
        raise ValueError("URL is not a valid YouTube URL")
    
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Could not extract video ID from the URL")
    
    try:   
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = format_transcript(transcript_list)
        
        # Set max length of transcript to 20000--otherwise, might take too long to process
        max_length = 20000  
        if len(transcript_text) > max_length:
            transcript_text = transcript_text[:max_length] + "...\n[Transcript truncated due to length]"
            
        return transcript_text
    except Exception as e:
        raise Exception(f"Error fetching YouTube transcript: {str(e)}")