import os
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "reconstruct_embeddings")

class VectorStore:
    """
    Vector store for embeddings using Qdrant
    """
    def __init__(self):
        self.client = None
        self.connected = False
        self.embedding_size = 128  # Default embedding size
    
    def connect(self):
        """
        Connect to Qdrant
        """
        try:
            self.client = QdrantClient(url=QDRANT_URL)
            self.connected = True
            logger.info(f"Connected to Qdrant: {QDRANT_URL}")
            
            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if QDRANT_COLLECTION not in collection_names:
                self.client.create_collection(
                    collection_name=QDRANT_COLLECTION,
                    vectors_config=models.VectorParams(
                        size=self.embedding_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {QDRANT_COLLECTION}")
            
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {str(e)}")
            self.connected = False
    
    def store_embedding(self, embedding: np.ndarray, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Store an embedding in Qdrant
        
        Args:
            embedding: Embedding vector
            metadata: Metadata for the embedding
        
        Returns:
            ID of the stored embedding
        """
        if not self.connected:
            self.connect()
        
        try:
            # Generate a unique ID
            import uuid
            point_id = str(uuid.uuid4())
            
            # Store the embedding
            self.client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding.tolist(),
                        payload=metadata
                    )
                ]
            )
            
            logger.info(f"Stored embedding with ID: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}")
            return None
    
    def search_similar(self, embedding: np.ndarray, limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in Qdrant
        
        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)
        
        Returns:
            List of similar embeddings with metadata
        """
        if not self.connected:
            self.connect()
        
        try:
            # Search for similar embeddings
            results = self.client.search(
                collection_name=QDRANT_COLLECTION,
                query_vector=embedding.tolist(),
                limit=limit,
                score_threshold=threshold
            )
            
            # Extract results
            similar_embeddings = []
            for result in results:
                similar_embeddings.append({
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.payload
                })
            
            logger.info(f"Found {len(similar_embeddings)} similar embeddings")
            return similar_embeddings
            
        except Exception as e:
            logger.error(f"Error searching for similar embeddings: {str(e)}")
            return []
    
    def delete_embedding(self, embedding_id: str) -> bool:
        """
        Delete an embedding from Qdrant
        
        Args:
            embedding_id: ID of the embedding to delete
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            self.connect()
        
        try:
            # Delete the embedding
            self.client.delete(
                collection_name=QDRANT_COLLECTION,
                points_selector=models.PointIdsList(
                    points=[embedding_id]
                )
            )
            
            logger.info(f"Deleted embedding with ID: {embedding_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting embedding: {str(e)}")
            return False

# Create a singleton instance
vector_store = VectorStore()
