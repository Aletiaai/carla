# services/wordpress_service.py
import aiohttp
from core.config import settings

class WordPressService:
    def __init__(self):
        self.api_url = settings.WP_API_URL
        self.username = settings.WP_USERNAME
        self.password = settings.WP_PASSWORD
        
    async def create_post(self, title, content):
        """Create a draft post in WordPress"""
        auth = aiohttp.BasicAuth(self.username, self.password)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/posts",
                json={
                    "title": title,
                    "content": content,
                    "status": "draft"
                },
                auth=auth
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create WordPress post: {error_text}")