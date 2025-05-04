import requests
import json
import time

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_environment_processing():
    """Test the environment processing API"""
    print("Testing environment processing API...")
    
    # Get all videos
    response = requests.get(f"{BASE_URL}/videos")
    if response.status_code != 200:
        print(f"Error getting videos: {response.text}")
        return
    
    videos = response.json()
    print(f"Found {len(videos)} videos")
    
    # Find environment video
    env_video = None
    for video in videos:
        if video.get("isEnvironment", False):
            env_video = video
            break
    
    if not env_video:
        print("No environment video found")
        return
    
    print(f"Found environment video: {env_video['id']}")
    
    # Process environment video
    response = requests.post(
        f"{BASE_URL}/environment/process",
        json={"videoId": env_video['id']}
    )
    
    if response.status_code != 200:
        print(f"Error processing environment video: {response.text}")
        return
    
    env_context = response.json()
    print(f"Environment context created with ID: {env_context['id']}")
    
    # Wait for processing to complete
    print("Waiting for environment processing to complete...")
    time.sleep(5)
    
    # Test analysis with environment context
    # Get a non-environment video
    non_env_video = None
    for video in videos:
        if not video.get("isEnvironment", False):
            non_env_video = video
            break
    
    if not non_env_video:
        print("No non-environment video found")
        return
    
    print(f"Found non-environment video: {non_env_video['id']}")
    
    # Run analysis with environment context
    response = requests.post(
        f"{BASE_URL}/analysis/general",
        json={
            "videoId": non_env_video['id'],
            "includeEnvironment": True
        }
    )
    
    if response.status_code != 200:
        print(f"Error running analysis: {response.text}")
        return
    
    analysis = response.json()
    print(f"Analysis created with ID: {analysis['id']}")
    
    # Wait for analysis to complete
    print("Waiting for analysis to complete...")
    time.sleep(10)
    
    # Get analysis summary
    response = requests.get(f"{BASE_URL}/summary/{analysis['id']}")
    
    if response.status_code != 200:
        print(f"Error getting summary: {response.text}")
        return
    
    summary = response.json()
    print(f"Summary: {summary.get('summary', 'No summary available')}")

if __name__ == "__main__":
    test_environment_processing()
