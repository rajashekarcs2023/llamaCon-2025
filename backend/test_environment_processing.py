import asyncio
import os
import json
from bson import ObjectId
from utils.video_analyzer_enhanced import video_analyzer

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

async def test_environment_processing():
    """Test the environment video processing functionality directly"""
    print("Testing environment video processing...")
    
    # Path to the environment video
    env_video_path = "data/environment/environment awareness.MOV"
    
    # Check if the file exists
    if not os.path.exists(env_video_path):
        print(f"Environment video not found at {env_video_path}")
        return
    
    print(f"Found environment video at {env_video_path}")
    
    # Process the environment video
    try:
        print("Processing environment video...")
        env_context = await video_analyzer.process_environment_video(env_video_path, "env-test-id")
        
        # Print the environment context
        print("\nEnvironment Context:")
        print(json.dumps(env_context, indent=2, cls=JSONEncoder))
        
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"Error processing environment video: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_environment_processing())
