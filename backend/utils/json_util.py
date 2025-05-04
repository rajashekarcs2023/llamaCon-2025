import json
from bson import ObjectId
from typing import Any, Dict, List, Union

class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles MongoDB ObjectId serialization"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def serialize_mongo(obj: Any) -> Any:
    """
    Recursively serialize MongoDB objects (like ObjectId) to JSON-compatible formats
    
    Args:
        obj: The object to serialize
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {k: serialize_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj
