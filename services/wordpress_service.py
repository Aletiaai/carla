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
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/wp-json/wp/v2/posts",
                    json={
                        "title": title,
                        "content": content,
                        "status": "draft"
                    },
                    auth=auth
                ) as response:
                    response_data = await response.json()
                    if response.status == 201:
                        return response_data
                    else:
                        response_text = await response.text()
                        raise Exception(
                            f"Failed to create WordPress post: {response_data}, response text: {response_text}"
                        )
        except aiohttp.ClientError as e:
            raise Exception(f"Aiohttp error: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")