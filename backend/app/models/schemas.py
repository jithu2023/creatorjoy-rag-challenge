from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VideoMetadata(BaseModel):
    video_id: str
    platform: str
    url: str
    title: str
    creator_name: str
    follower_count: int
    views: int
    likes: int
    comments: int
    hashtags: List[str]
    upload_date: datetime
    duration_seconds: int
    transcript: str
    
    @property
    def engagement_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return ((self.likes + self.comments) / self.views) * 100

class VideoInput(BaseModel):
    url_a: str
    url_b: str