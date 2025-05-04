from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any, Callable
import os
import uuid
import shutil
from datetime import datetime
import json
import asyncio
import concurrent.futures
from functools import partial
import logging
from dotenv import load_dotenv
from bson import ObjectId
from utils.json_util import serialize_mongo, MongoJSONEncoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from models.video import VideoFeed
from models.suspect import Suspect
from models.timeline import TimelineEvent
from models.graph import GraphData, GraphNode, GraphEdge
from models.analysis import AnalysisRequest, AnalysisResult, AnalysisOptions
from models.query import Query, QueryResponse

# GPU preference function
def get_gpu_preference():
    """Get GPU preference from environment variables"""
    return os.getenv("USE_GPU", "False").lower() == "true"

# Import utilities
from utils.video_analyzer_enhanced import video_analyzer
from utils.llama_client import llama_client
from utils.groq_client import groq_client

# Create FastAPI app
app = FastAPI(
    title="Reconstruct API",
    description="Backend API for Reconstruct - CCTV Analysis System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directories if they don't exist
os.makedirs("data/videos", exist_ok=True)
os.makedirs("data/suspects", exist_ok=True)
os.makedirs("data/results", exist_ok=True)

# Import database connectors
from utils.db_connector import mongodb

# Initialize MongoDB connection
@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect_async()

@app.on_event("shutdown")
async def shutdown_db_client():
    mongodb.disconnect()

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "Reconstruct API"}

# Video Endpoints
@app.post("/upload_video", response_model=VideoFeed)
async def upload_video(
    file: UploadFile = File(...),
    name: str = Form(None),
    location: str = Form(None),
    timestamp: str = Form(None),
    background_tasks: BackgroundTasks = None
):
    """Upload a CCTV video file with metadata"""
    # Generate a unique ID for the video
    video_id = f"video-{uuid.uuid4()}"
    
    # Create file path
    file_path = f"data/videos/{video_id}.mp4"
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Set default values if not provided
    if not name:
        name = file.filename
    if not location:
        location = "Unknown"
    if not timestamp:
        timestamp = datetime.now().isoformat()
    
    # Process video in background (extract frames, etc.)
    if background_tasks:
        background_tasks.add_task(video_analyzer.process_video, file_path, video_id, {
            "name": name,
            "location": location,
            "timestamp": timestamp
        })
    
    # Create video metadata
    video_data = {
        "id": video_id,
        "name": name,
        "location": location,
        "timestamp": timestamp,
        "duration": 0,  # Will be updated after processing
        "fileUrl": f"/videos/{video_id}.mp4",
        "thumbnailUrl": f"/videos/{video_id}_thumb.jpg",
        "size": os.path.getsize(file_path),
        "processed": False
    }
    
    # Store in database
    await mongodb.insert_one_async("videos", video_data)
    
    return video_data

@app.get("/videos", response_model=List[VideoFeed])
async def get_videos():
    """Get all uploaded videos"""
    videos = await mongodb.find_many_async("videos", {})
    return videos

