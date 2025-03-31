from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from data.repository import BlogRepository
from core.config import settings
from pydantic import BaseModel
import traceback
from . import dependencies
import re
from services.blog_service.generator import BlogGenerator

router = APIRouter()

# Request models
class BlogGenerationRequest(BaseModel):
    topic: str
    audience: str
    length: int = settings.DEFAULT_BLOG_LENGTH
    user_id: str = "default_user"  # In a real app, get this from auth
    personal_story: str = ""

class BlogUpdateRequest(BaseModel):
    blog_id: str
    final_content: str
    user_id: str = "default_user"  # In a real app, get this from auth
    post_id: int = None

@router.post("/generate")
async def generate_blog(
    request: BlogGenerationRequest,
    blog_generator: BlogGenerator = Depends(dependencies.get_blog_generator),
    blog_repository: BlogRepository = Depends(dependencies.get_blog_repository)
):
    """Generate a blog post based on given parameters and save initial version"""
    try:
        # Generate blog content
        blog_content = await blog_generator.generate_blog(
            request.topic,
            request.audience,
            request.length,
            request.personal_story
        )
        
        # Prepare data for storage
        blog_data = {
            "title": blog_content.get("title", ""),
            "topic": request.topic,
            "audience": request.audience,
            "length": request.length,
            "raw_content": blog_content.get("raw_content", "")
        }
        
        # Save initial blog post
        blog_id = await blog_repository.save_initial_blog(blog_data, request.user_id)
        
        # Return data with the blog ID
        return JSONResponse(content={
            "status": "success", 
            "data": {**blog_content, "id": blog_id}
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.post("/save")
async def save_blog(
    request: BlogUpdateRequest,
    blog_repository: BlogRepository = Depends(dependencies.get_blog_repository)
):
    """Save the final edited content of a blog"""
    try:
        # Log received data for debugging
        print(f"Received save request for blog_id: {request.blog_id}")
        print(f"Content length: {len(request.final_content)}")
        
        # Update the blog content
        success = await blog_repository.update_final_content(
            request.blog_id,
            request.final_content,
            request.post_id
        )
        
        if success:
            return JSONResponse(content={"status": "success", "blog_id": request.blog_id})
        else:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Blog not found or update failed"}
            )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error saving blog: {str(e)}")
        print(error_details)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
    
@router.post("/email-campaign")
async def create_email_campaign(request: dict, mailerlite = Depends(dependencies.get_mailerlite_service), blog_repository = Depends(dependencies.get_blog_repository)):
    try:
        raw_content = request.get("content")
        blog_id = request.get("blog_id")  # Get blog_id from request

        if not blog_id:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "blog_id is required"}
            )
        # Get the blog post from Firestore
        blog_post = await blog_repository.get_blog_post(blog_id)
        if not blog_post:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"Blog post with id {blog_id} not found"}
            )
        post_id = blog_post.get("post_id")
        if not post_id:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"post_id not found for blog post with id {blog_id}"}
            )
        
        result = await mailerlite.create_campaign(content=raw_content, post_id=post_id)
        return {"status": "success", "campaign": result}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating email campaign: {str(e)}")
        print(error_details)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error", "details": str(e)}
        )
        


@router.post("/draft-to-wp")
async def publish_to_wordpress(request: dict = Body(...), wordpress = Depends(dependencies.get_wordpress_service), blog_repository: BlogRepository = Depends(dependencies.get_blog_repository)):
    """Create a draft post in WordPress"""
    try:
        content = request.get("content")
        title = request.get("title")
        blog_id = request.get("blog_id")
        final_content = request.get("final_content")
        post_id = request.get("post_id")

        print(f"Received title: {title}")
        print(f"Received blog_id: {blog_id}")
        print(f"Received post_id: {post_id}")    

        if not content or not title or not blog_id:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Content, title and blog_id are required"}
            )
        
        # First save to database if final_content is provided
        if final_content:
            print(f"Saving to database first, content length: {len(final_content)}")
            save_success = await blog_repository.update_final_content(
                blog_id,
                final_content,
                post_id
            )
            if not save_success:
                return JSONResponse(
                    status_code=404,
                    content={"status": "error", "message": "Blog not found or database save failed"}
                )
        # Then publish to WordPress
        result = await wordpress.create_post(title=title, content=content)
        post_id = result['id'] #get the post id from wordpress.
        print(f"Received post_id: {post_id}")

        # Retrieve the post link
        post_link = await dependencies.get_wordpress_post_link(post_id)
        print(f"Received post_link: {post_link}")

        # Update the firestore document with the post id
        # Note: If final_content was already saved above, this will just update the post_id
        await blog_repository.update_final_content(
            blog_id=blog_id,
            final_content = final_content or "",
            post_id = post_id) #update the firestore document with the post id.

        return JSONResponse(content={
            "status": "success",
            "message": "Content saved to database and published to WordPress",
            "post": result,
            "post_link": post_link
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"WordPress error: {str(e)}") # added logging before the exception.
        print(error_details)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e),"details": error_details}
        )