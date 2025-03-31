from fastapi import Depends
from services.ai.openai_provider import OpenAIProvider
from services.ai.gemini_provider import GeminiProvider
from data.repository import BlogRepository
from core.config import settings
from services.blog_service.generator import BlogGenerator
from services.mailerlite_service.campaign_creator import MailerLiteService
from services.wordpress_service.draft_creator import WordPressService
import aiohttp
import asyncio
from core.config import settings

async def get_wordpress_post_link(post_id: int, max_retries=3, retry_delay=2, timeout=10):
        """Retrieves the link of a WordPress post by its ID with retry logic and timeout."""
        api_url = settings.WP_API_URL
        username = settings.WP_USERNAME
        password = settings.WP_PASSWORD
        
        for attempt in range(max_retries):
            try:
                # Create a new session for each attempt with explicit timeout settings
                timeout_config = aiohttp.ClientTimeout(total=timeout)
                async with aiohttp.ClientSession(timeout=timeout_config) as session:
                    get_link_url = f"{api_url}/wp-json/wp/v2/posts/{post_id}"
                    # Add headers to maintain connection
                    headers = {
                        'Connection': 'keep-alive',
                        'User-Agent': 'Carla/1.0'
                    }
                    async with session.get(get_link_url, auth=aiohttp.BasicAuth(username, password), headers=headers,ssl = False) as link_response:
                        if link_response.status == 200:
                            post_data = await link_response.json()
                            return post_data['link']
                        else:
                            response_text = await link_response.text()
                            print(f"Failed to get post link (Status {link_response.status}): {response_text}")
                            raise Exception(f"Failed to get the post link: {response_text}")
            except aiohttp.client_exceptions.ServerDisconnectedError as e:
                print(f"Attempt {attempt + 1} failed: Server disconnected. Retrying in {retry_delay} seconds.")
                if attempt == max_retries - 1:
                    raise Exception(f"Server disconnected after {max_retries} attempts") from e
                await asyncio.sleep(retry_delay)
            except aiohttp.client_exceptions.ClientConnectorError as e:
                print(f"Attempt {attempt + 1} failed: Connection error: {str(e)}. Retrying in {retry_delay} seconds.")
                if attempt == max_retries - 1:
                    raise Exception(f"Connection error after {max_retries} attempts") from e
                await asyncio.sleep(retry_delay)
            except aiohttp.client_exceptions.ClientTimeout as e:
                print(f"Attempt {attempt + 1} failed: Request timed out. Retrying in {retry_delay} seconds.")
                if attempt == max_retries - 1:
                    raise Exception(f"Request timed out after {max_retries} attempts") from e
                await asyncio.sleep(retry_delay)
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds.")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(retry_delay)
    
        raise Exception("Max retries exceeded without successful response")

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