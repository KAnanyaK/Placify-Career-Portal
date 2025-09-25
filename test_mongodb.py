import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def test_mongodb_connection():
    try:
        connection_string = os.getenv("MONGODB_URI")
        client = MongoClient(connection_string)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB Atlas connected successfully!")
        
        # Test insert
        db = client.placement_portal
        test_collection = db.test_collection
        result = test_collection.insert_one({"test": "Hello MongoDB!"})
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Cleanup
        test_collection.delete_one({"test": "Hello MongoDB!"})
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
