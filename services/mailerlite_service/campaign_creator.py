import mailerlite as MailerLite
from core.config import settings
import re, os
from services.ai.gemini_provider import GeminiProvider
from api.routes import dependencies 
from html import escape 

PROMPTS_DIR = "prompts"

class MailerLiteService:
    def __init__(self):
        self.client = MailerLite.Client({
            'api_key': settings.MAILERLITE_API_KEY
        })
    
    async def _generate_email_body(self, personal_intro: str) -> str:
        """Generates an enhanced email body using an LLM."""
        llm = GeminiProvider()
        prompt = _create_email_body_prompt(personal_intro)
        try:
            email_campaign_body = await llm.generate_content(prompt, max_tokens = 500)
            clean_email_campaign_body = _clean_email_body(email_campaign_body)
            return clean_email_campaign_body
        except Exception as e:
            print(f"Error generating email body: {str(e)}")
            return personal_intro
    
    async def create_campaign(self, content: str, post_id: int, sender_name="Gema", sender_email="marko.garcia@gmail.com")-> dict:
        """Creates an email campaign using MailerLite."""
        seed_content = extract_campaign_content(content)
        subject = extract_title_from_content(content)

        try:
            post_link = await dependencies.get_wordpress_post_link(post_id)
            print(f"Received post_link: {post_link}")
            email_body = await self._generate_email_body(seed_content)
            link_html = create_button_html(post_link)
            #link_html = f"""<div style="text-align: justify; font-family: Montserrat;"><a href="{escape(post_link)}" style="color: #0066cc; text-decoration: none;"><b>Sigue leyendo aquí →</b></a></div>"""
            enhance_content = email_body + link_html

        except Exception as e:
            print(f"Error getting wordpress post link: {str(e)}")
            enhance_content = await self._generate_email_body(seed_content)

        params = {
            "name": subject,
            "language_id": 8,
            "type": "regular",
            "emails": [{
                "subject": subject,
                "from_name": sender_name,
                "from": sender_email,
                "content": enhance_content
            }]
        }
        print(f"MailerLite API Request Params: {params}")

        try:
            result = self.client.campaigns.create(params)
            print(f"MailerLite API Response: {result}")  # Print the raw response
            return {"status": "success", "campaign": result}
        except Exception as e:
            print(f"MailerLite API Error: {str(e)}")
            return {"status": "error", "message": "MailerLite API error", "details": str(e)}
    
def extract_title_from_content(content: str) -> str:
    """Extracts the title from the HTML content."""
    match = re.search(r'<h1>(.*?)<\/h1>', content)
    if match:
        return match.group(1).strip()
    return ""

def extract_campaign_content(content: str) -> str:
    """Extracts the first paragraph from the full HTML content string."""
    match = re.search(r'<\/h1><br><br>(.*?)<br><br>', content)
    if match:
        return match.group(1).strip()
    return ""
def _create_email_body_prompt(personal_intro: str) -> str:
        """Loads the prompt from a file in the prompts directory."""
        try:
            filename = "campaign_body_generator.txt"
            with open(os.path.join(PROMPTS_DIR, filename), "r", encoding='utf-8') as f:
                prompt_template = f.read().strip() # Added strip() to remove any trailing whitespace
                prompt_completed = prompt_template.format(personal_intro = personal_intro)
                return prompt_completed
        except Exception as e:
            print(f"Error loading prompt file {filename}: {str(e)}")
            return None
def _clean_email_body(email_body: str) -> str:
    if email_body.startswith("```html"):
        email_body = email_body[7:]  # Remove first 7 characters
    if email_body.endswith("```"):
        email_body = email_body[:-3]  # Remove last 3 characters
    return email_body.strip()

from html import escape

def create_button_html(post_link, button_text="Sigue leyendo aquí →"):
  """
  Creates an HTML button with a link."""
  link_html = f"""
  <div style="text-align: center; font-family: Montserrat;">
    <a href="{escape(post_link)}" style="text-decoration: none;">
      <button style="background-color: #335d55; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-family: Montserrat; font-weight: bold;">
        {button_text}
      </button>
    </a>
  </div>
  """
  return link_html