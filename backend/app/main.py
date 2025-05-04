from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import uuid
import shutil
from datetime import datetime
import json

# Import models
from models.video import VideoFeed
from models.suspect import Suspect
from models.timeline import TimelineEvent
from models.graph import GraphData, GraphNode, GraphEdge
from models.analysis import AnalysisRequest, AnalysisResult
from models.query import Query

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
    suspect = await mongodb.find_one_async("suspects", {"id": suspect_id})
    if not suspect:
        raise HTTPException(status_code=404, detail="Suspect not found")
    return suspect

# Analysis Endpoints
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_suspect(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Run suspect tracking analysis across selected videos"""
    # Validate request
    suspect = await mongodb.find_one_async("suspects", {"id": request.suspectId})
    if not suspect:
        raise HTTPException(status_code=404, detail="Suspect not found")
    
    for video_id in request.videoIds:
        video = await mongodb.find_one_async("videos", {"id": video_id})
        if not video:
            raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
    
    # Generate a unique ID for the analysis
    analysis_id = f"analysis-{uuid.uuid4()}"
    
    # Create initial analysis result
    analysis_result = {
        "id": analysis_id,
        "suspectId": request.suspectId,
        "timeline": [],
        "graph": {"nodes": [], "edges": []},
        "summary": "Analysis in progress...",
        "narrationUrl": None
    }
    
    # Store in database
    await mongodb.insert_one_async("analyses", analysis_result)
    
    # Run analysis in background
    background_tasks.add_task(
        run_analysis,
        analysis_id,
        request.suspectId,
        request.videoIds,
        request.timeframe,
        request.options
    )
    
    return analysis_result

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

# Summary Endpoint
@app.get("/summary/{analysis_id}")
async def get_summary(analysis_id: str):
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
    options: Optional[Dict[str, Any]] = None
):
    """Run the full analysis pipeline in the background"""
    try:
        # Get suspect and video data
        suspect = await mongodb.find_one_async("suspects", {"id": suspect_id})
        videos = []
        for video_id in video_ids:
            video = await mongodb.find_one_async("videos", {"id": video_id})
            if video:
                videos.append(video)
        
        # Make sure videos are processed
        for video in videos:
            if not video.get("processed", False):
                logger.info(f"Processing video: {video['id']}")
                await video_analyzer.process_video(
                    f"data/videos/{video['id']}.mp4",
                    video['id'],
                    {
                        "name": video.get("name", ""),
                        "location": video.get("location", ""),
                        "timestamp": video.get("timestamp", "")
                    }
                )
                
                # Analyze frames to detect persons
                await video_analyzer.analyze_frames(video['id'])
        
        # Track suspect across videos
        tracking_results = await video_analyzer.track_suspect(suspect, videos, timeframe)
        
        # Store tracking results
        for result in tracking_results:
            await mongodb.insert_one_async("tracking_results", result)
        
        # Generate timeline
        timeline = await video_analyzer.generate_timeline(tracking_results)
        
        # Build knowledge graph
        graph = await video_analyzer.build_knowledge_graph(tracking_results)
        
        # Generate summary using LLaMA
        summary = await video_analyzer.generate_summary(timeline)
        
        # Generate narration if requested
        narration_url = None
        if options and options.get("includeNarration"):
            language = options.get("language", "en")
            
            # Generate narration text using LLaMA
            narration_prompt = f"""Generate a detailed narration of the following timeline of events in {language} language.
            Make it sound like a detective explaining the movements of a suspect across multiple CCTV cameras.
            
            {json.dumps(timeline, indent=2)}
            """
            
            messages = [
                {
                    "role": "user",
                    "content": narration_prompt
                }
            ]
            
            response = llama_client.chat_completion(messages)
            narration_text = response["choices"][0]["message"]["content"]
            
            # In a real implementation, we would convert this text to speech
            # For now, we'll just store the text in a file
            narration_file = f"data/results/{analysis_id}_narration.txt"
            os.makedirs(os.path.dirname(narration_file), exist_ok=True)
            
            with open(narration_file, "w") as f:
                f.write(narration_text)
            
            narration_url = f"/results/{analysis_id}_narration.txt"
        
        # Update analysis result
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "timeline": timeline,
            "graph": graph,
            "summary": summary,
            "narrationUrl": narration_url
        })
        
    except Exception as e:
        # Update analysis with error
        await mongodb.update_one_async("analyses", {"id": analysis_id}, {
            "summary": f"Error during analysis: {str(e)}"
        })
