from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment variables
uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # List available databases
    print("\nAvailable databases:")
    for db_name in client.list_database_names():
        print(f" - {db_name}")
    
    # Use the specified database
    db_name = os.getenv("MONGODB_DB", "reconstruct")
    db = client[db_name]
    
    # Create a test collection and insert a document
    test_collection = db.test_collection
    test_document = {"name": "Test Document", "status": "Connected"}
    
    # Insert the document
    result = test_collection.insert_one(test_document)
    print(f"\nInserted document with ID: {result.inserted_id}")
    
    # Find the document
    found_document = test_collection.find_one({"name": "Test Document"})
    print(f"Found document: {found_document}")
    
    # Clean up - delete the test document
    test_collection.delete_one({"name": "Test Document"})
    print("Test document deleted")
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
