import requests
from core.config import settings

class MailerLiteService:
    def __init__(self):
        self.api_key = settings.MAILERLITE_API_KEY
        self.base_url = "https://connect.mailerlite.com/api"
        self.headers = {
            "X-MailerLite-ApiKey": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_campaign(self, subject, content, sender_name="Your Company", sender_email="your@email.com"):
        url = f"{self.base_url}/campaigns"
        payload = {
            "subject": subject,
            "type": "regular",
            "from": sender_name,
            "from_email": sender_email,
            "html": content
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()