from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryResponse(BaseModel):
    """
    Model representing a response to a natural language query
    """
    text: str
    visualData: Optional[Dict[str, Any]] = None

class Query(BaseModel):
    """
    Model representing a natural language query about an analysis
    """
    id: str
    text: str
    timestamp: str
    response: Optional[QueryResponse] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "query-123456",
                "text": "Where was the suspect at 10:30 AM?",
                "timestamp": "2025-05-04T08:45:00Z",
                "response": {
                    "text": "At 10:30 AM, the suspect was seen in the main hallway on the first floor.",
                    "visualData": {
                        "type": "image",
                        "url": "/events/event-789012.jpg"
                    }
                }
            }
        }
