import cv2
import os
import numpy as np
from typing import Dict, List, Any
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_video(file_path: str, video_id: str) -> Dict[str, Any]:
    """
    Process a video file to extract frames, duration, and generate a thumbnail
    
    Args:
        file_path: Path to the video file
        video_id: Unique ID of the video
    
    Returns:
        Dict with video metadata
    """
    logger.info(f"Processing video: {file_path}")
    
    try:
        # Open the video file
        cap = cv2.VideoCapture(file_path)
        
        if not cap.isOpened():
            logger.error(f"Error opening video file: {file_path}")
            return {"error": "Failed to open video file"}
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create frames directory if it doesn't exist
        frames_dir = f"data/videos/frames/{video_id}"
        os.makedirs(frames_dir, exist_ok=True)
        
        # Extract frames at regular intervals (1 frame per second)
        frame_interval = int(fps)
        frames_extracted = 0
        
        # Generate thumbnail from first frame
        ret, frame = cap.read()
        if ret:
            thumbnail_path = f"data/videos/{video_id}_thumb.jpg"
            cv2.imwrite(thumbnail_path, frame)
        
        # Extract frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        current_frame = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if current_frame % frame_interval == 0:
                frame_path = f"{frames_dir}/frame_{frames_extracted:04d}.jpg"
                cv2.imwrite(frame_path, frame)
                frames_extracted += 1
            
            current_frame += 1
            
            # Limit to 1000 frames for very long videos
            if frames_extracted >= 1000:
                break
        
        # Release the video capture object
        cap.release()
        
        logger.info(f"Video processing complete: {video_id}, extracted {frames_extracted} frames")
        
        # Update video metadata
        video_metadata = {
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps,
            "frame_count": frame_count,
            "frames_extracted": frames_extracted,
            "processed": True
        }
        
        # In a real implementation, this would update the database
        # For now, we'll just return the metadata
        return video_metadata
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return {"error": str(e)}

async def extract_frame(video_path: str, timestamp: float) -> np.ndarray:
    """
    Extract a specific frame from a video at the given timestamp
    
    Args:
        video_path: Path to the video file
        timestamp: Time in seconds to extract the frame from
    
    Returns:
        The extracted frame as a numpy array
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate frame number from timestamp
    frame_number = int(timestamp * fps)
    
    # Set position to the desired frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    ret, frame = cap.read()
    
    # Release the video capture object
    cap.release()
    
    if not ret:
        raise ValueError(f"Could not read frame at timestamp {timestamp}")
    
    return frame

async def generate_video_clip(video_path: str, start_time: float, end_time: float, output_path: str) -> str:
    """
    Generate a short video clip from a specific time range
    
    Args:
        video_path: Path to the video file
        start_time: Start time in seconds
        end_time: End time in seconds
        output_path: Path to save the output clip
    
    Returns:
        Path to the generated clip
    """
    try:
        # This is a simplified implementation
        # In a production system, you might use ffmpeg directly
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Calculate start and end frames
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        # Set position to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Read and write frames
        for _ in range(end_frame - start_frame):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        
        # Release objects
        cap.release()
        out.release()
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating video clip: {str(e)}")
        raise
