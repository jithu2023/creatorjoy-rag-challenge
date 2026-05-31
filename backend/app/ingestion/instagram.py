import re
from datetime import datetime
from typing import Optional

def extract_instagram_reel_id(url: str) -> Optional[str]:
    patterns = [
        r'(?:instagram\.com\/reel\/)([\w-]+)',
        r'(?:instagram\.com\/p\/)([\w-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def process_instagram_reel(url: str) -> dict:
    """
    Mock Instagram Reel processor.
    
    NOTE: Instagram's public API blocks programmatic access without business verification.
    In production, this would use the official Instagram Graph API with OAuth.
    For this technical screening, we return realistic mock data to demonstrate the RAG pipeline.
    """
    print(f"Processing Instagram URL (mock mode): {url}")
    
    shortcode = extract_instagram_reel_id(url) or "mock_reel_id"
    
    # Match the exact field names expected by main.py
    return {
        "video_id": shortcode,
        "title": "Instagram Reel: How to get a swimmer's physique 💪",
        "creator_name": "thesistraining",
        "follower_count": 125000,
        "views": 61000,
        "likes": 61000,
        "comments": 342,
        "hashtags": ["#gym", "#swimming", "#buildmuscle", "#workout", "#hardgainer"],
        "upload_date": datetime.now(),
        "duration_seconds": 30,
        "url": url,
        "platform": "instagram",
        "transcript": "This Instagram Reel shows workout tips for developing a swimmer's physique. The creator emphasizes developing lats, wide shoulders, and strong arms to create a V-taper torso. Key exercises and nutrition tips are demonstrated throughout the 30-second clip."
    }