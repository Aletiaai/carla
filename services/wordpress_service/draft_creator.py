# services/wordpress_service/wordpress_service.py
import json
import subprocess
import shlex
import pipes
from core.config import settings

class WordPressService:
    def __init__(self):
        self.api_url = settings.WP_API_URL
        self.username = settings.WP_USERNAME
        self.password = settings.WP_PASSWORD
      
    async def create_post(self, title, content):
        """Create a draft post in WordPress using curl subprocess"""
        try:
            # Create proper JSON for the data payload
            payload = json.dumps({
                "title": title,
                "content": content,
                "status": "draft"
            })
            
            # Use a temporary file to avoid shell escaping issues
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
                temp.write(payload)
                temp_path = temp.name
            
            # Construct curl command with data from file
            curl_cmd = [
                'curl', '-X', 'POST',
                '-u', f'{self.username}:{self.password}',
                '-H', 'Content-Type: application/json',
                '-d', '@' + temp_path,
                f'{self.api_url}/wp-json/wp/v2/posts'
            ]
            
            # Execute the curl command without shell
            process = subprocess.Popen(
                curl_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Clean up the temp file
            import os
            os.unlink(temp_path)
            
            if process.returncode != 0:
                print(f"CURL ERROR: {stderr}")
                raise Exception(f"Curl command failed: {stderr}")
            
            # Parse the response JSON
            try:
                response_data = json.loads(stdout)
                return response_data
            except json.JSONDecodeError:
                print(f"JSON ERROR: {stdout}")
                raise Exception(f"Invalid JSON response: {stdout}")
                
        except Exception as e:
            print(f"GENERAL ERROR: {str(e)}")
            raise Exception(f"WordPress post creation failed: {str(e)}")