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

async def test_sample_video():
    """
    Test the video analysis pipeline with the sample video
    """
    print("=== Testing Video Analysis Pipeline with Sample Video ===")
    
    # Use in-memory database for testing
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
    
    # Create mock implementations for LLaMA and Groq clients
    # This is to avoid API authentication errors during testing
    
    # Mock LLaMA client
    class MockLlamaClient:
        def extract_person_features(self, image_path):
            print(f"Mock extracting person features from {image_path}")
            return {
                "face": {"visible": True, "features": "Oval face with brown eyes"},
                "body": {"build": "Medium", "height": "Medium", "posture": "Upright"},
                "clothing": {"upper": "Dark jacket", "lower": "Blue jeans", "colors": ["black", "blue"]},
                "hair": {"style": "Short", "color": "Brown"},
                "distinctive": ["Glasses", "Watch on left wrist"]
            }
        
        def analyze_frame_for_persons(self, frame_url):
            print(f"Mock analyzing frame: {frame_url}")
            return {
                "persons": [
                    {
                        "id": "person_1",
                        "bbox": [100, 100, 300, 400],
                        "description": "Male, approximately 30-40 years old, wearing dark jacket",
                        "position": "Center of frame",
                        "carrying": ["backpack"],
                        "features": {
                            "face": {"visible": True, "features": "Oval face with brown eyes"},
                            "body": {"build": "Medium", "height": "Medium", "posture": "Upright"},
                            "clothing": {"upper": "Dark jacket", "lower": "Blue jeans", "colors": ["black", "blue"]},
                            "hair": {"style": "Short", "color": "Brown"},
                            "distinctive": ["Glasses", "Watch on left wrist"]
                        }
                    }
                ]
            }
    
    # Mock Groq client
    class MockGroqClient:
        def process_video_frame(self, frame_path, model=None, use_url=False):
            print(f"Mock processing video frame: {frame_path}")
            return {
                "persons": [
                    {
                        "id": "person_1",
                        "bbox": [100, 100, 300, 400],
                        "description": "Male, approximately 30-40 years old, wearing dark jacket",
                        "position": "Center of frame",
                        "carrying": ["backpack"]
                    }
                ]
            }
        
        def compare_images(self, image1_path, image2_path, prompt, model=None, use_urls=False):
            print(f"Mock comparing images: {image1_path} and {image2_path}")
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"match": true, "confidence": 85, "reasoning": "Similar facial features and clothing"}'
                        }
                    }
                ]
            }
    
    # Replace the real clients with mock implementations
    llama_client.extract_person_features = MockLlamaClient().extract_person_features
    llama_client.analyze_frame_for_persons = MockLlamaClient().analyze_frame_for_persons
    groq_client.process_video_frame = MockGroqClient().process_video_frame
    groq_client.compare_images = MockGroqClient().compare_images
    
    # Check if we have sample data
    sample_video_path = "data/sample/IMG_7654.MOV"
    
    if not os.path.exists(sample_video_path):
        print(f"Sample video not found at {sample_video_path}")
        # Check if we have videos in the videos folder
        videos_folder = "data/videos"
        if os.path.exists(videos_folder):
            videos = [f for f in os.listdir(videos_folder) if f.endswith('.mp4')]
            if videos:
                sample_video_path = os.path.join(videos_folder, videos[0])
                print(f"Using video from videos folder: {sample_video_path}")
            else:
                print("No videos found in the videos folder either.")
                return
        else:
            print("Videos folder not found.")
            return
    
    # Create test video record
    video_id = "test_video_001"
    video_data = {
        "id": video_id,
        "name": "Test CCTV Feed",
        "location": "Main Entrance",
        "timestamp": "2025-05-04T08:00:00Z",
        "duration": 0,
        "fileUrl": f"/videos/{video_id}.mp4",
        "thumbnailUrl": f"/videos/{video_id}_thumb.jpg",
        "size": os.path.getsize(sample_video_path),
        "processed": False
    }
    
    # Save sample video to data directory
    os.makedirs("data/videos", exist_ok=True)
    if not os.path.exists(f"data/videos/{video_id}.mp4"):
        import shutil
        shutil.copy(sample_video_path, f"data/videos/{video_id}.mp4")
    
    # Store video in database
    await mongodb.insert_one_async("videos", video_data)
    print(f"Created test video record: {video_id}")
    
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
    
    # Process video
    print("Processing video...")
    result = await video_analyzer.process_video(
        f"data/videos/{video_id}.mp4",
        video_id,
        {
            "name": video_data["name"],
            "location": video_data["location"],
            "timestamp": video_data["timestamp"]
        }
    )
    print(f"Video processing result: {result}")
    
    # Analyze frames
    print("Analyzing frames...")
    analysis_result = await video_analyzer.analyze_frames(video_id)
    print(f"Frame analysis result: {analysis_result}")
    
    # Track suspect
    print("Tracking suspect...")
    tracking_results = await video_analyzer.track_suspect(
        suspect_data,
        [video_data]
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
    asyncio.run(test_sample_video())
