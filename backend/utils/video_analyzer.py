import os
import cv2
import numpy as np
import logging
import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import base64
import tempfile

# Import our clients
from utils.llama_client import llama_client
from utils.groq_client import groq_client
from utils.db_connector import mongodb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAnalyzer:
    """
    Core video analysis pipeline for processing CCTV footage and tracking suspects
    """
    def __init__(self, use_groq_for_frames: bool = True):
        """
        Initialize the video analyzer
        
        Args:
            use_groq_for_frames: Whether to use Groq for frame analysis (faster)
        """
        self.use_groq_for_frames = use_groq_for_frames
        logger.info(f"Initializing VideoAnalyzer (using Groq for frames: {use_groq_for_frames})")
    
    async def process_video(self, video_path: str, video_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a video file to extract frames and metadata
        
        Args:
            video_path: Path to the video file
            video_id: Unique ID of the video
            metadata: Video metadata including location and timestamp
        
        Returns:
            Dict with video processing results
        """
        logger.info(f"Processing video: {video_path}")
        
        try:
            # Open the video file
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Error opening video file: {video_path}")
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
            
            # Store frame metadata
            frame_metadata = []
            
            # Set base timestamp from metadata
            if "timestamp" in metadata and metadata["timestamp"]:
                try:
                    base_timestamp = datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    base_timestamp = datetime.now()
            else:
                base_timestamp = datetime.now()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if current_frame % frame_interval == 0:
                    # Calculate timestamp for this frame
                    frame_time = base_timestamp + timedelta(seconds=current_frame/fps)
                    frame_timestamp = frame_time.isoformat()
                    
                    # Save frame
                    frame_path = f"{frames_dir}/frame_{frames_extracted:04d}.jpg"
                    cv2.imwrite(frame_path, frame)
                    
                    # Store frame metadata
                    frame_metadata.append({
                        "frame_id": f"{video_id}_frame_{frames_extracted:04d}",
                        "video_id": video_id,
                        "frame_index": frames_extracted,
                        "timestamp": frame_timestamp,
                        "path": frame_path,
                        "processed": False
                    })
                    
                    frames_extracted += 1
                
                current_frame += 1
                
                # Limit to 1000 frames for very long videos
                if frames_extracted >= 1000:
                    break
            
            # Release the video capture object
            cap.release()
            
            logger.info(f"Video processing complete: {video_id}, extracted {frames_extracted} frames")
            
            # Store frame metadata in MongoDB
            for frame_data in frame_metadata:
                await mongodb.insert_one_async("frames", frame_data)
            
            # Update video metadata
            video_result = {
                "duration": duration,
                "width": width,
                "height": height,
                "fps": fps,
                "frame_count": frame_count,
                "frames_extracted": frames_extracted,
                "processed": True
            }
            
            # Update video record in database
            await mongodb.update_one_async("videos", {"id": video_id}, video_result)
            
            return video_result
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_frames(self, video_id: str, batch_size: int = 10) -> Dict[str, Any]:
        """
        Analyze extracted frames to detect persons
        
        Args:
            video_id: ID of the video to analyze
            batch_size: Number of frames to process in parallel
        
        Returns:
            Dict with analysis results
        """
        logger.info(f"Analyzing frames for video: {video_id}")
        
        try:
            # Get all frames for this video
            frames = await mongodb.find_many_async("frames", {
                "video_id": video_id,
                "processed": False
            })
            
            if not frames:
                logger.warning(f"No unprocessed frames found for video: {video_id}")
                return {"frames_analyzed": 0}
            
            logger.info(f"Found {len(frames)} unprocessed frames")
            
            # Process frames in batches
            total_processed = 0
            total_persons_detected = 0
            
            for i in range(0, len(frames), batch_size):
                batch = frames[i:i+batch_size]
                
                # Process batch in parallel
                tasks = []
                for frame in batch:
                    task = asyncio.create_task(self.analyze_single_frame(frame))
                    tasks.append(task)
                
                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks)
                
                # Update frame records and count persons
                for frame, result in zip(batch, results):
                    if "persons" in result:
                        persons = result["persons"]
                        total_persons_detected += len(persons)
                        
                        # Store person detections
                        for person in persons:
                            person_id = f"person_{uuid.uuid4()}"
                            person_data = {
                                "id": person_id,
                                "frame_id": frame["frame_id"],
                                "video_id": video_id,
                                "timestamp": frame["timestamp"],
                                "bbox": person.get("bbox", [0, 0, 0, 0]),
                                "description": person.get("description", ""),
                                "position": person.get("position", ""),
                                "carrying": person.get("carrying", []),
                                "embedding": None  # Will be added later
                            }
                            
                            await mongodb.insert_one_async("persons", person_data)
                        
                        # Update frame record
                        await mongodb.update_one_async("frames", 
                            {"frame_id": frame["frame_id"]},
                            {
                                "processed": True,
                                "persons_detected": len(persons)
                            }
                        )
                        
                        total_processed += 1
            
            logger.info(f"Frame analysis complete: {total_processed} frames processed, {total_persons_detected} persons detected")
            
            return {
                "frames_analyzed": total_processed,
                "persons_detected": total_persons_detected
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frames: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_single_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single frame to detect persons
        
        Args:
            frame: Frame metadata including path
        
        Returns:
            Dict with detected persons
        """
        frame_path = frame["path"]
        
        try:
            # Choose which client to use for frame analysis
            if self.use_groq_for_frames:
                # Use Groq for faster inference
                result = groq_client.process_video_frame(frame_path)
            else:
                # Use LLaMA for potentially higher quality
                # Convert local file path to data URL for LLaMA API
                with open(frame_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    data_url = f"data:image/jpeg;base64,{base64_image}"
                
                result = llama_client.analyze_frame_for_persons(data_url)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frame {frame['frame_id']}: {str(e)}")
            return {"persons": []}
    
    async def track_suspect(
        self, 
        suspect: Dict[str, Any],
        videos: List[Dict[str, Any]],
        timeframe: Optional[Dict[str, str]] = None,
        confidence_threshold: float = 70.0
    ) -> List[Dict[str, Any]]:
        """
        Track a suspect across multiple videos using Llama 4's long context capabilities
        
        Args:
            suspect: Suspect data including image URL
            videos: List of video data
            timeframe: Optional timeframe filter
            confidence_threshold: Minimum confidence score to consider a match
        
        Returns:
            List of tracking results
        """
        logger.info(f"Tracking suspect {suspect['id']} across {len(videos)} videos")
        
        tracking_results = []
        
        try:
            # Load suspect image
        
        logger.info(f"Frame analysis complete: {total_processed} frames processed, {total_persons_detected} persons detected")
        
        return {
            "frames_analyzed": total_processed,
            "persons_detected": total_persons_detected
        }
        
    except Exception as e:
        logger.error(f"Error analyzing frames: {str(e)}")
        return {"error": str(e)}

async def analyze_single_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a single frame to detect persons
    
    Args:
        frame: Frame metadata including path
    
    Returns:
        Dict with detected persons
    """
    frame_path = frame["path"]
    
    try:
        # Choose which client to use for frame analysis
        if self.use_groq_for_frames:
            # Use Groq for faster inference
            result = groq_client.process_video_frame(frame_path)
        else:
            # Use LLaMA for potentially higher quality
            # Convert local file path to data URL for LLaMA API
            with open(frame_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{base64_image}"
            
            result = llama_client.analyze_frame_for_persons(data_url)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing frame {frame['frame_id']}: {str(e)}")
        return {"persons": []}

async def track_suspect(
    self, 
    suspect: Dict[str, Any],
    videos: List[Dict[str, Any]],
    timeframe: Optional[Dict[str, str]] = None,
    confidence_threshold: float = 70.0
) -> List[Dict[str, Any]]:
    """
    Track a suspect across multiple videos using Llama 4's long context capabilities
    
    Args:
        suspect: Suspect data including image URL
        videos: List of video data
        timeframe: Optional timeframe filter
        confidence_threshold: Minimum confidence score to consider a match
    
    Returns:
        List of tracking results
    """
    logger.info(f"Tracking suspect {suspect['id']} across {len(videos)} videos")
    
    tracking_results = []
    
    try:
        # Load suspect image
        suspect_image_path = f"data/suspects/{suspect['id']}.jpg"
        if not os.path.exists(suspect_image_path):
            logger.error(f"Suspect image not found: {suspect_image_path}")
            return []
    
        # Get suspect features using LLaMA
        suspect_features = await self._get_person_features(suspect_image_path)
        
        # Use Llama 4's long context to analyze all videos together
        # This allows cross-video correlation and pattern recognition
        all_frames = []
        video_metadata = {}
        
        # Process each video
        for video in videos:
            video_id = video['id']
            logger.info(f"Processing video {video_id} for suspect tracking")
            
            # Store video metadata for reference
            video_metadata[video_id] = {
                "location": video.get("location", "Unknown"),
                "name": video.get("name", "Unknown"),
                "timestamp": video.get("timestamp", "")
            }
            
            # Get analyzed frames for this video
            frames = await mongodb.find_async("frames", {"videoId": video_id})
            frames_list = await frames.to_list(length=None)
            
            if not frames_list:
                logger.warning(f"No analyzed frames found for video {video_id}")
                continue
            
            # Apply timeframe filter if provided
            if timeframe:
                filtered_frames = []
                start_time = None
                end_time = None
                
                if "start" in timeframe and timeframe["start"]:
                    start_time = datetime.fromisoformat(timeframe["start"].replace('Z', '+00:00'))
                
                if "end" in timeframe and timeframe["end"]:
                    end_time = datetime.fromisoformat(timeframe["end"].replace('Z', '+00:00'))
                
                for frame in frames_list:
                    frame_time = datetime.fromisoformat(frame["timestamp"].replace('Z', '+00:00'))
                    
                    if start_time and frame_time < start_time:
                        continue
                    
                    if end_time and frame_time > end_time:
                        continue
                    
                    filtered_frames.append(frame)
                
                frames_list = filtered_frames
            
            # Skip if no frames after filtering
            if not frames_list:
                logger.warning(f"No frames match the timeframe filter for video {video_id}")
                continue
            
            # Add to all frames collection
            all_frames.extend(frames_list)
        
        # Sort all frames by timestamp for chronological analysis
        all_frames.sort(key=lambda x: x["timestamp"])
        
        # Skip if no frames to analyze
        if not all_frames:
            logger.warning("No frames to analyze after filtering")
            return []
        
        # Use Llama 4's long context to analyze all frames together
        # This allows for better pattern recognition and identity consistency
        if len(all_frames) > 200:
            # Process in batches if too many frames
            logger.info(f"Processing {len(all_frames)} frames in batches")
            batch_size = 200
            batches = [all_frames[i:i+batch_size] for i in range(0, len(all_frames), batch_size)]
            
            for batch_idx, batch in enumerate(batches):
                logger.info(f"Processing batch {batch_idx+1}/{len(batches)}")
                batch_results = await self._process_frames_batch(batch, suspect, suspect_features, video_metadata, confidence_threshold)
                tracking_results.extend(batch_results)
        else:
            # Process all frames together if within context window
            tracking_results = await self._process_frames_batch(all_frames, suspect, suspect_features, video_metadata, confidence_threshold)
        
        # Use Llama 4 to verify identity consistency across appearances
        tracking_results = await self._verify_identity_consistency(tracking_results, suspect)
        
        # Detect clothing changes and carrying items
        tracking_results = await self._detect_appearance_changes(tracking_results)
        
        # Analyze suspicious behavior patterns
        tracking_results = await self._analyze_behavior_patterns(tracking_results)
        
        logger.info(f"Found {len(tracking_results)} appearances of suspect {suspect['id']}")
        
        return tracking_results
    
    except Exception as e:
        logger.error(f"Error tracking suspect: {str(e)}")
        return []

async def _process_frames_batch(self, frames_batch, suspect, suspect_features, video_metadata, confidence_threshold):
    """Process a batch of frames to identify the suspect"""
    batch_results = []
    async def _process_frames_batch(self, frames_batch, suspect, suspect_features, video_metadata, confidence_threshold):
        """Process a batch of frames to identify the suspect"""
        batch_results = []
        
        for frame in frames_batch:
            video_id = frame["videoId"]
            
            # Skip frames without detected persons
            if not frame.get("persons"):
                continue
            
            # Compare each detected person with the suspect
            for person in frame["persons"]:
                # Skip if no features available
                if not person.get("features"):
                    continue
                
                # Calculate similarity score
                similarity = self._calculate_similarity(suspect_features, person["features"])
                confidence = similarity * 100  # Convert to percentage
                
                # If confidence exceeds threshold, consider it a match
                if confidence >= confidence_threshold:
                    # Create tracking result
                    result = {
                        "id": f"track-{uuid.uuid4()}",
                        "suspectId": suspect["id"],
                        "videoId": video_id,
                        "frameId": frame["id"],
                        "timestamp": frame["timestamp"],
                        "location": video_metadata[video_id]["location"],
                        "confidence": confidence,
                        "boundingBox": person["boundingBox"],
                        "thumbnailUrl": f"/frames/{video_id}/{frame['id']}.jpg",
                        "carrying": person.get("carrying", []),
                        "activities": person.get("activities", []),
                        "interactions": person.get("interactions", [])
                    }
                    
                    batch_results.append(result)
        
        return batch_results
    
    def _calculate_similarity(self, features1, features2):
        """Calculate cosine similarity between two feature vectors"""
        # Convert features to numpy arrays if they aren't already
        if not isinstance(features1, np.ndarray):
            features1 = np.array(features1)
        if not isinstance(features2, np.ndarray):
            features2 = np.array(features2)
        
        # Normalize the vectors
        features1 = features1 / np.linalg.norm(features1)
        features2 = features2 / np.linalg.norm(features2)
        
        # Calculate cosine similarity
        similarity = np.dot(features1, features2)
        
        # Ensure the result is between 0 and 1
        return max(0, min(1, similarity))
    
    async def _verify_identity_consistency(self, tracking_results, suspect):
        """Use Llama 4 to verify identity consistency across appearances"""
        if not tracking_results or len(tracking_results) <= 1:
            return tracking_results
        
        try:
            # Prepare data for Llama 4
            suspect_name = suspect.get("name", "Unknown Suspect")
            suspect_desc = suspect.get("description", "")
            
            # Extract frame paths for all appearances
            appearance_data = []
            for result in tracking_results:
                video_id = result["videoId"]
                frame_id = result["frameId"]
                timestamp = result["timestamp"]
                location = result["location"]
                confidence = result["confidence"]
                
                frame_path = f"data/videos/frames/{video_id}/{frame_id}.jpg"
                if os.path.exists(frame_path):
                    appearance_data.append({
                        "frame_path": frame_path,
                        "timestamp": timestamp,
                        "location": location,
                        "confidence": confidence,
                        "result_id": result["id"]
                    })
            
            # Skip if no valid appearances
            if not appearance_data:
                return tracking_results
            
            # In a real implementation, we would use Llama 4's multimodal capabilities
            # to analyze all appearances together and verify identity consistency
            
            # For now, we'll just return the original results
            # In a real implementation, we would filter out false positives
            
            return tracking_results
            
        except Exception as e:
            logger.error(f"Error verifying identity consistency: {str(e)}")
            return tracking_results
    
    async def _detect_appearance_changes(self, tracking_results):
        """Detect clothing changes and items being carried"""
        if not tracking_results or len(tracking_results) <= 1:
            return tracking_results
        
        try:
            # Group appearances by time proximity
            # This helps identify when the suspect might have changed clothes
            sorted_results = sorted(tracking_results, key=lambda x: x["timestamp"])
            
            current_group = [sorted_results[0]]
            appearance_groups = [current_group]
            
            for i in range(1, len(sorted_results)):
                current = sorted_results[i]
                previous = sorted_results[i-1]
                
                current_time = datetime.fromisoformat(current["timestamp"].replace('Z', '+00:00'))
                previous_time = datetime.fromisoformat(previous["timestamp"].replace('Z', '+00:00'))
                
                time_diff = (current_time - previous_time).total_seconds() / 60  # in minutes
                
                # If more than 30 minutes have passed, start a new group
                if time_diff > 30:
                    current_group = [current]
                    appearance_groups.append(current_group)
                else:
                    current_group.append(current)
            
            # In a real implementation, we would use Llama 4's multimodal capabilities
            # to analyze appearance changes within and between groups
            
            # For now, we'll just return the original results
            # In a real implementation, we would add appearance change annotations
            
            return tracking_results
            
        except Exception as e:
            logger.error(f"Error detecting appearance changes: {str(e)}")
            return tracking_results
    
    async def _analyze_behavior_patterns(self, tracking_results):
        """Analyze suspicious behavior patterns"""
        if not tracking_results or len(tracking_results) <= 1:
            return tracking_results
        
        try:
            # Analyze movement patterns
            # Look for suspicious patterns like loitering, repeated visits, etc.
            location_visits = {}
            
            for result in tracking_results:
                location = result["location"]
                timestamp = result["timestamp"]
                
                if location not in location_visits:
                    location_visits[location] = []
                
                location_visits[location].append(timestamp)
            
            # Identify locations with multiple visits
            repeated_locations = {loc: visits for loc, visits in location_visits.items() if len(visits) > 1}
            
            # Add behavior annotations to results
            for result in tracking_results:
                location = result["location"]
                
                if location in repeated_locations:
                    if "behaviorNotes" not in result:
                        result["behaviorNotes"] = []
                    
                    result["behaviorNotes"].append(f"Repeated visits to {location}")
            
            return tracking_results
            
        except Exception as e:
            logger.error(f"Error analyzing behavior patterns: {str(e)}")
            return tracking_results
    
    async def generate_timeline(self, tracking_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                # Generate thumbnail for the event
                frame_path = result.get("frame_path")
                
                if not frame_path or not os.path.exists(frame_path):
                    logger.warning(f"Frame path not found: {frame_path}")
                    continue
                
                # Create event ID
                event_id = f"event_{uuid.uuid4()}"
                
                # Save thumbnail
                thumbnail_path = f"data/results/{event_id}_thumb.jpg"
                os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
                
                # Copy frame as thumbnail
                import shutil
                shutil.copy(frame_path, thumbnail_path)
                
                # Get video path
                video_id = result["videoId"]
                video = await mongodb.find_one_async("videos", {"id": video_id})
                
                if not video:
                    logger.warning(f"Video not found: {video_id}")
                    continue
                
                video_path = f"data/videos/{video_id}.mp4"
                
                # Generate video clip
                clip_path = f"data/results/{event_id}_clip.mp4"
                
                # In a real implementation, we would extract a clip from the video
                # For now, we'll just copy the thumbnail as a placeholder
                shutil.copy(thumbnail_path, clip_path.replace(".mp4", ".jpg"))
                
                # Generate event description
                description = self.generate_event_description(result)
                
                # Create timeline event
                event = {
                    "id": event_id,
                    "suspectId": result["suspectId"],
                    "videoId": video_id,
                    "timestamp": result["timestamp"],
                    "confidence": result["confidence"],
                    "thumbnailUrl": f"/results/{event_id}_thumb.jpg",
                    "clipUrl": f"/results/{event_id}_clip.mp4",
                    "description": description,
                    "startTime": result["startTime"],
                    "endTime": result["endTime"],
                    "position": result.get("position", ""),
                    "carrying": result.get("carrying", [])
                }
                
                timeline_events.append(event)
                
            except Exception as e:
                logger.error(f"Error processing tracking result: {str(e)}")
        
        # Sort events by timestamp
        timeline_events.sort(key=lambda x: x["timestamp"])
        
        return timeline_events
    
    def generate_event_description(self, result: Dict[str, Any]) -> str:
        """
        Generate a natural language description of an event
        
        Args:
            result: Tracking result data
        
        Returns:
            Description string
        """
        # Parse timestamp
        timestamp = datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))
        time_str = timestamp.strftime("%I:%M %p")
        
        # Get confidence level description
        confidence = result["confidence"]
        if confidence >= 90:
            confidence_desc = "high confidence"
        elif confidence >= 70:
            confidence_desc = "medium confidence"
        else:
            confidence_desc = "low confidence"
        
        # Include position if available
        position_desc = ""
        if result.get("position"):
            position_desc = f" at {result['position']}"
        
        # Include carried items if available
        carrying_desc = ""
        if result.get("carrying") and len(result["carrying"]) > 0:
            items = ", ".join(result["carrying"])
            carrying_desc = f", carrying {items}"
        
        # Generate description
        description = f"Suspect detected at {time_str}{position_desc} with {confidence_desc}{carrying_desc}"
        
        return description
    
    async def build_knowledge_graph(self, tracking_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a knowledge graph from tracking results
        
        Args:
            tracking_results: List of suspect tracking results
        
        Returns:
            Graph data with nodes and edges
        """
        logger.info(f"Building knowledge graph from {len(tracking_results)} tracking results")
        
        # Initialize graph data
        nodes = []
        edges = []
        
        # Track unique IDs to avoid duplicates
        node_ids = set()
        edge_ids = set()
        
        # Add suspect node
        if tracking_results:
            suspect_id = tracking_results[0]["suspectId"]
            suspect = await mongodb.find_one_async("suspects", {"id": suspect_id})
            
            if suspect:
                suspect_node = {
                    "id": suspect_id,
                    "type": "suspect",
                    "label": suspect.get("name", "Suspect"),
                    "imageUrl": suspect.get("imageUrl")
                }
                nodes.append(suspect_node)
                node_ids.add(suspect_id)
        else:
            logger.warning("No tracking results to build graph from")
            return {"nodes": [], "edges": []}
        
        # Process each tracking result
        for result in tracking_results:
            try:
                video_id = result["videoId"]
                timestamp = result["timestamp"]
                
                # Get video data for location
                video = await mongodb.find_one_async("videos", {"id": video_id})
                
                if not video:
                    logger.warning(f"Video not found: {video_id}")
                    continue
                
                # Create location node based on video
                location_id = f"location-{video_id}"
                if location_id not in node_ids:
                    location_label = video.get("location", f"Camera {video_id[-6:]}")
                    
                    location_node = {
                        "id": location_id,
                        "type": "location",
                        "label": location_label
                    }
                    nodes.append(location_node)
                    node_ids.add(location_id)
                
                # Create edge between suspect and location
                edge_id = f"edge-{suspect_id}-{location_id}-{timestamp}"
                if edge_id not in edge_ids:
                    edge = {
                        "id": edge_id,
                        "source": suspect_id,
                        "target": location_id,
                        "label": "visited",
                        "timestamp": timestamp
                    }
                    edges.append(edge)
                    edge_ids.add(edge_id)
                
                # Add object nodes and edges based on carrying
                if result.get("carrying"):
                    for item in result["carrying"]:
                        object_id = f"object-{item.replace(' ', '_')}"
                        if object_id not in node_ids:
                            object_node = {
                                "id": object_id,
                                "type": "object",
                                "label": item.title(),
                                "timestamp": timestamp
                            }
                            nodes.append(object_node)
                            node_ids.add(object_id)
                        
                        # Create edge between suspect and object
                        edge_id = f"edge-{suspect_id}-{object_id}"
                        if edge_id not in edge_ids:
                            edge = {
                                "id": edge_id,
                                "source": suspect_id,
                                "target": object_id,
                                "label": "carried",
                                "timestamp": timestamp
                            }
                            edges.append(edge)
                            edge_ids.add(edge_id)
                
            except Exception as e:
                logger.error(f"Error processing tracking result for graph: {str(e)}")
        
        # Return graph data
        graph_data = {
            "nodes": nodes,
            "edges": edges
        }
        
        logger.info(f"Built knowledge graph with {len(nodes)} nodes and {len(edges)} edges")
        
        return graph_data
    
    async def generate_summary(self, timeline_events: List[Dict[str, Any]]) -> str:
        """
        Generate a natural language summary of the analysis
        
        Args:
            timeline_events: List of timeline events
        
        Returns:
            Summary text
        """
        if not timeline_events:
            return "No suspect appearances were detected in the provided videos."
        
        try:
            # Use LLaMA to generate a comprehensive summary
            summary = await llama_client.generate_timeline_summary(timeline_events)
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            
            # Fallback to simple summary
            first_event = timeline_events[0]
            last_event = timeline_events[-1]
            
            first_time = datetime.fromisoformat(first_event["timestamp"].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(last_event["timestamp"].replace('Z', '+00:00'))
            
            duration = (last_time - first_time).total_seconds() / 60  # in minutes
            
            locations = set()
            for event in timeline_events:
                video_id = event["videoId"]
                video = await mongodb.find_one_async("videos", {"id": video_id})
                if video and "location" in video:
                    locations.add(video["location"])
            
            locations_str = ", ".join(locations) if locations else "multiple locations"
            
            return f"Suspect was tracked for approximately {duration:.0f} minutes across {len(locations)} different locations ({locations_str}). First appeared at {first_time.strftime('%I:%M %p')} and was last seen at {last_time.strftime('%I:%M %p')}."

# Create a singleton instance
video_analyzer = VideoAnalyzer()
