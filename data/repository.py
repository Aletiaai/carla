from google.cloud import firestore
from core.database import Database
from datetime import datetime
from typing import Dict, Any, Optional, List

class BlogRepository:
    """Repository for blog data storage and retrieval"""
    
    def __init__(self):
        db = Database()
        self.collection = db.get_collection('blogs')
        
    async def save_blog(self, blog_data: Dict[str, Any], user_id: str) -> str:
        """Save a blog to the database"""
        blog_doc = {
            **blog_data,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": user_id,
        }
        doc_ref = self.collection.document()
        doc_ref.set(blog_doc)
        return doc_ref.id
        
    async def get_blog(self, blog_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a blog by ID"""
        doc = self.collection.document(blog_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
        
    async def list_blogs(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List blogs for a specific user"""
        query = (
            self.collection
            .where("user_id", "==", user_id)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
