import asyncio
import os
import json
import time
from bson import ObjectId
from utils.video_analyzer_enhanced import video_analyzer
from utils.db_connector import MongoDBConnector

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)

# Initialize MongoDB connector
mongodb = MongoDBConnector()

async def test_full_analysis():
    """Test the full analysis workflow with environment context"""
    print("Testing full analysis workflow with environment context...")
    
    # Step 1: Get a video from the database
    # Since find_async doesn't exist, we'll use a direct approach
    cursor = mongodb.db["videos"].find({"isEnvironment": {"$ne": True}})
    videos = []
    async for doc in cursor:
        videos.append(doc)
        if len(videos) >= 1:
            break
    
    if not videos:
        print("No regular videos found in the database")
        return
    
    video = videos[0]
    print(f"Using video: {video['id']}")
    
    # Get environment video
    cursor = mongodb.db["videos"].find({"isEnvironment": True})
    env_videos = []
    async for doc in cursor:
        env_videos.append(doc)
        if len(env_videos) >= 1:
            break
    
    if not env_videos:
        print("No environment videos found in the database")
        return
    
    env_video = env_videos[0]
    print(f"Using environment video: {env_video['id']}")
    
    # Step 2: Process the environment video
    print("\nProcessing environment video...")
    env_context = await video_analyzer.process_environment_video(
        env_video.get("path", f"data/videos/{env_video['id']}.mp4"), 
        env_video['id']
    )
    
    print(f"Environment context created with ID: {env_context.get('id', 'unknown')}")
    
    # Step 3: Create a mock suspect
    suspect_id = f"suspect-test-{int(time.time())}"
    suspect = {
        "id": suspect_id,
        "name": "Test Suspect",
        "description": "Person of interest for testing",
        "imagePath": "data/suspects/test_suspect.jpg",
        "features": {
            "face": {"visible": True, "features": "Average features"},
            "body": {"build": "Medium", "height": "Average", "posture": "Upright"},
            "clothing": {"upper": "Dark jacket", "lower": "Jeans", "colors": ["black", "blue"]},
            "hair": {"style": "Short", "color": "Dark"},
            "distinctive": ["Carrying a backpack"]
        },
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Insert suspect into database
    try:
        await mongodb.insert_one_async("suspects", suspect)
        print(f"Created test suspect with ID: {suspect_id}")
    except Exception as e:
        print(f"Error creating suspect: {str(e)}")
        # Continue even if suspect already exists
    
    # Step 4: Create an analysis
    analysis_id = f"analysis-test-{int(time.time())}"
    analysis = {
        "id": analysis_id,
        "suspectId": suspect_id,
        "videoIds": [video['id']],
        "status": "processing",
        "includeEnvironment": True,
        "environmentContextId": env_context.get('id'),
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Insert analysis into database
    try:
        await mongodb.insert_one_async("analyses", analysis)
        print(f"Created test analysis with ID: {analysis_id}")
    except Exception as e:
        print(f"Error creating analysis: {str(e)}")
        return
    
    # Step 5: Process the video
    print("\nProcessing video...")
    try:
        video_path = video.get("path", f"data/videos/{video['id']}.mp4")
        
        # Process video to extract frames
        await video_analyzer.process_video(
            video_path,
            video['id'],
            {
                "name": video.get("name", ""),
                "location": video.get("location", ""),
                "timestamp": video.get("timestamp", "")
            }
        )
        
        print(f"Video processed: {video['id']}")
        
        # Analyze frames to detect objects
        await video_analyzer.analyze_frames(video['id'])
        print("Frames analyzed for objects")
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return
    
    # Step 6: Track suspect
    print("\nTracking suspect...")
    try:
        tracking_results = await video_analyzer.track_suspect(
            suspect,
            [video],
            confidence_threshold=30.0
        )
        
        print(f"Tracked suspect with {len(tracking_results)} results")
        
        # Store tracking results
        for result in tracking_results:
            result["analysisId"] = analysis_id
            await mongodb.insert_one_async("tracking_results", result)
        
        # Update analysis with tracking results
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "trackingResults": len(tracking_results),
            "status": "tracked"
        })
    except Exception as e:
        print(f"Error tracking suspect: {str(e)}")
        return
    
    # Step 7: Generate timeline
    print("\nGenerating timeline...")
    try:
        timeline = await video_analyzer.generate_timeline(tracking_results)
        
        # Store timeline
        timeline["analysisId"] = analysis_id
        await mongodb.insert_one_async("timelines", timeline)
        
        print(f"Generated timeline with {len(timeline.get('events', []))} events")
        
        # Update analysis with timeline
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "timelineId": timeline.get("id", ""),
            "status": "timeline_generated"
        })
    except Exception as e:
        print(f"Error generating timeline: {str(e)}")
        return
    
    # Step 8: Generate knowledge graph
    print("\nGenerating knowledge graph...")
    try:
        graph = await video_analyzer.build_knowledge_graph(tracking_results)
        
        # Store graph
        graph["analysisId"] = analysis_id
        await mongodb.insert_one_async("graphs", graph)
        
        print(f"Generated knowledge graph with {len(graph.get('nodes', []))} nodes and {len(graph.get('edges', []))} edges")
        
        # Update analysis with graph
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "graphId": graph.get("id", ""),
            "status": "graph_generated"
        })
    except Exception as e:
        print(f"Error generating knowledge graph: {str(e)}")
        return
    
    # Step 9: Generate summary with environment context
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
        
        # Update analysis with summary
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "summary": summary,
            "status": "completed"
        })
        
        print("\nGenerated summary:")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        print("\nFull analysis completed successfully!")
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return

if __name__ == "__main__":
    asyncio.run(test_full_analysis())
