import logging
import os
import json
import httpx
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# LLaMA API configuration
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY", "")
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "https://api.llama.ai/v1/chat/completions")

async def generate_narration(analysis_data: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    """
    Generate a narration of the analysis using LLaMA
    
    Args:
        analysis_data: Analysis data including timeline and graph
        language: Language code (e.g., 'en', 'es', 'fr')
    
    Returns:
        Dictionary with narration text and URL
    """
    logger.info(f"Generating narration in language: {language}")
    
    # In a real implementation, this would call the LLaMA API
    # For now, we'll simulate the response
    
    # Extract timeline events
    timeline_events = analysis_data.get("timeline", [])
    
    # Generate narration text
    narration_text = ""
    
    if not timeline_events:
        narration_text = "No suspect appearances were detected in the provided videos."
    else:
        # Sort events by timestamp
        sorted_events = sorted(timeline_events, key=lambda x: x['timestamp'])
        
        # Generate introduction
        narration_text = "Analysis of suspect movements across surveillance footage. "
        
        # Generate event descriptions
        for i, event in enumerate(sorted_events):
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            time_str = event_time.strftime("%I:%M %p")
            
            if i == 0:
                narration_text += f"First sighting at {time_str} where the suspect was detected "
            else:
                narration_text += f"Then at {time_str}, the suspect was detected "
            
            narration_text += f"with {event['confidence']:.1f}% confidence. "
        
        # Generate conclusion
        if len(sorted_events) > 1:
            first_event = sorted_events[0]
            last_event = sorted_events[-1]
            
            first_time = datetime.fromisoformat(first_event['timestamp'].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
            
            duration = (last_time - first_time).total_seconds() / 60  # in minutes
            
            narration_text += f"The suspect was tracked for approximately {duration:.0f} minutes across {len(set(e['videoId'] for e in sorted_events))} different camera feeds."
    
    # In a real implementation, we would translate the text if language is not English
    # and convert the text to speech using a TTS API
    
    # For now, we'll simulate a narration URL
    narration_url = f"/narrations/simulated_{datetime.now().timestamp()}.mp3"
    
    return {
        "text": narration_text,
        "url": narration_url,
        "language": language
    }

async def answer_query(query_text: str, analysis_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Answer a natural language query about an analysis using LLaMA
    
    Args:
        query_text: The query text
        analysis_id: Optional ID of the analysis to query
    
    Returns:
        Response with text and optional visual data
    """
    logger.info(f"Answering query: {query_text}")
    
    # In a real implementation, this would call the LLaMA API
    # For now, we'll simulate the response based on query keywords
    
    response_text = ""
    visual_data = None
    
    # Simple keyword-based response generation
    query_lower = query_text.lower()
    
    if "where" in query_lower and "suspect" in query_lower:
        response_text = "Based on the analysis, the suspect was last seen at the east exit at 10:45 AM. They were wearing a dark jacket and carrying a backpack."
        visual_data = {
            "type": "image",
            "url": "/results/simulated_location.jpg"
        }
    elif "when" in query_lower:
        response_text = "The suspect was first detected at 10:15 AM at the north entrance and was last seen at 10:45 AM at the east exit."
        visual_data = {
            "type": "timeline",
            "data": [
                {"time": "10:15 AM", "location": "North Entrance"},
                {"time": "10:22 AM", "location": "Main Hall"},
                {"time": "10:45 AM", "location": "East Exit"}
            ]
        }
    elif "who" in query_lower and "with" in query_lower:
        response_text = "The suspect interacted with a security guard at 10:20 AM and briefly spoke with a receptionist at 10:35 AM."
        visual_data = {
            "type": "graph",
            "url": "/results/simulated_interactions.jpg"
        }
    elif "what" in query_lower and "carrying" in query_lower:
        response_text = "The suspect was carrying a black backpack throughout the footage. At 10:30 AM, they were also seen using a mobile phone."
        visual_data = {
            "type": "image",
            "url": "/results/simulated_objects.jpg"
        }
    else:
        response_text = "I don't have specific information about that query. Please try asking about the suspect's location, timing, interactions, or carried objects."
    
    return {
        "text": response_text,
        "visualData": visual_data
    }

async def call_llama_api(prompt: str, system_message: str = "") -> str:
    """
    Call the LLaMA API with a prompt
    
    Args:
        prompt: The prompt text
        system_message: Optional system message
    
    Returns:
        LLaMA response text
    """
    if not LLAMA_API_KEY:
        logger.warning("LLAMA_API_KEY not set, using simulated response")
        return f"Simulated LLaMA response for: {prompt[:50]}..."
    
    try:
        # Prepare the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLAMA_API_KEY}"
        }
        
        data = {
            "model": "llama-4",
            "messages": [
                {"role": "system", "content": system_message} if system_message else None,
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        # Remove None values
        data["messages"] = [msg for msg in data["messages"] if msg]
        
        # Make the API call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LLAMA_API_URL,
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            # Parse the response
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"LLaMA API error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code}"
    
    except Exception as e:
        logger.error(f"Error calling LLaMA API: {str(e)}")
        return f"Error: {str(e)}"
