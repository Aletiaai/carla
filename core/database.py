from google.cloud import firestore
from core.config import settings

class Database:
    """Database connection manager"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.client = firestore.Client(
            )
        return cls._instance
    
    def get_collection(self, collection_name: str):
        """Get a reference to a Firestore collection"""
        return self.client.collection(collection_name)