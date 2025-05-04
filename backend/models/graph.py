from pydantic import BaseModel
from typing import Optional, List, Literal

class GraphNode(BaseModel):
    """
    Model representing a node in the knowledge graph
    """
    id: str
    type: Literal["suspect", "location", "person", "object"]
    label: str
    imageUrl: Optional[str] = None
    details: Optional[str] = None
    timestamp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "suspect-123456",
                "type": "suspect",
                "label": "Unknown Subject",
                "imageUrl": "/suspects/suspect-123456.jpg",
                "details": "Male, approximately 30-40 years old, wearing dark jacket",
                "timestamp": "2025-05-04T08:15:00Z"
            }
        }

class GraphEdge(BaseModel):
    """
    Model representing an edge (relationship) in the knowledge graph
    """
    id: str
    source: str
    target: str
    label: str
    timestamp: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "edge-123456",
                "source": "suspect-123456",
                "target": "location-123456",
                "label": "visited",
                "timestamp": "2025-05-04T08:15:00Z"
            }
        }

class GraphData(BaseModel):
    """
    Model representing the complete knowledge graph
    """
    nodes: List[GraphNode]
    edges: List[GraphEdge]
