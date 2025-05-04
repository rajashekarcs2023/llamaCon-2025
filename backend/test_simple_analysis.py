import asyncio
import os
import json
import time
from bson import ObjectId
from utils.video_analyzer_enhanced import video_analyzer

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

async def test_simple_analysis():
    """Test a simple analysis with environment context"""
    print("Testing simple analysis with environment context...")
    
    # Step 1: Define paths to test videos
    env_video_path = "data/environment/environment awareness.MOV"
    video_path = "data/videos/video-15efebb0-fce7-4377-99fa-d4f7983f4e29.mp4"
    
    # Check if files exist
    if not os.path.exists(env_video_path):
        print(f"Environment video not found at {env_video_path}")
        return
    
    if not os.path.exists(video_path):
        print(f"Video not found at {video_path}")
        return
    
    print(f"Found environment video: {env_video_path}")
    print(f"Found video: {video_path}")
    
    # Step 2: Process the environment video
    print("\nProcessing environment video...")
    env_context = await video_analyzer.process_environment_video(
        env_video_path, 
        "env-test-id"
    )
    
    print(f"Environment context created with {len(env_context.get('locations', []))} locations")
    
    # Step 3: Create a mock suspect
    suspect = {
        "id": "suspect-test-id",
        "name": "Test Suspect",
        "description": "Person of interest for testing",
        "features": {
            "face": {"visible": True, "features": "Average features"},
            "body": {"build": "Medium", "height": "Average", "posture": "Upright"},
            "clothing": {"upper": "Dark jacket", "lower": "Jeans", "colors": ["black", "blue"]},
            "hair": {"style": "Short", "color": "Dark"},
            "distinctive": ["Carrying a backpack"]
        }
    }
    
    # Step 4: Process the video
    print("\nProcessing video...")
    try:
        # Process video to extract frames - note that process_video is synchronous
        video_result = video_analyzer.process_video(
            video_path,
            "video-test-id",
            {
                "name": "Test Video",
                "location": "Test Location",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        )
        
        print("Video processed successfully")
        
        # Analyze frames to detect objects - note that analyze_frames is synchronous
        analysis_result = video_analyzer.analyze_frames("video-test-id")
        print(f"Frames analyzed for objects: {analysis_result.get('frames_analyzed', 0)} frames processed")
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return
    
    # Step 5: Track suspect
    print("\nTracking suspect...")
    try:
        video_obj = {
            "id": "video-test-id",
            "name": "Test Video",
            "location": "Test Location",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        tracking_results = await video_analyzer.track_suspect(
            suspect,
            [video_obj],
            confidence_threshold=30.0
        )
        
        print(f"Tracked suspect with {len(tracking_results)} results")
        
        if len(tracking_results) == 0:
            print("No tracking results found, using mock data for testing")
            # Create mock tracking results for testing
            tracking_results = [
                {
                    "id": "track-1",
                    "suspectId": "suspect-test-id",
                    "videoId": "video-test-id",
                    "frameId": "frame_0001",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "confidence": 85.5,
                    "location": "Main Entrance",
                    "position": "Standing near the door",
                    "activity": "Entering the building",
                    "description": "Subject is entering the building through the main entrance"
                },
                {
                    "id": "track-2",
                    "suspectId": "suspect-test-id",
                    "videoId": "video-test-id",
                    "frameId": "frame_0010",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 60)),
                    "confidence": 92.1,
                    "location": "Lobby",
                    "position": "Walking across the lobby",
                    "activity": "Walking",
                    "description": "Subject is walking across the lobby toward the corridor"
                },
                {
                    "id": "track-3",
                    "suspectId": "suspect-test-id",
                    "videoId": "video-test-id",
                    "frameId": "frame_0020",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 120)),
                    "confidence": 88.7,
                    "location": "Corridor",
                    "position": "Standing in the corridor",
                    "activity": "Talking",
                    "description": "Subject is standing in the corridor, appears to be talking to someone"
                }
            ]
    except Exception as e:
        print(f"Error tracking suspect: {str(e)}")
        return
    
    # Step 6: Generate timeline
    print("\nGenerating timeline...")
    try:
        timeline = await video_analyzer.generate_timeline(tracking_results)
        
        print(f"Generated timeline with {len(timeline.get('events', []))} events")
        print("Timeline narrative:")
        print(timeline.get('narrative', 'No narrative available')[:300] + "...")
    except Exception as e:
        print(f"Error generating timeline: {str(e)}")
        return
    
    # Step 7: Generate knowledge graph
    print("\nGenerating knowledge graph...")
    try:
        graph = await video_analyzer.build_knowledge_graph(tracking_results)
        
        print(f"Generated knowledge graph with {len(graph.get('nodes', []))} nodes and {len(graph.get('edges', []))} edges")
    except Exception as e:
        print(f"Error generating knowledge graph: {str(e)}")
        return
    
    # Step 8: Generate summary with environment context
    print("\nGenerating summary with environment context...")
    try:
        # Get timeline events
        timeline_events = timeline.get("events", [])
        
        # Generate summary
        summary = await video_analyzer.generate_summary(
            timeline_events,
            graph,
            env_context
        )
        
        print("\nGenerated summary:")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        print("\nFull analysis completed successfully!")
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return

if __name__ == "__main__":
    asyncio.run(test_simple_analysis())
