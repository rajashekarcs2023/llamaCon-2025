from bson import ObjectId
import json
from fastapi.responses import JSONResponse

class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle MongoDB ObjectId"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def mongo_serializable(obj):
    """Convert MongoDB objects to serializable format"""
    if isinstance(obj, dict):
        return {k: mongo_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [mongo_serializable(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

def mongo_response(content):
    """Create a JSONResponse with MongoDB-safe serialization"""
    serializable_content = mongo_serializable(content)
    return JSONResponse(content=serializable_content)
