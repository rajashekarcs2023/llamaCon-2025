import asyncio
import os
import logging
import json
import base64
import cv2
import tempfile
from dotenv import load_dotenv
from utils.groq_client import groq_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def test_direct_comparison():
    """
    Test direct image comparison between suspect and frame crops
    """
    print("=== Testing Direct Image Comparison ===")
    
    # Check if API keys are set
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("GROQ_API_KEY not set in .env file")
        return
    
    print("API keys found in .env file")
    
    # Create output directory for debug images
    debug_dir = "debug_images"
    os.makedirs(debug_dir, exist_ok=True)
    
    # Find suspect image
    suspect_image_path = "data/suspects/test_suspect_001.jpg"
    if not os.path.exists(suspect_image_path):
        print(f"Suspect image not found: {suspect_image_path}")
        return
    
    print(f"Using suspect image: {suspect_image_path}")
    
    # Save a copy to debug directory
    import shutil
    shutil.copy(suspect_image_path, os.path.join(debug_dir, "suspect.jpg"))
    
    # Find frames directory
    frames_dir = "data/videos/frames/test_video_001"
    if not os.path.exists(frames_dir):
        print(f"Frames directory not found: {frames_dir}")
        return
    
    # Get all frame images
    frame_paths = [os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.jpg')]
    frame_paths.sort()
    
    print(f"Found {len(frame_paths)} frames")
    
    # Process each frame to extract persons
    for i, frame_path in enumerate(frame_paths):
        print(f"\nProcessing frame {i+1}/{len(frame_paths)}: {frame_path}")
        
        # Use Groq to detect persons in the frame
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
            # Use Groq to analyze the frame
            result = groq_client.process_video_frame(frame_path)
            persons = result.get("persons", [])
            
            print(f"Detected {len(persons)} persons in frame")
            
            # Process each detected person
            for j, person in enumerate(persons):
                bbox = person.get("bbox")
                if not bbox or len(bbox) != 4:
                    continue
                
                # Read the frame image
                frame_img = cv2.imread(frame_path)
                if frame_img is None:
                    continue
                
                # Ensure bbox is within frame boundaries
                height, width = frame_img.shape[:2]
                x1 = max(0, int(bbox[0]))
                y1 = max(0, int(bbox[1]))
                x2 = min(width, int(bbox[2]))
                y2 = min(height, int(bbox[3]))
                
                # Skip if invalid bbox
                if x1 >= x2 or y1 >= y2:
                    continue
                
                # Crop person from frame
                person_img = frame_img[y1:y2, x1:x2]
                
                # Skip if crop resulted in empty image
                if person_img.size == 0:
                    continue
                
                # Save cropped image to debug directory
                person_img_path = os.path.join(debug_dir, f"frame_{i:02d}_person_{j:02d}.jpg")
                cv2.imwrite(person_img_path, person_img)
                
                # Compare with suspect using Groq
                comparison_prompt = """
                Compare these two images carefully. The first image is of a suspect we're trying to track.
                The second image is from a CCTV camera and shows a person.
                
                Even if the images are partial, blurry, or the person is not fully visible, try to determine if they could possibly be the same person.
                Consider any similarities in:
                1. Any visible facial features (even if partially visible)
                2. Body type, build, and posture
                3. Clothing style, color, and accessories
                4. Hair style and color (if visible)
                5. General appearance and demeanor
                
                Be lenient in your assessment - if there's any reasonable possibility they could be the same person, consider it a potential match.
                
                Provide a confidence score (0-100) indicating how likely these are the same person.
                Even if you're not highly confident, if there are some similarities, assign at least a moderate score (30-50).
                
                Format your response as a JSON object:
                {
                    "match": true/false,
                    "confidence": 85,
                    "reasoning": "Detailed explanation of why you think they might match or don't match"
                }
                """
                
                # Use Groq for comparison
                comparison_result = groq_client.compare_images(
                    suspect_image_path,
                    person_img_path,
                    comparison_prompt,
                    use_urls=False
                )
                
                # Extract comparison data
                try:
                    content = comparison_result["choices"][0]["message"]["content"]
                    
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
                    comparison_data = json.loads(json_str)
                    
                    # Save comparison result
                    with open(os.path.join(debug_dir, f"frame_{i:02d}_person_{j:02d}_comparison.json"), "w") as f:
                        json.dump(comparison_data, f, indent=2)
                    
                    # Print result
                    match = comparison_data.get("match", False)
                    confidence = comparison_data.get("confidence", 0)
                    print(f"  Person {j}: Match={match}, Confidence={confidence}")
                    
                    if match and confidence >= 30:
                        print(f"  POTENTIAL MATCH FOUND! Frame {i}, Person {j}")
                        print(f"  Reasoning: {comparison_data.get('reasoning', '')}")
                
                except Exception as e:
                    print(f"  Error parsing comparison result: {str(e)}")
        
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
    
    print("\n=== Test Complete ===")
    print(f"Debug images and comparison results saved to {debug_dir}")

if __name__ == "__main__":
    asyncio.run(test_direct_comparison())
