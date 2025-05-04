import os
import logging
import json
import base64
from typing import Dict, List, Any, Optional, Union
import requests
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class GroqClient:
    """
    Client for interacting with Groq API for fast inference
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        
        if not self.api_key:
            logger.warning("Groq API key not set. Please set GROQ_API_KEY environment variable.")
        
        # Initialize the official Groq client
        self.client = Groq(api_key=self.api_key)
    
    def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using Groq API
        
        Args:
            messages: List of message objects with role and content
            model: Model to use
            temperature: Sampling temperature (0-1)
            top_p: Top-p sampling parameter
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
        
        Returns:
            API response as a dictionary
        """
        if not self.api_key:
            raise ValueError("Groq API key not set")
        
        try:
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
                return {
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": "assistant"
                            },
                            "index": 0,
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "model": response.model,
                    "id": response.id
                }
        
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise
    
    def analyze_image(
        self, 
        image_path: str, 
        prompt: str,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        use_url: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze an image using Groq's multimodal capabilities
        
        Args:
            image_path: Path to the image or URL if use_url is True
            prompt: Text prompt describing what to analyze
            model: Model to use (must support image input)
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
            
            # Call the Groq API using the official client
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
                            "content": response.choices[0].message.content,
                            "role": "assistant"
                        },
                        "index": 0,
                        "finish_reason": response.choices[0].finish_reason
                    }
                ],
                "model": response.model,
                "id": response.id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image with Groq: {str(e)}")
            raise
    
    def process_video_frame(
        self, 
        frame_path: str,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        use_url: bool = False
    ) -> Dict[str, Any]:
        """
        Process a video frame to detect persons and objects
        
        Args:
            frame_path: Path to the frame image or URL if use_url is True
            model: Model to use
            use_url: Whether frame_path is a URL or a local file path
        
        Returns:
            Dictionary with detected persons and objects
        """
        prompt = """
        Analyze this CCTV frame and identify ALL persons visible, even if they're partially visible or at a distance.
        Be thorough and make sure to identify EVERY person in the frame, no matter how small or partially visible they might be.
        
        For each person, provide:
        1. A bounding box in format [x1, y1, x2, y2] that encompasses their FULL BODY from head to toe, not just their face or upper body
        2. A detailed description including estimated age, gender, clothing (top and bottom), and any distinctive features
        3. Their precise position in the scene (e.g., "left side near door", "center background")
        4. Any objects they are carrying or interacting with
        5. Their posture or activity (standing, walking, sitting, etc.)
        
        IMPORTANT: Make sure the bounding boxes are accurate and include the ENTIRE person from head to toe with some margin.
        If a person is partially out of frame, extend the bounding box to the edge of the frame.
        
        Format your response as a JSON object with an array of detected persons.
        Example:
        {
            "persons": [
                {
                    "id": 1,
                    "bbox": [100, 150, 300, 450],
                    "description": "Male, approximately 30-40 years old, wearing dark jacket and blue jeans, athletic build",
                    "position": "Near entrance on the left side",
                    "carrying": ["backpack", "phone"],
                    "posture": "Standing, facing the camera"
                },
                {
                    "id": 2,
                    "bbox": [400, 200, 500, 600],
                    "description": "Female, approximately 20-30 years old, wearing red top and black pants, slim build",
                    "position": "Center of frame, near the counter",
                    "carrying": ["handbag"],
                    "posture": "Walking towards the right"
                }
            ]
        }
        """
        
        try:
            # Prepare the image content
            if use_url:
                # Use image URL directly
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": frame_path}
                }
            else:
                # Encode local image as base64
                with open(frame_path, "rb") as image_file:
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
            
            # Call the Groq API using the official client with JSON mode
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1000,
                top_p=1.0,
                response_format={"type": "json_object"}
            )
            
            # Extract the JSON response
            content = response.choices[0].message.content
            
            # Parse the JSON
            persons_data = json.loads(content)
            return persons_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return {"persons": []}
        except Exception as e:
            logger.error(f"Error processing video frame: {str(e)}")
            return {"persons": []}
    
    def generate_text(self, prompt: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct") -> Dict[str, Any]:
        """
        Generate text using Groq's API
        
        Args:
            prompt: Text prompt for generation
            model: Model to use
        
        Returns:
            Generated text response
        """
        try:
            # Create the message with text only
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Call the Groq API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=2000,  # Longer for narrative generation
                top_p=1.0
            )
            
            # Convert to dictionary for consistent interface
            response_dict = {
                "choices": [
                    {
                        "message": {
                            "content": response.choices[0].message.content
                        }
                    }
                ]
            }
            
            return response_dict
            
        except Exception as e:
            logger.error(f"Error generating text with Groq: {str(e)}")
            return {"choices": [{"message": {"content": ""}}]}
    
    def compare_images(
        self, 
        image1_path: str,
        image2_path: str,
        prompt: str,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        use_urls: bool = False
    ) -> Dict[str, Any]:
        """
        Compare two images and analyze their similarities/differences
        
        Args:
            image1_path: Path to the first image or URL if use_urls is True
            image2_path: Path to the second image or URL if use_urls is True
            prompt: Text prompt describing what to analyze
            model: Model to use
            use_urls: Whether image paths are URLs or local file paths
        
        Returns:
            API response as a dictionary
        """
        try:
            # Prepare image content
            if use_urls:
                # Use image URLs directly
                image1_content = {
                    "type": "image_url",
                    "image_url": {"url": image1_path}
                }
                image2_content = {
                    "type": "image_url",
                    "image_url": {"url": image2_path}
                }
            else:
                # Encode local images as base64
                with open(image1_path, "rb") as image_file:
                    base64_image1 = base64.b64encode(image_file.read()).decode('utf-8')
                
                with open(image2_path, "rb") as image_file:
                    base64_image2 = base64.b64encode(image_file.read()).decode('utf-8')
                    
                image1_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image1}"}
                }
                image2_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image2}"}
                }
            
            # Create the message with text and images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        image1_content,
                        image2_content
                    ]
                }
            ]
            
            # Call the Groq API using the official client with JSON mode
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1000,
                top_p=1.0,
                response_format={"type": "json_object"}
            )
            
            # Convert the response to a dictionary for compatibility
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.choices[0].message.content,
                            "role": "assistant"
                        },
                        "index": 0,
                        "finish_reason": response.choices[0].finish_reason
                    }
                ],
                "model": response.model,
                "id": response.id
            }
            
        except Exception as e:
            logger.error(f"Error comparing images: {str(e)}")
            raise

# Create a singleton instance
groq_client = GroqClient()