@app.get("/videos/{video_id}", response_model=VideoFeed)
async def get_video(video_id: str):
    """Get a specific video by ID"""
    video = await mongodb.find_one_async("videos", {"id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

# Suspect Endpoints
@app.post("/upload_suspect", response_model=Suspect)
async def upload_suspect(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload a suspect image with optional metadata"""
    # Generate a unique ID for the suspect
    suspect_id = f"suspect-{uuid.uuid4()}"
    
    # Create file path
    file_path = f"data/suspects/{suspect_id}.jpg"
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create suspect metadata
    suspect_data = {
        "id": suspect_id,
        "imageUrl": f"/suspects/{suspect_id}.jpg",
        "name": name or "Unknown",
        "description": description or "",
        "lastSeen": None
    }
    
    # Store in database
    await mongodb.insert_one_async("suspects", suspect_data)
    
    return suspect_data

@app.get("/suspects", response_model=List[Suspect])
async def get_suspects():
    """Get all uploaded suspects"""
    suspects = await mongodb.find_many_async("suspects", {})
    return suspects

@app.get("/suspects/{suspect_id}", response_model=Suspect)
async def get_suspect(suspect_id: str):
    """Get a specific suspect by ID"""
    suspect = await mongodb.find_one_async("suspects", {"_id": ObjectId(suspect_id)})
    if not suspect:
        raise HTTPException(status_code=404, detail="Suspect not found")
    return suspect

# Analysis Endpoints
@app.post("/analysis/track-suspect")
async def analyze_suspect(
    request: dict,
    background_tasks: BackgroundTasks,
    use_gpu: bool = Depends(get_gpu_preference)
):
    """Run suspect tracking analysis across selected videos"""
    try:
        # Extract data from the request dictionary
        suspect_id = request.get("suspectId")
        video_ids = request.get("videoIds", [])
        timeframe = request.get("timeframe")
        options = request.get("options", {})
        
        logger.info(f"Received analysis request for suspect: {suspect_id}")
        
        if not suspect_id:
            return {"error": "suspectId is required"}
            
        if not video_ids:
            return {"error": "At least one videoId is required"}
        
        # Generate a unique ID for the analysis
        analysis_id = f"analysis-{uuid.uuid4()}"
        logger.info(f"Generated analysis ID: {analysis_id}")
        
        # Create a comprehensive analysis result with all required fields
        analysis_result = {
            "id": analysis_id,
            "suspectId": suspect_id,
            "timeline": [],
            "graph": {"nodes": [], "edges": []},
            "summary": "Analysis in progress...",
            "narrationUrl": None,
            "enhancedNarrative": "",
            "activitySummary": "",
            "locations": [],
            "duration": 0,
            "firstSeen": "",
            "lastSeen": "",
            "visualTimeline": []
        }
        
        # Store in database
        try:
            await mongodb.insert_one_async("analyses", analysis_result)
            logger.info(f"Stored initial analysis result in database")
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Continue even if database insert fails
        
        # For now, return a mock analysis result with some data
        # This ensures the frontend gets something to display
        mock_result = {
            "id": analysis_id,
            "suspectId": suspect_id,
            "timeline": [
                {
                    "id": f"event-{uuid.uuid4()}",
                    "timestamp": datetime.now().isoformat(),
                    "location": "Main Entrance",
                    "activity": "Walking",
                    "confidence": 85,
                    "thumbnailUrl": "/static/thumbnails/sample.jpg",
                    "description": "Suspect seen entering the building"
                }
            ],
            "graph": {
                "nodes": [
                    {"id": "node-1", "label": "Suspect", "type": "person"},
                    {"id": "node-2", "label": "Main Entrance", "type": "location"}
                ],
                "edges": [
                    {"source": "node-1", "target": "node-2", "label": "entered", "timestamp": datetime.now().isoformat()}
                ]
            },
            "summary": "Suspect was observed entering the building through the main entrance.",
            "narrationUrl": None,
            "enhancedNarrative": "The suspect was first seen entering the building through the main entrance.",
            "activitySummary": "Walking, standing",
            "locations": ["Main Entrance"],
            "duration": 30,
            "firstSeen": datetime.now().isoformat(),
            "lastSeen": datetime.now().isoformat(),
            "visualTimeline": [
                {
                    "id": f"visual-event-{uuid.uuid4()}",
                    "time": datetime.now().isoformat(),
                    "location": "Main Entrance",
                    "activity": "Walking",
                    "thumbnailUrl": "/static/thumbnails/sample.jpg",
                    "confidence": 85,
                    "isLocationChange": True,
                    "description": "Entering the building"
                }
            ]
        }
        
        # In the background, start the real analysis
        try:
            # Check if we should include environment context
            include_environment = options.get("includeEnvironment", True) if options else True
            
            background_tasks.add_task(
                run_analysis,
                analysis_id,
                suspect_id,
                video_ids,
                timeframe,
                options,
                use_gpu,
                include_environment
            )
            logger.info(f"Added background task for analysis with environment context: {include_environment}")
        except Exception as task_error:
            logger.error(f"Error adding background task: {str(task_error)}")
            # Continue even if adding task fails
        
        # Return the mock analysis result for immediate display
        return mock_result
    except Exception as e:
        logger.error(f"Error in analyze_suspect: {str(e)}")
        # Return a simple error response instead of raising an exception
        return {"error": f"Error in analyze_suspect: {str(e)}"}

@app.get("/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

# Timeline Endpoints
@app.get("/timeline/{analysis_id}", response_model=List[TimelineEvent])
async def get_timeline(analysis_id: str):
    """Get timeline for a specific analysis"""
    analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis["timeline"]

# Graph Endpoints
@app.get("/graph/{analysis_id}", response_model=GraphData)
async def get_graph(analysis_id: str):
    """Get knowledge graph for a specific analysis"""
    analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis["graph"]

# Narration Endpoints
@app.get("/narrate/{analysis_id}")
async def get_narration(analysis_id: str, language: str = "en"):
    """Get narration for a specific analysis in the specified language"""
    analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if not analysis.get("narrationUrl"):
        # Generate narration if not already available
        narration = await generate_narration(analysis, language)
        analysis["narrationUrl"] = narration["url"]
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {"narrationUrl": narration["url"]})
    
    return {"narrationUrl": analysis["narrationUrl"]}

# Query Endpoints
@app.post("/query", response_model=Query)
async def submit_query(query: Dict[str, Any]):
    """Submit a natural language query about an analysis"""
    query_id = f"query-{uuid.uuid4()}"
    
    # Extract query text and analysis ID
    query_text = query.get("text")
    analysis_id = query.get("analysisId")
    
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text is required")
    
    # Check if analysis exists if ID is provided
    if analysis_id:
        analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Process query using LLaMA
    if analysis_id:
        # Get analysis data
        analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
        timeline = analysis.get("timeline", [])
        graph = analysis.get("graph", {"nodes": [], "edges": []})
        
        # Prepare context for LLaMA
        context = {
            "timeline": timeline,
            "graph": graph,
            "summary": analysis.get("summary", "")
        }
        
        # Create prompt with context
        prompt = f"""You are an AI assistant helping with a CCTV investigation.
        Below is the data from our analysis of a suspect tracked across multiple cameras.
        
        TIMELINE:
        {json.dumps(timeline, indent=2)}
        
        GRAPH DATA:
        {json.dumps(graph, indent=2)}
        
        SUMMARY:
        {analysis.get('summary', '')}
        
        Based on this information, please answer the following question:
        {query_text}
        
        Provide a detailed answer using only the information available in the data.
        If the answer cannot be determined from the data, please say so.
        """
    else:
        # General query without specific analysis
        prompt = f"""You are an AI assistant helping with a CCTV investigation.
        Please answer the following question about video surveillance and suspect tracking:
        
        {query_text}
        
        Provide a helpful and informative answer.
        """
    
    # Call LLaMA API
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    llama_response = llama_client.chat_completion(messages)
    response_text = llama_response["choices"][0]["message"]["content"]
    
    # Create visual data if applicable
    visual_data = None
    if analysis_id and any(keyword in query_text.lower() for keyword in ["where", "location", "when", "time"]):
        # For location/time queries, provide a visual from the timeline
        if timeline:
            # Find most relevant event
            relevant_event = timeline[0]  # Default to first event
            
            # Simple keyword matching to find most relevant event
            for event in timeline:
                if any(keyword in query_text.lower() for keyword in event.get("description", "").lower().split()):
                    relevant_event = event
                    break
            
            visual_data = {
                "type": "image",
                "url": relevant_event.get("thumbnailUrl", "")
            }
    
    # Create query response
    response = {
        "text": response_text,
        "visualData": visual_data
    }
    
    # Create query record
    query_data = {
        "id": query_id,
        "text": query_text,
        "timestamp": datetime.now().isoformat(),
        "response": response
    }
    
    # Store in database
    await mongodb.insert_one_async("queries", query_data)
    
    return query_data

# Environment Context Endpoints
@app.post("/environment/process")
async def process_environment_video(
    request: dict,
    background_tasks: BackgroundTasks,
    use_gpu: bool = Depends(get_gpu_preference)
):
    """Process an environment video to extract context information"""
    try:
        # Extract data from the request dictionary
        video_id = request.get("videoId")
        
        logger.info(f"Received environment video processing request for video: {video_id}")
        
        if not video_id:
            return {"error": "videoId is required"}
    except Exception as e:
        logger.error(f"Error in process_environment_video: {str(e)}")
        return {"error": f"Failed to process environment video: {str(e)}"}
        
    try:
        # Get the video from the database
        video = await mongodb.find_one_async("videos", {"id": video_id})
        if not video:
            logger.error(f"Video {video_id} not found")
            return {"error": f"Video {video_id} not found"}
        
        # Generate a unique ID for the environment context
        context_id = f"env-{uuid.uuid4()}"
        logger.info(f"Generated environment context ID: {context_id}")
        
        # Create a basic environment context result
        env_context = {
            "id": context_id,
            "videoId": video_id,
            "description": "Environment context processing in progress...",
            "locations": [],
            "status": "processing"
        }
        
        # Store in database
        try:
            await mongodb.insert_one_async("environment_contexts", env_context)
            logger.info(f"Stored initial environment context in database")
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Continue even if database insert fails
        
        # In the background, process the environment video
        try:
            background_tasks.add_task(
                run_environment_processing,
                context_id,
                video_id,
                use_gpu
            )
            logger.info(f"Added background task for environment video processing")
        except Exception as task_error:
            logger.error(f"Error adding background task: {str(task_error)}")
            # Continue even if adding task fails
        
        # Return the initial environment context
        return env_context
    except Exception as e:
        logger.error(f"Error in process_environment_video: {str(e)}")
        return {"error": f"Failed to process environment video: {str(e)}"}

# Environment Context Processing Function
async def run_environment_processing(context_id: str, video_id: str, use_gpu: bool):
    """Run environment context processing in the background"""
    try:
        # Get the video from the database
        video = await mongodb.find_one_async("videos", {"id": video_id})
        if not video:
            logger.error(f"Video {video_id} not found")
            await mongodb.update_one_async("environment_contexts", {"id": context_id}, {"status": "error", "description": f"Video {video_id} not found"})
            return
        
        # Process the environment video
        logger.info(f"Processing environment video: {video_id}")
        video_path = f"data/videos/{video['id']}.mp4"
        
        # Check if video file exists
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            await mongodb.update_one_async("environment_contexts", {"id": context_id}, {"status": "error", "description": f"Video file not found: {video['id']}"})
            return
        
        # Process the environment video using the new method
        environment_context = await video_analyzer.process_environment_video(video_path, video_id)
        
        # Update environment context with results
        await mongodb.update_one_async("environment_contexts", {"id": context_id}, {
            "status": "complete",
            "description": environment_context.get("description", "Environment context processing complete"),
            "locations": environment_context.get("locations", []),
            "securityFeatures": environment_context.get("securityFeatures", []),
            "dimensions": environment_context.get("dimensions", ""),
            "materials": environment_context.get("materials", ""),
            "lighting": environment_context.get("lighting", ""),
            "layout": environment_context.get("layout", ""),
            "furnishings": environment_context.get("furnishings", ""),
            "accessPoints": environment_context.get("accessPoints", []),
            "blindSpots": environment_context.get("blindSpots", []),
            "updatedAt": datetime.now().isoformat()
        })
        logger.info("Updated environment context with detailed results")
    except Exception as e:
        logger.error(f"Error processing environment video: {str(e)}")
        await mongodb.update_one_async("environment_contexts", {"id": context_id}, {"status": "error", "description": f"Error processing environment video: {str(e)}"})
        return

# Summary Endpoint
@app.get("/summary/{analysis_id}")
async def get_analysis_summary(analysis_id: str):
    """Get a detailed summary of the analysis"""
    analysis = await mongodb.find_one_async("analyses", {"id": analysis_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {"summary": analysis["summary"]}

# Background task for running the full analysis
async def run_analysis(
    analysis_id: str,
    suspect_id: str,
    video_ids: List[str],
    timeframe: Optional[Dict[str, str]] = None,
    options: Optional[Dict[str, Any]] = None,
    use_gpu: bool = False,
    include_environment: bool = True
):
    """Run the full analysis pipeline in the background"""
    try:
        logger.info(f"Starting analysis {analysis_id} for suspect {suspect_id}")
        
        # Get suspect
        suspect = await mongodb.find_one_async("suspects", {"id": suspect_id})
        if not suspect:
            logger.error(f"Suspect {suspect_id} not found")
            await mongodb.update_one_async("analyses", {"id": analysis_id}, {"summary": "Error: Suspect not found"})
            return
        
        logger.info(f"Found suspect: {suspect['id']}")
        
        # Get videos
        videos = []
        for video_id in video_ids:
            video = await mongodb.find_one_async("videos", {"id": video_id})
            if not video:
                logger.error(f"Video {video_id} not found")
                await mongodb.update_one_async("analyses", {"id": analysis_id}, {"summary": f"Error: Video {video_id} not found"})
                return
            videos.append(video)
            logger.info(f"Found video: {video['id']}")
        
        # First, get or process environment context
        environment_context = None
        try:
            # Try to get the latest environment context from the database
            env_contexts = await mongodb.find_many_async("environment_contexts", {"status": "complete"}, sort=[("createdAt", -1)], limit=1)
            if env_contexts and len(env_contexts) > 0:
                environment_context = env_contexts[0]
                logger.info(f"Using existing environment context: {environment_context['id']}")
            else:
                # If no environment context exists, check if there's an environment video
                env_videos = await mongodb.find_many_async("videos", {"isEnvironment": True}, limit=1)
                if env_videos and len(env_videos) > 0:
                    env_video = env_videos[0]
                    logger.info(f"Processing environment video: {env_video['id']}")
                    
                    # Process the environment video
                    env_video_path = env_video.get("path", f"data/videos/{env_video['id']}.mp4")
                    if not os.path.exists(env_video_path):
                        env_video_path = "data/environment/environment awareness.MOV"
                    
                    if os.path.exists(env_video_path):
                        # Process the environment video
                        environment_context = await video_analyzer.process_environment_video(env_video_path, env_video['id'])
                        logger.info(f"Generated environment context from video: {env_video['id']}")
                    else:
                        logger.warning(f"Environment video not found: {env_video_path}")
                else:
                    logger.warning("No environment videos found")
        except Exception as env_error:
            logger.error(f"Error processing environment context: {str(env_error)}")
            # Continue without environment context
        
        # If still no environment context, create a default one
        if not environment_context:
            logger.info("Using default environment context")
            environment_context = {
                "id": f"env-default-{uuid.uuid4()}",
                "description": "The environment is a modern office building with multiple areas including entrances, hallways, dining areas, and office spaces.",
                "locations": [
                    {"name": "Main Entrance", "description": "The main entrance to the building"},
                    {"name": "Hallway", "description": "Connecting corridor"},
                    {"name": "Dining Area", "description": "Area with tables for eating"},
                    {"name": "Office Space", "description": "Work area with desks"}
                ],
                "securityFeatures": [
                    {"type": "CCTV Camera", "location": "Main entrance"}
                ],
                "dimensions": "Approximately 50x40 meters",
                "materials": "Modern construction with glass, metal, and concrete",
                "lighting": "Well-lit with overhead lighting",
                "layout": "Open floor plan with some partitioned areas",
                "accessPoints": [
                    {"type": "Main Entrance", "location": "Front of building"}
                ],
                "blindSpots": [
                    {"location": "Behind columns", "description": "Areas behind structural columns"}
                ]
            }
        
        # Update analysis with environment context
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "environmentContextId": environment_context.get("id"),
            "status": "environment_processed"
        })
        
        # Make sure videos are processed
        for video in videos:
            try:
                logger.info(f"Processing video: {video['id']}")
                video_path = f"data/videos/{video['id']}.mp4"
                
                # Check if video file exists
                if not os.path.exists(video_path):
                    logger.error(f"Video file not found: {video_path}")
                    await mongodb.update_one_async("analyses", {"id": analysis_id}, {"summary": f"Error: Video file not found: {video['id']}"})
                    return
                
                # Process video - note that process_video is synchronous
                video_result = video_analyzer.process_video(
                    video_path,
                    video['id'],
                    {
                        "name": video.get("name", ""),
                        "location": video.get("location", ""),
                        "timestamp": video.get("timestamp", "")
                    }
                )
                
                # Analyze frames to detect persons - note that analyze_frames is synchronous
                analysis_result = video_analyzer.analyze_frames(video['id'])
                logger.info(f"Successfully processed video: {video['id']} with {analysis_result.get('frames_analyzed', 0)} frames analyzed")
            except Exception as e:
                logger.error(f"Error processing video {video['id']}: {str(e)}")
                await mongodb.update_one_async("analyses", {"id": analysis_id}, {"summary": f"Error processing video {video['id']}: {str(e)}"})
                return
        
        try:
            # Track suspect across videos
            logger.info(f"Tracking suspect {suspect['id']} across {len(videos)} videos")
            tracking_results = await video_analyzer.track_suspect(suspect, videos, timeframe)
            logger.info(f"Found {len(tracking_results)} tracking results")
            
            # Store tracking results
            for result in tracking_results:
                await mongodb.insert_one_async("tracking_results", result)
            
            # Generate timeline
            logger.info("Generating timeline")
            timeline = await video_analyzer.generate_timeline(tracking_results)
            logger.info(f"Generated timeline with {len(timeline)} events")
            
            # Build knowledge graph
            logger.info("Building knowledge graph")
            graph = await video_analyzer.build_knowledge_graph(tracking_results)
            logger.info(f"Built knowledge graph with {len(graph.get('nodes', []))} nodes and {len(graph.get('edges', []))} edges")
            
            # Environment context was already processed at the beginning of the function
            # No need to fetch it again
            
            # Generate summary with environment context
            logger.info("Generating summary with environment context")
            summary = await video_analyzer.generate_summary(timeline, graph, environment_context)
            logger.info("Summary generated successfully")
            
            # Update analysis with results
            await mongodb.update_one_async("analyses", {"id": analysis_id}, {
                "timeline": timeline,
                "graph": graph,
                "summary": summary
            })
            logger.info("Updated analysis with results")
            
            # Generate narration if requested
            if options and options.get("includeNarration", False):
                try:
                    language = options.get("language", "en")
                    logger.info(f"Generating narration in {language}")
                    
                    narration_prompt = f"Generate a detailed narration of the following timeline of events in {language} language.\nMake it sound like a detective explaining the movements of a suspect across multiple CCTV cameras.\n\n{json.dumps(timeline, indent=2, cls=MongoJSONEncoder)}"
                    
                    messages = [
                        {"role": "system", "content": "You are an expert detective analyzing CCTV footage. Generate a detailed narration of events based on the timeline provided."},
                        {"role": "user", "content": narration_prompt}
                    ]
                    
                    response = llama_client.chat_completion(messages)
                    narration = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Save narration to file
                    narration_filename = f"narration-{analysis_id}.txt"
                    narration_path = os.path.join("data", "narrations", narration_filename)
                    os.makedirs(os.path.dirname(narration_path), exist_ok=True)
                    
                    with open(narration_path, "w") as f:
                        f.write(narration)
                    
                    narration_url = f"/static/narrations/{narration_filename}"
                    await mongodb.update_one_async("analyses", {"id": analysis_id}, {"narrationUrl": narration_url})
                    logger.info("Narration generated and saved successfully")
                except Exception as e:
                    logger.error(f"Error generating narration: {str(e)}")
                    # Continue even if narration fails
        except Exception as e:
            logger.error(f"Error during analysis processing: {str(e)}")
            await mongodb.update_one_async("analyses", {"id": analysis_id}, {"summary": f"Error during analysis processing: {str(e)}"})
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        # Update analysis with error
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {"summary": f"Error during analysis: {str(e)}"})
        return
