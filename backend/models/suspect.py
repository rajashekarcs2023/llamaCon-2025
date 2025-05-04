from pydantic import BaseModel
from typing import Optional

class Suspect(BaseModel):
    """
    Model representing a suspect to be tracked
    """
    id: str
    imageUrl: str
    name: Optional[str] = None
    description: Optional[str] = None
    lastSeen: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "suspect-123456",
                "imageUrl": "/suspects/suspect-123456.jpg",
                "name": "Unknown Subject",
                "description": "Male, approximately 30-40 years old, wearing dark jacket",
                "lastSeen": "2025-05-04T08:15:00Z"
            }
        }
