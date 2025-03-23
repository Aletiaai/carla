from google.cloud import firestore
from core.database import Database
from datetime import datetime
from typing import Dict, Any, Optional, List

class BlogRepository:
    """Repository for blog data storage and retrieval"""
    
    def __init__(self):
        db = Database()
        self.collection = db.get_collection('blog_posts')
        
    async def save_initial_blog(self, blog_data: Dict[str, Any], user_id: str) -> str:
        """Save a newly generated blog to the database"""
        blog_doc = {
            "title": blog_data.get("title", ""),
            "topic": blog_data.get("topic", ""),
            "audience": blog_data.get("audience", ""),
            "length": blog_data.get("length", 0),
            "raw_content": blog_data.get("raw_content", ""),
            "final_content": "",  # Initially empty
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": user_id,
            "status": "draft"
        }
        doc_ref = self.collection.document()
        doc_ref.set(blog_doc)
        return doc_ref.id
    
    async def update_final_content(self, blog_id: str, final_content: str) -> bool:
        """Update the final_content of a blog post"""
        try:
            doc_ref = self.collection.document(blog_id)
            doc_ref.update({
                "final_content": final_content,
                "updated_at": datetime.now(),
                "status": "edited"
            })
            return True
        except Exception as e:
            print(f"Error updating blog: {str(e)}")
            return False
        

    async def get_blog(self, blog_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a blog by ID"""
        doc = self.collection.document(blog_id).get()
        if doc.exists:
            data = doc.to_dict()
            return {"id": doc.id, **data}
        return None
    
    async def list_blogs(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List blogs for a specific user"""
        query = (
            self.collection
            .where("created_by", "==", user_id)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    