from bson import ObjectId
import json
from typing import Any

class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles MongoDB ObjectId serialization"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def serialize_mongodb_doc(doc: dict) -> dict:
    """
    Recursively convert MongoDB ObjectId to string in a document
    
    Args:
        doc: MongoDB document with potential ObjectId fields
        
    Returns:
        Document with ObjectId converted to strings
    """
    if doc is None:
        return None
        
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = serialize_mongodb_doc(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_mongodb_doc(item) if isinstance(item, dict) else 
                str(item) if isinstance(item, ObjectId) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
