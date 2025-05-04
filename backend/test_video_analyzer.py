import asyncio
import os
import logging
import json
from dotenv import load_dotenv
from utils.video_analyzer import video_analyzer
from utils.llama_client import llama_client
from utils.groq_client import groq_client
from utils.db_connector import mongodb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_video_analysis():
    """
    Test the video analysis pipeline with a sample video and suspect image
    """
    print("=== Testing Video Analysis Pipeline ===")
    
    # Connect to MongoDB
    await mongodb.connect_async()
    print("Connected to MongoDB")
    
    # Test LLaMA API connection
    try:
        response = llama_client.chat_completion([
            {"role": "user", "content": "Hello, are you working?"}
        ])
        print(f"LLaMA API test: {response['choices'][0]['message']['content'][:50]}...")
    except Exception as e:
        print(f"Error testing LLaMA API: {str(e)}")
    
    # Test Groq API connection
    try:
        response = groq_client.chat_completion([
            {"role": "user", "content": "Hello, are you working?"}
        ])
        print(f"Groq API test: {response['choices'][0]['message']['content'][:50]}...")
    except Exception as e:
        print(f"Error testing Groq API: {str(e)}")
    
    # Check if we have sample data
    sample_video_path = "data/sample/sample_video.mp4"
    sample_suspect_path = "data/sample/suspect.jpg"
    
    if not os.path.exists(sample_video_path) or not os.path.exists(sample_suspect_path):
        print("Sample data not found. Please add sample video and suspect image to data/sample/ directory.")
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
    suspect_data = {
        "id": suspect_id,
        "imageUrl": f"/suspects/{suspect_id}.jpg",
        "name": "Test Suspect",
        "description": "Person of interest for testing"
    }
    
    # Save sample suspect image to data directory
    os.makedirs("data/suspects", exist_ok=True)
    if not os.path.exists(f"data/suspects/{suspect_id}.jpg"):
        import shutil
        shutil.copy(sample_suspect_path, f"data/suspects/{suspect_id}.jpg")
    
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
        print(f"Summary: {summary[:100]}...")
    else:
        print("No suspect appearances found, skipping timeline and graph generation")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_video_analysis())
