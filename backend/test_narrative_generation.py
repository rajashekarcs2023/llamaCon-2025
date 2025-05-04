import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.video_analyzer_enhanced import VideoAnalyzer
from utils.groq_client import groq_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_narrative_generation():
    """
    Test the narrative generation feature with multiple videos
    """
    print("=== Testing Narrative Generation with Multiple Videos ===")
    
    # Check if API keys are set
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("GROQ_API_KEY not set in .env file")
        return
    
    print("API keys found in .env file")
    
    # Create test data directory
    os.makedirs("data/test_narrative", exist_ok=True)
    
    # Initialize the video analyzer
    video_analyzer = VideoAnalyzer(use_groq_for_frames=True)
    
    # Create test suspect
    suspect_data = {
        "id": "test_suspect_001",
        "name": "John Doe",
        "imagePath": "data/suspects/test_suspect_001.jpg"
    }
    
    # Create test videos with different timestamps and locations
    base_time = datetime.now()
    videos_data = [
        {
            "id": "video_001",
            "name": "Main Entrance Camera",
            "location": "Main Entrance",
            "timestamp": (base_time - timedelta(minutes=30)).isoformat(),
            "path": "data/videos/test_video_001.mp4"
        },
        {
            "id": "video_002",
            "name": "Lobby Camera",
            "location": "Lobby",
            "timestamp": (base_time - timedelta(minutes=25)).isoformat(),
            "path": "data/videos/test_video_001.mp4"  # Reusing the same video for testing
        },
        {
            "id": "video_003",
            "name": "Hallway Camera",
            "location": "Hallway",
            "timestamp": (base_time - timedelta(minutes=20)).isoformat(),
            "path": "data/videos/test_video_001.mp4"  # Reusing the same video for testing
        },
        {
            "id": "video_004",
            "name": "Exit Camera",
            "location": "Emergency Exit",
            "timestamp": (base_time - timedelta(minutes=15)).isoformat(),
            "path": "data/videos/test_video_001.mp4"  # Reusing the same video for testing
        }
    ]
    
    # Create simulated tracking results
    tracking_results = []
    
    # Generate tracking results for each video
    for video_idx, video in enumerate(videos_data):
        video_id = video["id"]
        location = video["location"]
        base_timestamp = datetime.fromisoformat(video["timestamp"].replace('Z', '+00:00'))
        
        # Create 5 tracking results per video with increasing timestamps
        for i in range(5):
            timestamp = (base_timestamp + timedelta(minutes=i)).isoformat()
            
            # Create a tracking result
            result = {
                "id": f"track-{video_id}-{i}",
                "suspectId": suspect_data["id"],
                "videoId": video_id,
                "frameId": f"frame_{i:04d}",
                "timestamp": timestamp,
                "location": location,
                "confidence": 85 + (i * 2),
                "thumbnailUrl": f"/frames/{video_id}/frame_{i:04d}.jpg",
                "description": f"Male, approximately 30-40 years old, wearing dark jacket and jeans",
                "position": f"{'Entering' if i == 0 else 'Walking through' if i < 4 else 'Exiting'} the {location.lower()}",
                "reasoning": "The suspect matches the description and appears to be the same person based on clothing and physical characteristics",
                "carrying": ["backpack"] if video_idx % 2 == 0 else ["phone", "coffee cup"]
            }
            
            tracking_results.append(result)
    
    # Sort tracking results by timestamp
    tracking_results.sort(key=lambda x: x["timestamp"])
    
    print(f"Created {len(tracking_results)} simulated tracking results across {len(videos_data)} videos")
    
    # Generate timeline with narrative
    print("\nGenerating timeline with narrative...")
    timeline = await video_analyzer.generate_timeline(tracking_results)
    
    # Print timeline information
    print(f"\nTimeline generated with {len(timeline['events'])} events")
    print(f"Duration: {timeline['duration']} minutes")
    print(f"Locations: {', '.join(timeline['locations'])}")
    print(f"First seen: {timeline['firstSeen']}")
    print(f"Last seen: {timeline['lastSeen']}")
    
    # Print activity summary
    print(f"\nActivity Summary:")
    print(timeline['activitySummary'])
    
    # Print narrative
    print(f"\nNarrative:")
    print(timeline['narrative'])
    
    # Print visual timeline (first 3 entries)
    print(f"\nVisual Timeline (first 3 entries):")
    for entry in timeline['visualTimeline'][:3]:
        print(f"- {entry['time']} at {entry['location']}: {entry['activity']}")
    
    # Save the timeline to a file
    with open("data/test_narrative/timeline.json", "w") as f:
        json.dump(timeline, f, indent=2)
    
    print(f"\nTimeline saved to data/test_narrative/timeline.json")
    print("=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_narrative_generation())
