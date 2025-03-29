import mailerlite as MailerLite
from core.config import settings
import re

class MailerLiteService:
    def __init__(self):
        self.client = MailerLite.Client({
            'api_key': settings.MAILERLITE_API_KEY
        })
    
    async def create_campaign(self, subject, content, sender_name="Gema", sender_email="marko.garcia@gmail.com"):
        params = {
            "name": subject,
            "language_id": 6,
            "type": "regular",
            "emails": [{
                "subject": subject,
                "from_name": sender_name,
                "from": sender_email,
                "content": content
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