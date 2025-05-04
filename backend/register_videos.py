import os
import asyncio
import uuid
from datetime import datetime
from utils.db_connector import MongoDBConnector

# Initialize MongoDB connector
mongodb = MongoDBConnector()

async def register_videos():
    """Register all videos in the data/videos directory to MongoDB"""
    videos_dir = "data/videos"
    
    # Check if videos directory exists
    if not os.path.exists(videos_dir):
        print(f"Videos directory {videos_dir} not found")
        return
    
    # Get all video files
    video_files = [f for f in os.listdir(videos_dir) if f.endswith(".mp4")]
    
    if not video_files:
        print("No video files found")
        return
    
    print(f"Found {len(video_files)} video files")
    
    # Register each video
    for video_file in video_files:
        # Extract video ID from filename
        video_id = video_file.replace("video-", "").replace(".mp4", "")
        
        # Check if video already exists in database
        existing_video = await mongodb.find_one_async("videos", {"id": video_id})
        
        if existing_video:
            print(f"Video {video_id} already registered")
            continue
        
        # Create video document
        video_doc = {
            "id": video_id,
            "name": f"Video {video_id[:8]}",
            "location": "Unknown",
            "timestamp": datetime.now().isoformat(),
            "duration": 0,
            "processed": False,
            "path": f"data/videos/{video_file}",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        # Insert video document
        try:
            await mongodb.insert_one_async("videos", video_doc)
            print(f"Registered video {video_id}")
        except Exception as e:
            print(f"Error registering video {video_id}: {str(e)}")

    # Register environment video
    env_video_path = "data/environment/environment awareness.MOV"
    if os.path.exists(env_video_path):
        env_video_id = f"env-{uuid.uuid4()}"
        
        # Create environment video document
        env_video_doc = {
            "id": env_video_id,
            "name": "Environment Awareness",
            "location": "Environment",
            "timestamp": datetime.now().isoformat(),
            "duration": 0,
            "processed": False,
            "path": env_video_path,
            "isEnvironment": True,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        # Insert environment video document
        try:
            await mongodb.insert_one_async("videos", env_video_doc)
            print(f"Registered environment video {env_video_id}")
        except Exception as e:
            print(f"Error registering environment video: {str(e)}")
    else:
        print(f"Environment video not found at {env_video_path}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(register_videos())
