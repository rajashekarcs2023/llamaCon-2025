from pydantic import BaseModel
from typing import Optional, List

class TimelineEvent(BaseModel):
    """
    Model representing a timeline event of a suspect sighting
    """
    id: str
    suspectId: str
    videoId: str
    timestamp: str
    confidence: float
    thumbnailUrl: str
    description: str
    startTime: float  # Start time in seconds within the video
    endTime: float    # End time in seconds within the video
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "event-123456",
                "suspectId": "suspect-123456",
                "videoId": "video-123456",
                "timestamp": "2025-05-04T08:15:00Z",
                "confidence": 85.5,
                "thumbnailUrl": "/events/event-123456.jpg",
                "description": "Suspect entered through north entrance",
                "startTime": 30.5,
                "endTime": 45.2
            }
        }
