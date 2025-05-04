from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoFeed(BaseModel):
    """
    Model representing a CCTV video feed
    """
    id: str
    name: str
    location: str
    timestamp: str
    duration: float
    fileUrl: str
    thumbnailUrl: str
    size: int
    processed: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "video-123456",
                "name": "North Entrance CCTV",
                "location": "Main Building, Floor 1",
                "timestamp": "2025-05-04T08:00:00Z",
                "duration": 120.5,
                "fileUrl": "/videos/video-123456.mp4",
                "thumbnailUrl": "/videos/video-123456_thumb.jpg",
                "size": 15728640,
                "processed": True
            }
        }
