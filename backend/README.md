# Reconstruct Backend API

This is the backend API for the Reconstruct project - an AI-powered system for tracking suspects across multiple CCTV feeds.

## Features

- Video upload and processing
- Suspect image upload and tracking
- Timeline generation of suspect movements
- Knowledge graph of interactions
- LLaMA-powered narration and querying
- Multilingual support

## Setup and Installation

1. Make sure you have Python 3.9+ installed
2. All dependencies are installed in the `llamaenv` virtual environment

### Environment Setup

The backend uses environment variables for configuration. Copy the `.env.example` file to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Then edit the `.env` file with your specific configuration.

### Running the Backend

Activate the virtual environment and run the FastAPI server:

```bash
source ../llamaenv/bin/activate
python run.py
```

The API will be available at http://localhost:8000

## API Endpoints

### Video Endpoints

- `POST /upload_video` - Upload a CCTV video file with metadata
- `GET /videos` - Get all uploaded videos
- `GET /videos/{video_id}` - Get a specific video by ID

### Suspect Endpoints

- `POST /upload_suspect` - Upload a suspect image with optional metadata
- `GET /suspects` - Get all uploaded suspects
- `GET /suspects/{suspect_id}` - Get a specific suspect by ID

### Analysis Endpoints

- `POST /analyze` - Run suspect tracking analysis across selected videos
- `GET /analysis/{analysis_id}` - Get analysis results by ID
- `GET /timeline/{analysis_id}` - Get timeline for a specific analysis
- `GET /graph/{analysis_id}` - Get knowledge graph for a specific analysis
- `GET /narrate/{analysis_id}` - Get narration for a specific analysis
- `GET /summary/{analysis_id}` - Get a detailed summary of the analysis

### Query Endpoints

- `POST /query` - Submit a natural language query about an analysis

## Integration with Frontend

The backend API is designed to integrate seamlessly with the existing frontend. Update the API service in the frontend to point to this backend instead of using mock data.

In your frontend's `api-service.ts` file, update the API calls to point to the backend server:

```typescript
// Example for the uploadVideo function
export async function uploadVideo(file: File, metadata: Partial<VideoFeed>): Promise<VideoFeed> {
  const formData = new FormData();
  formData.append('file', file);
  
  if (metadata.name) formData.append('name', metadata.name);
  if (metadata.location) formData.append('location', metadata.location);
  if (metadata.timestamp) formData.append('timestamp', metadata.timestamp);
  
  const response = await fetch('http://localhost:8000/upload_video', {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error('Failed to upload video');
  }
  
  return response.json();
}
```

## Data Storage

The backend currently uses in-memory storage for development. For production, it's designed to be easily switched to MongoDB for metadata and Qdrant for vector embeddings.

## LLaMA Integration

The backend integrates with LLaMA 4 for:
- Generating natural language summaries of suspect movements
- Creating multilingual narrations
- Answering natural language queries about the analysis

Make sure to set your LLaMA API key in the `.env` file to enable these features.
