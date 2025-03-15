from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from services.ai.openai_provider import OpenAIProvider
from services.ai.gemini_provider import GeminiProvider
from services.blog_service.generator import BlogGenerator
from data.repository import BlogRepository
from core.config import settings
from pydantic import BaseModel
from services.mailerlite_service import MailerLiteService
from services.wordpress_service import WordPressService


router = APIRouter()

# Dependency for AI provider
def get_ai_provider():
    return GeminiProvider()

# Dependency for blog generator
def get_blog_generator(ai_provider: OpenAIProvider = Depends(get_ai_provider)):
    return BlogGenerator(ai_provider)

# Dependency for blog repository
def get_blog_repository():
    return BlogRepository()

# Request models
class BlogGenerationRequest(BaseModel):
    topic: str
    audience: str
    length: int = settings.DEFAULT_BLOG_LENGTH
    user_id: str = "default_user"  # In a real app, get this from auth

@router.post("/generate")
async def generate_blog(
    request: BlogGenerationRequest,
    blog_generator: BlogGenerator = Depends(get_blog_generator)
):
    """Generate a blog post based on given parameters"""
    try:
        blog_content = await blog_generator.generate_blog(
            request.topic, 
            request.audience, 
            request.length
        )
        return JSONResponse(content={"status": "success", "data": blog_content})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.post("/save")
async def save_blog(
    blog_data: Dict[str, Any] = Body(...),
    user_id: str = Body("default_user"),
    blog_repository: BlogRepository = Depends(get_blog_repository)
):
    """Save a generated blog to the database"""
    try:
        blog_id = await blog_repository.save_blog(blog_data, user_id)
        return JSONResponse(content={"status": "success", "blog_id": blog_id})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.get("/list/{user_id}")
async def list_blogs(
    user_id: str,
    blog_repository: BlogRepository = Depends(get_blog_repository)
):
    """List all blogs for a user"""
    try:
        blogs = await blog_repository.list_blogs(user_id)
        return JSONResponse(content={"status": "success", "data": blogs})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.post("/create-email")
async def create_email_campaign(request: dict):
    content = request.get("content")
    title = request.get("title")
    
    mailerlite = MailerLiteService()
    result = await mailerlite.create_campaign(subject=title, content=content)
    
    return {"status": "success", "campaign": result}

@router.post("/publish-to-wp")
async def publish_to_wordpress(request: dict = Body(...)):
    """Create a draft post in WordPress"""
    try:
        content = request.get("content")
        title = request.get("title")
        
        wordpress = WordPressService()
        result = await wordpress.create_post(title=title, content=content)
        
        return JSONResponse(content={"status": "success", "post": result})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e),"details": error_details}
        )