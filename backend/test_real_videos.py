import asyncio
import os
import logging
import json
from dotenv import load_dotenv
from utils.video_analyzer_enhanced import video_analyzer
from utils.llama_client import llama_client
from utils.groq_client import groq_client
from utils.db_connector import mongodb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_real_videos():
    """
    Test the video analysis pipeline with real videos in the videos folder
    """
    print("=== Testing Video Analysis Pipeline with Real Videos ===")
    
    # Connect to MongoDB
    try:
        await mongodb.connect_async()
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {str(e)}")
        print("Using in-memory storage for testing")
        
        # Create an in-memory database for testing
        class InMemoryDB:
            def __init__(self):
                self.collections = {}
            
            async def insert_one_async(self, collection, document):
                if collection not in self.collections:
                    self.collections[collection] = []
                self.collections[collection].append(document)
                return True
            
            async def find_one_async(self, collection, query):
                if collection not in self.collections:
                    return None
                for doc in self.collections[collection]:
                    match = True
                    for key, value in query.items():
                        if key not in doc or doc[key] != value:
                            match = False
                            break
                    if match:
                        return doc
                return None
            
            async def find_async(self, collection, query):
                class AsyncCursor:
                    def __init__(self, docs):
                        self.docs = docs
                    
                    async def to_list(self, length=None):
                        return self.docs
                
                if collection not in self.collections:
                    return AsyncCursor([])
                
                results = []
                for doc in self.collections[collection]:
                    match = True
                    for key, value in query.items():
                        if key not in doc or doc[key] != value:
                            match = False
                            break
                    if match:
                        results.append(doc)
                
                return AsyncCursor(results)
            
            async def update_one_async(self, collection, query, update):
                if collection not in self.collections:
                    return False
                
                for i, doc in enumerate(self.collections[collection]):
                    match = True
                    for key, value in query.items():
                        if key not in doc or doc[key] != value:
                            match = False
                            break
                    
                    if match:
                        # Handle $set operator
                        if "$set" in update:
                            for key, value in update["$set"].items():
                                self.collections[collection][i][key] = value
                        return True
                
                return False
        
        # Monkey patch the mongodb instance
        in_memory_db = InMemoryDB()
        mongodb.insert_one_async = in_memory_db.insert_one_async
        mongodb.find_one_async = in_memory_db.find_one_async
        mongodb.find_async = in_memory_db.find_async
        mongodb.update_one_async = in_memory_db.update_one_async
    
    # Find all videos in the videos folder
    videos_folder = "data/videos"
    video_files = []
    
    if os.path.exists(videos_folder):
        for file in os.listdir(videos_folder):
            if file.endswith(".mp4") or file.endswith(".MOV"):
                video_files.append(os.path.join(videos_folder, file))
    
    if not video_files:
        print("No video files found in the videos folder")
        return
    
    print(f"Found {len(video_files)} video files: {video_files}")
    
    # Create test suspect record
    suspect_id = "test_suspect_001"
    
    # Use the existing suspect image in the suspects folder
    sample_suspect_path = f"data/suspects/{suspect_id}.jpg"
    
    if os.path.exists(sample_suspect_path):
        print(f"Using existing suspect image: {sample_suspect_path}")
    else:
        print("Suspect image not found. Creating a placeholder image...")
        # Create a placeholder suspect image
        import numpy as np
        import cv2
        placeholder_img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.rectangle(placeholder_img, (100, 100), (200, 200), (255, 255, 255), -1)
        os.makedirs("data/suspects", exist_ok=True)
        cv2.imwrite(sample_suspect_path, placeholder_img)
    
    suspect_data = {
        "id": suspect_id,
        "imageUrl": f"/suspects/{suspect_id}.jpg",
        "name": "Test Suspect",
        "description": "Person of interest for testing"
    }
    
    # Store suspect in database
    await mongodb.insert_one_async("suspects", suspect_data)
    print(f"Created test suspect record: {suspect_id}")
    
    # Process each video
    video_records = []
    
    for i, video_path in enumerate(video_files):
        video_id = f"video_{i+1:03d}"
        video_name = os.path.basename(video_path)
        
        video_data = {
            "id": video_id,
            "name": f"CCTV Feed {i+1}",
            "location": f"Location {i+1}",
            "timestamp": "2025-05-04T08:00:00Z",
            "duration": 0,
            "fileUrl": f"/videos/{video_name}",
            "thumbnailUrl": f"/videos/{video_id}_thumb.jpg",
            "size": os.path.getsize(video_path),
            "processed": False
        }
        
        # Store video in database
        await mongodb.insert_one_async("videos", video_data)
        print(f"Created video record: {video_id}")
        
        # Process video
        print(f"Processing video {i+1}/{len(video_files)}: {video_path}")
        result = await video_analyzer.process_video(
            video_path,
            video_id,
            {
                "name": video_data["name"],
                "location": video_data["location"],
                "timestamp": video_data["timestamp"]
            }
        )
        print(f"Video processing result: {result}")
        
        # Analyze frames
        print(f"Analyzing frames for video {i+1}/{len(video_files)}")
        analysis_result = await video_analyzer.analyze_frames(video_id)
        print(f"Frame analysis result: {analysis_result}")
        
        video_records.append(video_data)
    
    if video_records:
        # Track suspect across all videos
        print("Tracking suspect across all videos...")
        tracking_results = await video_analyzer.track_suspect(
            suspect_data,
            video_records
        )
        print(f"Found {len(tracking_results)} suspect appearances")
        
        if tracking_results:
            # Generate timeline
            print("Generating timeline...")
            timeline = await video_analyzer.generate_timeline(tracking_results)
            print(f"Generated timeline with {len(timeline)} events")
            
            # Build knowledge graph
            print("Building knowledge graph...")
            graph = await video_analyzer.build_knowledge_graph(tracking_results)
            print(f"Built knowledge graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
            
            # Generate summary
            print("Generating summary...")
            summary = await video_analyzer.generate_summary(timeline)
            print(f"Summary: {summary[:200]}...")
        else:
            print("No suspect appearances found, skipping timeline and graph generation")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_real_videos())
