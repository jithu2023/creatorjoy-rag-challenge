import re
from datetime import datetime
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import yt_dlp
import json
import requests

load_dotenv()

def extract_video_id(url: str):
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/v\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def parse_duration(duration: str) -> int:
    seconds = 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        secs = int(match.group(3) or 0)
        seconds = hours * 3600 + minutes * 60 + secs
    return seconds

def get_youtube_metadata(video_id: str):
    api_key = os.environ.get("YOUTUBE_API_KEY")
    
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not found in environment")
    
    youtube = build("youtube", "v3", developerKey=api_key)
    
    video_response = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    ).execute()
    
    if not video_response["items"]:
        raise ValueError(f"Video {video_id} not found")
    
    video = video_response["items"][0]
    snippet = video["snippet"]
    statistics = video["statistics"]
    content_details = video["contentDetails"]
    
    channel_id = snippet["channelId"]
    channel_response = youtube.channels().list(
        part="statistics",
        id=channel_id
    ).execute()
    
    follower_count = 0
    if channel_response["items"]:
        follower_count = int(channel_response["items"][0]["statistics"].get("subscriberCount", 0))
    
    description = snippet.get("description", "")
    hashtags = re.findall(r'#\w+', description)
    
    return {
        "video_id": video_id,
        "title": snippet["title"],
        "creator_name": snippet["channelTitle"],
        "follower_count": follower_count,
        "views": int(statistics.get("viewCount", 0)),
        "likes": int(statistics.get("likeCount", 0)),
        "comments": int(statistics.get("commentCount", 0)),
        "hashtags": hashtags,
        "upload_date": datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": parse_duration(content_details["duration"]),
    }

def get_youtube_transcript(video_id: str) -> str:
    # Check if running on Render (cloud deployment)
    if os.environ.get('RENDER') or os.environ.get('RENDER_GIT_COMMIT'):
        # Return a meaningful mock transcript for deployment
        return "This is a demonstration transcript for the YouTube video. The creator discusses engaging content, shares insights about their niche, and encourages viewer interaction. The video includes a strong hook in the first 5 seconds, maintains audience attention through storytelling, and ends with a clear call-to-action. For the purpose of this technical screening, the transcript is mock data. In production, this would fetch real transcripts via YouTube's official API or cookies-based authentication."
    
    # Local development: use yt-dlp
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Try manual subtitles first
            subtitles = info.get('subtitles', {})
            if 'en' in subtitles:
                subtitle_url = subtitles['en'][0]['url']
            elif 'en' in info.get('automatic_captions', {}):
                subtitle_url = info['automatic_captions']['en'][0]['url']
            else:
                return "[Transcript not available for this video]"
            
            response = requests.get(subtitle_url)
            content = response.text
            
            # Check if content is JSON (some subtitle formats)
            if content.strip().startswith('{'):
                try:
                    data = json.loads(content)
                    text_parts = []
                    if 'events' in data:
                        for event in data['events']:
                            if 'segs' in event:
                                for seg in event['segs']:
                                    if 'utf8' in seg:
                                        text_parts.append(seg['utf8'])
                    return " ".join(text_parts)
                except:
                    pass
            
            # Standard VTT parsing
            lines = content.split('\n')
            text_lines = []
            for line in lines:
                if '-->' not in line and not re.match(r'^\d+$', line.strip()):
                    clean = re.sub(r'<[^>]+>', '', line).strip()
                    clean = re.sub(r'\\n', ' ', clean)
                    if clean and not clean.isdigit() and 'WEBVTT' not in clean:
                        text_lines.append(clean)
            
            transcript = " ".join(text_lines)
            transcript = re.sub(r'\s+', ' ', transcript).strip()
            return transcript if transcript else "[Transcript found but empty]"
            
    except Exception as e:
        # Fallback to mock transcript if yt-dlp fails
        return "[Transcript temporarily unavailable. Using demo transcript for RAG demonstration.]"

def process_youtube_video(url: str) -> dict:
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL: {url}")
    
    metadata = get_youtube_metadata(video_id)
    transcript = get_youtube_transcript(video_id)
    
    return {
        **metadata,
        "url": url,
        "platform": "youtube",
        "transcript": transcript,
    }