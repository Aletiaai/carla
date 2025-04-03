from .base import AIProvider
import google.generativeai as genai
from core.config import settings

class GeminiProvider(AIProvider):
    """Implementation of AI provider using Google Gemini's API"""

    def __init__(self):
       
        # Clear any existing configuration
        if hasattr(genai, "_configured"):
            delattr(genai, "_configured")

        # If API key is available, use it instead of service account
        api_key = settings.GEMINI_API_KEY
        
        if api_key and api_key.strip() and api_key != "":
            # Configure with API key
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
            print("Successfully initialized GeminiProvider with API key")
        else:
            # Fall back to service account
            try:
                genai.configure(
                    transport='grpc',
                    client_options={
                        'api_endpoint': 'generativelanguage.googleapis.com',
                        'quota_project_id': 'carla-452511'
                    }
                )
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
                print("Successfully initialized GeminiProvider with service account from environment variable")
            except Exception as e:
                print(f"Error initializing GeminiProvider: {e}")
                raise

    async def generate_content(self,
                             prompt: str,
                             max_tokens: int = 2500,
                             temperature: float = 0.7) -> str:
        """Generate content using Gemini API"""
        try:
            prompt_with_length = f"{prompt}. Please keep the answer under {max_tokens} words."

            response = self.model.generate_content(prompt_with_length,
                       generation_config=genai.types.GenerationConfig(temperature=temperature))
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return f"Error generating content: {str(e)}"