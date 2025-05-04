from fastapi.responses import JSONResponse
from bson import ObjectId
import json

class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle MongoDB ObjectId"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

class MongoJSONResponse(JSONResponse):
    """Custom JSONResponse that uses MongoJSONEncoder"""
    def render(self, content):
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=MongoJSONEncoder,
        ).encode("utf-8")
