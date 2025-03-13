from .base import AIProvider
import google.generativeai as genai
from core.config import settings

class GeminiProvider(AIProvider):
    """Implementation of AI provider using Google Gemini's API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)  # Configure API key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Initialize Gemini model

    async def generate_content(self,
                              prompt: str,
                              max_tokens: int = 2500,
                              temperature: float = 0.7) -> str:
        """Generate content using Gemini API"""
        try:
            # Gemini doesn't have max_tokens or temperature parameters in the same way as OpenAI.
            # We'll include the length request in the prompt and rely on Gemini's understanding of temperature
            # and token management.

            #Construct a prompt that includes the length request.
            prompt_with_length = f"{prompt}. Please keep the answer under {max_tokens} words."

            response = self.model.generate_content(prompt_with_length, generation_config=genai.types.GenerationConfig(temperature=temperature))
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return f"Error generating content: {str(e)}"