from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from models.timeline import TimelineEvent
from models.graph import GraphData

class TimeframeFilter(BaseModel):
    """
    Model representing a timeframe filter for analysis
    """
    start: str
    end: str

class AnalysisOptions(BaseModel):
    """
    Model representing options for analysis
    """
    includeNarration: bool = False
    language: str = "en"

class AnalysisRequest(BaseModel):
    """
    Model representing a request to analyze videos for a suspect
    """
    suspectId: str
    videoIds: List[str]
    timeframe: Optional[TimeframeFilter] = None
    options: Optional[AnalysisOptions] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "suspectId": "suspect-123456",
                "videoIds": ["video-123456", "video-789012"],
                "timeframe": {
                    "start": "2025-05-04T08:00:00Z",
                    "end": "2025-05-04T09:00:00Z"
                },
                "options": {
                    "includeNarration": True,
                    "language": "en"
                }
            }
        }

class AnalysisResult(BaseModel):
    """
    Model representing the result of a suspect tracking analysis
    """
    id: str
    suspectId: str
    timeline: List[TimelineEvent]
    graph: GraphData
    summary: str
    narrationUrl: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "analysis-123456",
                "suspectId": "suspect-123456",
                "timeline": [],  # Will contain TimelineEvent objects
                "graph": {
                    "nodes": [],  # Will contain GraphNode objects
                    "edges": []   # Will contain GraphEdge objects
                },
                "summary": "Suspect was tracked across multiple camera feeds...",
                "narrationUrl": "/narrations/analysis-123456.mp3"
            }
        }
