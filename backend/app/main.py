from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import uuid
import shutil
from datetime import datetime
import json

# Import models and utils (to be implemented)
from models.video import VideoFeed
from models.suspect import Suspect
from models.timeline import TimelineEvent
from models.graph import GraphData, GraphNode, GraphEdge
from models.analysis import AnalysisRequest, AnalysisResult
from models.query import Query

# Import utilities (to be implemented)
from utils.video_processor import process_video
from utils.suspect_tracker import track_suspect
from utils.timeline_generator import generate_timeline
from utils.graph_builder import build_knowledge_graph
from utils.llama_integration import generate_narration, answer_query

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

# In-memory storage for development (replace with MongoDB in production)
videos_db = {}
suspects_db = {}
analyses_db = {}
queries_db = {}

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
        background_tasks.add_task(process_video, file_path, video_id)
    
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
    videos_db[video_id] = video_data
    
    return video_data

@app.get("/videos", response_model=List[VideoFeed])
async def get_videos():
    """Get all uploaded videos"""
    return list(videos_db.values())

@app.get("/videos/{video_id}", response_model=VideoFeed)
async def get_video(video_id: str):
    """Get a specific video by ID"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    return videos_db[video_id]

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
    suspects_db[suspect_id] = suspect_data
    
    return suspect_data

@app.get("/suspects", response_model=List[Suspect])
async def get_suspects():
    """Get all uploaded suspects"""
    return list(suspects_db.values())

@app.get("/suspects/{suspect_id}", response_model=Suspect)
async def get_suspect(suspect_id: str):
    """Get a specific suspect by ID"""
    if suspect_id not in suspects_db:
        raise HTTPException(status_code=404, detail="Suspect not found")
    return suspects_db[suspect_id]

# Analysis Endpoints
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_suspect(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Run suspect tracking analysis across selected videos"""
    # Validate request
    if request.suspectId not in suspects_db:
        raise HTTPException(status_code=404, detail="Suspect not found")
    
    for video_id in request.videoIds:
        if video_id not in videos_db:
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
    analyses_db[analysis_id] = analysis_result
    
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
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analyses_db[analysis_id]

# Timeline Endpoints
@app.get("/timeline/{analysis_id}", response_model=List[TimelineEvent])
async def get_timeline(analysis_id: str):
    """Get timeline for a specific analysis"""
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analyses_db[analysis_id]["timeline"]

# Graph Endpoints
@app.get("/graph/{analysis_id}", response_model=GraphData)
async def get_graph(analysis_id: str):
    """Get knowledge graph for a specific analysis"""
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analyses_db[analysis_id]["graph"]

# Narration Endpoints
@app.get("/narrate/{analysis_id}")
async def get_narration(analysis_id: str, language: str = "en"):
    """Get narration for a specific analysis in the specified language"""
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses_db[analysis_id]
    
    if not analysis["narrationUrl"]:
        # Generate narration if not already available
        narration = await generate_narration(analysis, language)
        analysis["narrationUrl"] = narration["url"]
        analyses_db[analysis_id] = analysis
    
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
    if analysis_id and analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Process query
    response = await answer_query(query_text, analysis_id)
    
    # Create query record
    query_data = {
        "id": query_id,
        "text": query_text,
        "timestamp": datetime.now().isoformat(),
        "response": response
    }
    
    # Store in database
    queries_db[query_id] = query_data
    
    return query_data

# Summary Endpoint
@app.get("/summary/{analysis_id}")
async def get_summary(analysis_id: str):
    """Get a detailed summary of the analysis"""
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {"summary": analyses_db[analysis_id]["summary"]}

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
        suspect = suspects_db[suspect_id]
        videos = [videos_db[video_id] for video_id in video_ids]
        
        # Track suspect across videos
        tracking_results = await track_suspect(suspect, videos, timeframe)
        
        # Generate timeline
        timeline = await generate_timeline(tracking_results)
        
        # Build knowledge graph
        graph = await build_knowledge_graph(tracking_results)
        
        # Generate summary using LLaMA
        summary = "Suspect was tracked across multiple camera feeds. Analysis complete."
        
        # Generate narration if requested
        narration_url = None
        if options and options.get("includeNarration"):
            language = options.get("language", "en")
            narration = await generate_narration(
                {"timeline": timeline, "graph": graph},
                language
            )
            narration_url = narration["url"]
        
        # Update analysis result
        analyses_db[analysis_id].update({
            "timeline": timeline,
            "graph": graph,
            "summary": summary,
            "narrationUrl": narration_url
        })
        
    except Exception as e:
        # Update analysis with error
        analyses_db[analysis_id].update({
            "summary": f"Error during analysis: {str(e)}"
        })
