from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from data.repository import BlogRepository
from core.config import settings
from pydantic import BaseModel
from services.mailerlite_service.campaign_creator import extract_title_from_content, extract_campaign_content
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
            request.final_content
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
    
@router.post("/create-email")
async def create_email_campaign(request: dict, mailerlite = Depends(dependencies.get_mailerlite_service)):
    try:
        content = request.get("content")
        title = extract_title_from_content(content)
        campaign_content = extract_campaign_content(content)
        print(title)
        print(campaign_content)

        result = await mailerlite.create_campaign(subject=title, content=campaign_content)
        return {"status": "success", "campaign": result}
    except Exception as e:
        print(f"Error creating email campaign: {str(e)}")
        return {"status": "error", "message": "Internal server error", "details": str(e)}
        


@router.post("/publish-to-wp")
async def publish_to_wordpress(request: dict = Body(...), wordpress = Depends(dependencies.get_wordpress_service)):
    """Create a draft post in WordPress"""
    try:
        content = request.get("content")
        title = request.get("title")

        if not content or not title:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Content and title are required"}
            )
        result = await wordpress.create_post(title=title, content=content)
        
        return JSONResponse(content={"status": "success", "post": result})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"WordPress error: {str(e)}")
        print(error_details)   
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e),"details": error_details}
        )