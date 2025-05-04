import os
import logging
import requests
import json
import base64
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv
from llama_api_client import LlamaAPIClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLaMA API configuration
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")

class LlamaClient:
    """
    Client for interacting with LLaMA API
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or LLAMA_API_KEY
        
        if not self.api_key:
            logger.warning("LLaMA API key not set. Please set LLAMA_API_KEY environment variable.")
        
        # Initialize the official LlamaAPIClient
        self.client = LlamaAPIClient(api_key=self.api_key)
    
    def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using LLaMA API
        
        Args:
            messages: List of message objects with role and content
            model: LLaMA model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            stream: Whether to stream the response
        
        Returns:
            API response as a dictionary
        """
        if not self.api_key:
            raise ValueError("LLaMA API key not set")
        
        try:
            # Call the LLaMA API using the official client
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=top_p,
                stream=stream
            )
            
            # Convert the response to a dictionary for compatibility
            if stream:
                return response
            else:
                # Create a dictionary with the response data
                # Handle the case where response may not have an id attribute
                response_dict = {
                    "choices": [
                        {
                            "message": {
                                "content": response.completion_message.content.text,
                                "role": "assistant"
                            },
                            "index": 0,
                            "finish_reason": "stop"
                        }
                    ],
                    "model": model
                }
                
                # Add id if it exists
                if hasattr(response, 'id'):
                    response_dict["id"] = response.id
                    
                return response_dict
        
        except Exception as e:
            logger.error(f"Error calling LLaMA API: {str(e)}")
            raise
    
    def analyze_image(
        self, 
        image_path: str, 
        prompt: str,
        model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8",
        use_url: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze an image using LLaMA's multimodal capabilities
        
        Args:
            image_path: Path to the image or URL if use_url is True
            prompt: Text prompt describing what to analyze
            model: LLaMA model to use (must support image input)
            use_url: Whether image_path is a URL or a local file path
        
        Returns:
            API response as a dictionary
        """
        try:
            # Prepare the image content
            if use_url:
                # Use image URL directly
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": image_path}
                }
            else:
                # Encode local image as base64
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            
            # Create the message with text and image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        image_content
                    ]
                }
            ]
            
            # Call the LLaMA API using the official client
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1000,
                top_p=1.0
            )
            
            # Convert the response to a dictionary for compatibility
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.completion_message.content.text,
                            "role": "assistant"
                        },
                        "index": 0,
                        "finish_reason": "stop"
                    }
                ],
                "model": model,
                "id": response.id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image with LLaMA: {str(e)}")
            raise
    
    def analyze_frame_for_persons(
        self, 
        frame_path: str,
        model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8",
        use_url: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a video frame to detect and describe persons
        
        Args:
            frame_path: Path to the frame image or URL if use_url is True
            model: LLaMA model to use
            use_url: Whether frame_path is a URL or a local file path
        
        Returns:
            Dictionary with detected persons and their descriptions
        """
        prompt = """
        Analyze this CCTV frame and identify all persons visible.
        For each person, provide:
        1. A bounding box in format [x1, y1, x2, y2]
        2. A brief description including estimated age, gender, clothing
        3. Their position in the scene
        4. Any objects they are carrying
        
        Format your response as a JSON object with an array of detected persons.
        Example:
        {
            "persons": [
                {
                    "id": 1,
                    "bbox": [100, 150, 300, 450],
                    "description": "Male, approximately 30-40 years old, wearing dark jacket and jeans",
                    "position": "Near entrance",
                    "carrying": ["backpack", "phone"]
                }
            ]
        }
        """
        
        try:
            # Use the analyze_image method with JSON mode
            response = self.analyze_image(frame_path, prompt, model, use_url)
            
            # Extract the JSON response from the text
            content = response["choices"][0]["message"]["content"]
            
            # Find JSON in the response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            # Parse the JSON
            persons_data = json.loads(json_str)
            return persons_data
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing LLaMA response: {str(e)}")
            return {"persons": []}
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return {"persons": []}
    
    def compare_person_with_suspect(
        self, 
        person_image_path: str,
        suspect_image_path: str,
        model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8",
        use_urls: bool = False
    ) -> Dict[str, Any]:
        """
        Compare a detected person with a suspect image to determine if they match
        
        Args:
            person_image_path: Path to the person image or URL if use_urls is True
            suspect_image_path: Path to the suspect image or URL if use_urls is True
            model: LLaMA model to use
            use_urls: Whether image paths are URLs or local file paths
        
        Returns:
            Dictionary with match confidence and reasoning
        """
        prompt = """
        Compare these two images carefully. The first image is of a person detected in CCTV footage.
        The second image is of a suspect we're trying to track.
        
        Determine if these are likely the same person based on:
        1. Facial features (if visible)
        2. Body type and posture
        3. Clothing and accessories
        4. Any other distinguishing characteristics
        
        Provide a confidence score (0-100) indicating how likely these are the same person,
        and explain your reasoning.
        
        Format your response as a JSON object:
        {
            "match": true/false,
            "confidence": 85,
            "reasoning": "Detailed explanation of why you think they match or don't match"
        }
        """
        
        try:
            # Prepare the image content
            if use_urls:
                # Use image URLs directly
                person_image_content = {
                    "type": "image_url",
                    "image_url": {"url": person_image_path}
                }
                suspect_image_content = {
                    "type": "image_url",
                    "image_url": {"url": suspect_image_path}
                }
            else:
                # Encode local images as base64
                with open(person_image_path, "rb") as image_file:
                    base64_person = base64.b64encode(image_file.read()).decode('utf-8')
                
                with open(suspect_image_path, "rb") as image_file:
                    base64_suspect = base64.b64encode(image_file.read()).decode('utf-8')
                    
                person_image_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_person}"}
                }
                suspect_image_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_suspect}"}
                }
            
            # Create the message with text and images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        person_image_content,
                        suspect_image_content
                    ]
                }
            ]
            
            # Call the LLaMA API using the official client with JSON mode
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1000,
                top_p=1.0,
                response_format="json_object"
            )
            
            # Extract the JSON response
            content = response.completion_message.content.text
            
            # Parse the JSON
            comparison_data = json.loads(content)
            return comparison_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return {
                "match": False,
                "confidence": 0,
                "reasoning": "Error processing JSON response"
            }
        except Exception as e:
            logger.error(f"Error comparing images: {str(e)}")
            return {
                "match": False,
                "confidence": 0,
                "reasoning": f"Error: {str(e)}"
            }
    
    def extract_person_features(
        self,
        image_path: str,
        model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    ) -> Dict[str, Any]:
        """
        Extract features of a person from an image
        
        Args:
            image_path: Path to the image file
            model: LLaMA model to use
        
        Returns:
            Dictionary with person features
        """
        prompt = """
        Analyze this person in the image and extract key identifying features.
        Focus on:
        1. Facial features (if visible)
        2. Body type and build
        3. Clothing and accessories
        4. Hair style and color
        5. Any distinctive characteristics
        
        Format your response as a JSON object:
        {
            "face": {
                "visible": true/false,
                "features": "Description of facial features"
            },
            "body": {
                "build": "Description of body type",
                "height": "Estimated height (tall/medium/short)",
                "posture": "Description of posture and stance"
            },
            "clothing": {
                "upper": "Description of upper body clothing",
                "lower": "Description of lower body clothing",
                "colors": ["List of dominant colors"]
            },
            "hair": {
                "style": "Description of hair style",
                "color": "Hair color"
            },
            "distinctive": ["List of any distinctive features or characteristics"]
        }
        """
        
        try:
            # Encode local image as base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            image_content = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
            
            # Create the message with text and image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        image_content
                    ]
                }
            ]
            
            # Call the LLaMA API using the official client with JSON mode
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1000,
                top_p=1.0,
                response_format="json_object"
            )
            
            # Extract the JSON response
            content = response.completion_message.content.text
            
            # Parse the JSON
            features = json.loads(content)
            return features
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return {
                "face": {"visible": False, "features": "Unknown"},
                "body": {"build": "Unknown", "height": "Unknown", "posture": "Unknown"},
                "clothing": {"upper": "Unknown", "lower": "Unknown", "colors": []},
                "hair": {"style": "Unknown", "color": "Unknown"},
                "distinctive": ["Unable to extract features"]
            }
        except Exception as e:
            logger.error(f"Error extracting person features: {str(e)}")
            return {
                "face": {"visible": False, "features": "Unknown"},
                "body": {"build": "Unknown", "height": "Unknown", "posture": "Unknown"},
                "clothing": {"upper": "Unknown", "lower": "Unknown", "colors": []},
                "hair": {"style": "Unknown", "color": "Unknown"},
                "distinctive": ["Unable to extract features"]
            }
    
    def generate_timeline_summary(
        self,
        timeline_events: List[Dict[str, Any]],
        model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    ) -> str:
        """
        Generate a natural language summary of timeline events
        
        Args:
            timeline_events: List of timeline events
            model: LLaMA model to use
        
        Returns:
            Summary text
        """
        events_text = json.dumps(timeline_events, indent=2)
        
        prompt = f"""
        Below is a timeline of events showing a suspect's movements across multiple CCTV cameras.
        Each event includes the timestamp, location, and a description of what was observed.
        
        {events_text}
        
        Please provide a comprehensive summary of the suspect's movements and activities.
        Include:
        1. The chronological flow of movement
        2. Key locations visited
        3. Any notable interactions or behaviors
        4. Patterns or anomalies in the movement
        
        Write this as a detailed investigative narrative that would be helpful for law enforcement.
        """
        
        try:
            # Call the LLaMA API using the official client
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_completion_tokens=2000,
                top_p=1.0
            )
            
            # Extract the summary text
            return response.completion_message.content.text
            
        except Exception as e:
            logger.error(f"Error generating timeline summary: {str(e)}")
            return f"Error generating summary: {str(e)}"

# Create a singleton instance
llama_client = LlamaClient()
