from .base import AIProvider
from openai import AsyncOpenAI
from core.config import settings

class OpenAIProvider(AIProvider):
    """Implementation of AI provider using OpenAI's API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = "gpt-4-turbo"
        
    async def generate_content(self, 
                              prompt: str, 
                              max_tokens: int = 2500,
                              temperature: float = 0.7) -> str:
        """Generate content using OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating content with OpenAI: {e}")
            return f"Error generating content: {str(e)}"