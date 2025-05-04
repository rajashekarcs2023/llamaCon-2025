import os
import logging
from typing import Dict, List, Any
import asyncio
from datetime import datetime
from utils.video_processor import extract_frame, generate_video_clip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_timeline(tracking_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate a timeline of events from tracking results
    
    Args:
        tracking_results: List of suspect tracking results
    
    Returns:
        List of timeline events
    """
    logger.info(f"Generating timeline from {len(tracking_results)} tracking results")
    
    timeline_events = []
    
    # Process each tracking result
    for result in tracking_results:
        try:
            # Get video path
            video_id = result['videoId']
            video_path = f"data/videos/{video_id}.mp4"
            
            if not os.path.exists(video_path):
                logger.warning(f"Video file not found: {video_path}")
                continue
            
            # Generate thumbnail for the event
            frame_time = result['startTime']
            frame = await extract_frame(video_path, frame_time)
            
            # Save thumbnail
            event_id = result['id']
            thumbnail_path = f"data/results/{event_id}_thumb.jpg"
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            import cv2
            cv2.imwrite(thumbnail_path, frame)
            
            # Generate video clip
            clip_path = f"data/results/{event_id}_clip.mp4"
            await generate_video_clip(
                video_path,
                result['startTime'],
                result['endTime'],
                clip_path
            )
            
            # Create timeline event
            event = {
                "id": event_id,
                "suspectId": result['suspectId'],
                "videoId": video_id,
                "timestamp": result['timestamp'],
                "confidence": result['confidence'],
                "thumbnailUrl": f"/results/{event_id}_thumb.jpg",
                "clipUrl": f"/results/{event_id}_clip.mp4",
                "description": generate_event_description(result),
                "startTime": result['startTime'],
                "endTime": result['endTime']
            }
            
            timeline_events.append(event)
            
        except Exception as e:
            logger.error(f"Error processing tracking result: {str(e)}")
    
    # Sort events by timestamp
    timeline_events.sort(key=lambda x: x['timestamp'])
    
    return timeline_events

def generate_event_description(result: Dict[str, Any]) -> str:
    """
    Generate a natural language description of an event
    
    Args:
        result: Tracking result data
    
    Returns:
        Description string
    """
    # In a real implementation, this would use LLaMA to generate more detailed descriptions
    # For now, we'll use a simple template
    
    # Parse timestamp
    timestamp = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
    time_str = timestamp.strftime("%I:%M %p")
    
    # Get confidence level description
    confidence = result['confidence']
    if confidence >= 90:
        confidence_desc = "high confidence"
    elif confidence >= 70:
        confidence_desc = "medium confidence"
    else:
        confidence_desc = "low confidence"
    
    # Generate description
    description = f"Suspect detected at {time_str} with {confidence_desc}"
    
    return description

async def merge_nearby_events(timeline: List[Dict[str, Any]], max_gap_seconds: int = 60) -> List[Dict[str, Any]]:
    """
    Merge events that are close in time to reduce clutter
    
    Args:
        timeline: List of timeline events
        max_gap_seconds: Maximum time gap in seconds to merge events
    
    Returns:
        Merged timeline events
    """
    if not timeline:
        return []
    
    # Sort by timestamp
    sorted_events = sorted(timeline, key=lambda x: x['timestamp'])
    
    merged_events = [sorted_events[0]]
    
    for event in sorted_events[1:]:
        last_event = merged_events[-1]
        
        # Parse timestamps
        last_time = datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
        current_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        
        # Calculate time difference in seconds
        time_diff = (current_time - last_time).total_seconds()
        
        # If events are close and in the same video, merge them
        if time_diff <= max_gap_seconds and event['videoId'] == last_event['videoId']:
            # Update end time
            last_event['endTime'] = event['endTime']
            
            # Update confidence to max of both
            last_event['confidence'] = max(last_event['confidence'], event['confidence'])
            
            # Update description
            last_event['description'] += f" and again at {current_time.strftime('%I:%M %p')}"
        else:
            # Add as new event
            merged_events.append(event)
    
    return merged_events
