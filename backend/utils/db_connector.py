import os
import logging
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio
from bson import ObjectId
from utils.json_encoder import serialize_mongodb_doc

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "reconstruct")

class MongoDBConnector:
    """
    Connector for MongoDB database with both sync and async support
    """
    def __init__(self):
        self.client = None
        self.async_client = None
        self.db = None
        self.async_db = None
        self.connected = False
        self.async_connected = False
    
    def connect(self):
        """
        Connect to MongoDB (synchronous)
        """
        try:
            # Use the recommended connection approach with ServerApi
            self.client = MongoClient(MONGODB_URI, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
            # Verify connection works by pinging the deployment
            self.client.admin.command('ping')
            self.db = self.client[MONGODB_DB]
            self.connected = True
            logger.info(f"Pinged your deployment. Successfully connected to MongoDB: {MONGODB_DB}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            self.connected = False
            
    async def connect_async(self):
        """
        Connect to MongoDB (asynchronous)
        """
        try:
            # Use the recommended connection approach for async client
            # Note: Motor doesn't support ServerApi parameter directly the same way
            # but it will use the same connection string format
            self.async_client = AsyncIOMotorClient(MONGODB_URI)
            # For async client, we'll verify the connection by accessing a database
            await self.async_client.admin.command('ping')
            self.async_db = self.async_client[MONGODB_DB]
            self.async_connected = True
            logger.info(f"Pinged your deployment. Successfully connected to MongoDB (async): {MONGODB_DB}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB (async): {str(e)}")
            self.async_connected = False
    
    def disconnect(self):
        """
        Disconnect from MongoDB (both sync and async)
        """
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Disconnected from MongoDB (sync)")
        
        if self.async_client:
            self.async_client.close()
            self.async_connected = False
            logger.info("Disconnected from MongoDB (async)")
    
    def get_collection(self, collection_name: str):
        """
        Get a collection from the database
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            MongoDB collection
        """
        if not self.connected:
            self.connect()
        
        return self.db[collection_name]
    
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a document into a collection
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
        
        Returns:
            ID of the inserted document
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document: {str(e)}")
            return None
    
    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a document in a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find the document
        
        Returns:
            Found document or None with ObjectId serialized to string
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one(query)
            return serialize_mongodb_doc(result) if result else None
        except Exception as e:
            logger.error(f"Error finding document: {str(e)}")
            return None
    
    def find_many(self, collection_name: str, query: Dict[str, Any]) -> list:
        """
        Find multiple documents in a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find the documents
        
        Returns:
            List of found documents with ObjectId serialized to string
        """
        try:
            collection = self.get_collection(collection_name)
            results = list(collection.find(query))
            return [serialize_mongodb_doc(doc) for doc in results]
        except Exception as e:
            logger.error(f"Error finding documents: {str(e)}")
            return []
    
    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        Update a document in a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find the document
            update: Update to apply
        
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a document from a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find the document
        
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False

    # Async methods for MongoDB operations
    async def get_collection_async(self, collection_name: str):
        """
        Get a collection from the database (async)
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            MongoDB collection
        """
        if not self.async_connected:
            await self.connect_async()
        
        return self.async_db[collection_name]
    
    async def insert_one_async(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a document into a collection (async)
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
        
        Returns:
            ID of the inserted document
        """
        try:
            collection = await self.get_collection_async(collection_name)
            result = await collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document (async): {str(e)}")
            return None
    
    async def find_one_async(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a document in a collection (async)
        
        Args:
            collection_name: Name of the collection
            query: Query to find the document
        
        Returns:
            Found document or None with ObjectId serialized to string
        """
        try:
            collection = await self.get_collection_async(collection_name)
            result = await collection.find_one(query)
            return serialize_mongodb_doc(result) if result else None
        except Exception as e:
            logger.error(f"Error finding document (async): {str(e)}")
            return None
    
    async def find_many_async(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find multiple documents in a collection (async)
        
        Args:
            collection_name: Name of the collection
            query: Query to find the documents
        
        Returns:
            List of found documents with ObjectId serialized to string
        """
        try:
            collection = await self.get_collection_async(collection_name)
            cursor = collection.find(query)
            results = await cursor.to_list(length=100)
            return [serialize_mongodb_doc(doc) for doc in results]
        except Exception as e:
            logger.error(f"Error finding documents (async): {str(e)}")
            return []
    
    async def update_one_async(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        Update a document in a collection (async)
        
        Args:
            collection_name: Name of the collection
            query: Query to find the document
            update: Update to apply
        
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = await self.get_collection_async(collection_name)
            result = await collection.update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document (async): {str(e)}")
            return False
    
    async def delete_one_async(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a document from a collection (async)
        
        Args:
            collection_name: Name of the collection
            query: Query to find the document
        
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = await self.get_collection_async(collection_name)
            result = await collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document (async): {str(e)}")
            return False

# Create a singleton instance
mongodb = MongoDBConnector()
