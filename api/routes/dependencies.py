from fastapi import Depends
from services.ai.openai_provider import OpenAIProvider
from services.ai.gemini_provider import GeminiProvider
from data.repository import BlogRepository
from core.config import settings
from services.blog_service.generator import BlogGenerator
from services.mailerlite_service.campaign_creator import MailerLiteService
from services.wordpress_service.draft_creator import WordPressService




# Dependency for AI provider
def get_ai_provider():
    return GeminiProvider()

# Dependency for blog generator
def get_blog_generator(ai_provider = Depends(get_ai_provider)):
    return BlogGenerator(ai_provider)

# Dependency for blog repository
def get_blog_repository():
    return BlogRepository()

# Mailerlite service dependency
def get_mailerlite_service():
    return MailerLiteService()

# Wordpress service dependency
def get_wordpress_service():
    return WordPressService()