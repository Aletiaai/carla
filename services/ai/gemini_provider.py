from .base import AIProvider
from google.oauth2 import service_account  #For using service account
import google.generativeai as genai
from core.config import settings
import os                                   #For using service account

class GeminiProvider(AIProvider):
    """Implementation of AI provider using Google Gemini's API"""

    def __init__(self, service_account_path: str = None):
       
        # Clear any existing configuration
        if hasattr(genai, "_configured"):
            delattr(genai, "_configured")

        # If API key is available, use it instead of service account
        api_key = settings.GEMINI_API_KEY
        
        if api_key and api_key.strip() and api_key != "":
            # Configure with API key
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("Successfully initialized GeminiProvider with API key")
        else:
            # Fall back to service account
            try:
                # Default path to service account key file
                self.service_account_path = service_account_path or os.path.join(os.getcwd(), "carla-452511-8b972688ef43.json")

                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
            
                # Configure Gemini with credentials
                genai.configure(credentials=credentials)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("Successfully initialized GeminiProvider with service account")
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



"""def __init__(self, api_key: str = None):
    self.api_key = api_key or settings.GEMINI_API_KEY
    genai.configure(api_key=self.api_key)  # Configure API key
    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Initialize Gemini model

async def generate_content(self,
                            prompt: str,
                            max_tokens: int = 2500,
                            temperature: float = 0.7) -> str:
    #Generate content using Gemini API
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
        """