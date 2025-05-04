import asyncio
import os
import logging
import json
import base64
from dotenv import load_dotenv
from utils.video_analyzer_enhanced import VideoAnalyzer
from utils.llama_client import llama_client
from utils.groq_client import groq_client
from utils.db_connector import mongodb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

async def test_real_apis():
    """
    Test the video analysis pipeline with real APIs
    """
    print("=== Testing Video Analysis Pipeline with Real APIs ===")
    
    # Check if API keys are set
    llama_api_key = os.getenv("LLAMA_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not llama_api_key:
        print("LLAMA_API_KEY not set in .env file")
        return
    
    if not groq_api_key:
        print("GROQ_API_KEY not set in .env file")
        return
    
    print("API keys found in .env file")
    
    # Use in-memory database for testing
    print("Using in-memory storage for testing")
    
    # Monkey patch the mongodb instance
    in_memory_db = InMemoryDB()
    mongodb.insert_one_async = in_memory_db.insert_one_async
    mongodb.find_one_async = in_memory_db.find_one_async
    mongodb.find_async = in_memory_db.find_async
    mongodb.update_one_async = in_memory_db.update_one_async
    
    # Create a new VideoAnalyzer instance that doesn't use mocks
    video_analyzer = VideoAnalyzer(use_groq_for_frames=True)
    
    # Find sample video
    sample_video_path = None
    
    # Check for video in sample folder
    sample_folder = "sample"
    if os.path.exists(sample_folder):
        videos = [f for f in os.listdir(sample_folder) if f.endswith('.MOV') or f.endswith('.mp4')]
        if videos:
            sample_video_path = os.path.join(sample_folder, videos[0])
            print(f"Using video from sample folder: {sample_video_path}")
    
    # If not found, check videos folder
    if not sample_video_path:
        videos_folder = "data/videos"
        if os.path.exists(videos_folder):
            videos = [f for f in os.listdir(videos_folder) if f.endswith('.mp4') or f.endswith('.MOV')]
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
        print("Suspect image not found. Please add a suspect image to data/suspects/test_suspect_001.jpg")
        return
    
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
    
    # Test direct API calls
    print("\nTesting direct API calls...")
    
    # Test LLaMA API
    print("Testing LLaMA API with suspect image...")
    try:
        suspect_features = await llama_client.extract_person_features(sample_suspect_path)
        print(f"LLaMA API response for suspect image: {json.dumps(suspect_features, indent=2)}")
    except Exception as e:
        print(f"Error calling LLaMA API: {str(e)}")
    
    # Test Groq API with a frame
    frames_dir = f"data/videos/frames/{video_id}"
    if os.path.exists(frames_dir):
        frames = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
        if frames:
            test_frame = os.path.join(frames_dir, frames[0])
            print(f"Testing Groq API with frame: {test_frame}")
            try:
                frame_analysis = groq_client.process_video_frame(test_frame)
                print(f"Groq API response for frame: {json.dumps(frame_analysis, indent=2)}")
            except Exception as e:
                print(f"Error calling Groq API: {str(e)}")
    
    # Analyze frames
    print("\nAnalyzing frames...")
    analysis_result = await video_analyzer.analyze_frames(video_id)
    print(f"Frame analysis result: {analysis_result}")
    
    # Track suspect
    print("\nTracking suspect...")
    tracking_results = await video_analyzer.track_suspect(
        suspect_data,
        [video_data]
    )
    # The track_suspect method returns a list directly, not a dictionary
    suspect_appearances = tracking_results
    print(f"Found {len(suspect_appearances)} suspect appearances")
    
    if suspect_appearances:
        print("\nSuspect appearances:")
        for i, result in enumerate(suspect_appearances[:5]):  # Show first 5 for brevity
            print(f"- Video: {result['videoId']}, Frame: {result['frameId']}, Confidence: {result['confidence']}")
            print(f"  Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            
            # Handle different result formats
            if 'wholeFrameMatch' in result and result['wholeFrameMatch']:
                print(f"  Whole Frame Match: Yes")
                print(f"  Position: {result.get('position', 'Not specified')}")
            else:
                print(f"  Position: {result.get('position', 'Not specified')}")
                print(f"  Description: {result.get('description', 'No description available')}")
                print(f"  Carrying: {', '.join(result.get('carrying', []))}")
            
            if i < len(suspect_appearances) - 1 and i < 4:
                print()
        
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
        print(f"Summary: {summary}")
    else:
        print("No suspect appearances found, skipping timeline and graph generation")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_real_apis())
