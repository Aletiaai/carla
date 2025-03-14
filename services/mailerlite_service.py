import mailerlite as MailerLite
from core.config import settings

class MailerLiteService:
    def __init__(self):
        self.client = MailerLite.Client({
            'api_key': settings.MAILERLITE_API_KEY
        })
    
    async def create_campaign(self, subject, content, sender_name="Aletia", sender_email="marko.garcia@gmail.com"):
        params = {
            "name": subject,
            "language_id": 1,
            "type": "regular",
            "emails": [{
                "subject": subject,
                "from_name": sender_name,
                "from": sender_email,
                "content": content
            }]
        }
        
        return self.client.campaigns.create(params)