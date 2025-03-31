from google.cloud import firestore
from core.database import Database
from datetime import datetime
from typing import Dict, Any, Optional, List

class BlogRepository:
    """Repository for blog data storage and retrieval"""
    
    def __init__(self):
        db = Database()
        self.collection = db.get_collection('blog_posts')

    async def get_blog_post(self, blog_id: str) -> Optional[Dict[str, Any]]:
        """Get a single blog post by its ID"""
        try:
            doc_ref = self.collection.document(blog_id)
            doc = doc_ref.get()
            if doc.exists:
                blog_post = doc.to_dict()
                # Add the document ID to the returned data
                blog_post['id'] = doc.id
                return blog_post
            return None
        except Exception as e:
            print(f"Error retrieving blog post: {str(e)}")
            return None
        
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
            "status": "draft",
            "post_id": None #initially empty since it hasn't been send to wp
        }
        doc_ref = self.collection.document()
        doc_ref.set(blog_doc)
        return doc_ref.id
    
    async def update_final_content(self, blog_id: str, final_content: str, post_id: int) -> bool:
        """Update the final_content of a blog post"""
        try:
            doc_ref = self.collection.document(blog_id)
            doc_ref.update({
                "final_content": final_content,
                "updated_at": datetime.now(),
                "status": "edited",
                "post_id": post_id 
            })
            return True
        except Exception as e:
            print(f"Error updating blog: {str(e)}")
            return False

    