import os
import re
from services.ai.base import AIProvider
from typing import Dict, Any

PROMPTS_DIR = "prompts"

class BlogGenerator:
    """Service for generating blog content"""
    
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider
        
    async def generate_blog(self, topic: str, audience: str, length: int, personal_story: str) -> Dict[str, Any]:
        """Generate a complete blog based on given parameters"""
        prompt = self._create_blog_prompt(topic, audience, length, personal_story)
        content = await self.ai_provider.generate_content(prompt, max_tokens=2500)
        return self._structure_blog_content(content)
        
    def _create_blog_prompt(self, topic: str, audience: str, length: int, personal_story: str) -> str:
        """Loads an optimized prompt for blog generation from a file in the prompts directory"""
        try:
            filename = "blog_generator.txt"
            with open(os.path.join(PROMPTS_DIR, filename), "r", encoding='utf-8') as f:
                prompt_template = f.read().strip() # Added strip() to remove any trailing whitespace
                prompt_completed = prompt_template.format(topic = topic, audience = audience, length = length, personal_story = personal_story)
                return prompt_completed
        except Exception as e:
            print(f"Error loading prompt file {filename}: {str(e)}")
            return None
        
    def _structure_blog_content(self, content: str) -> Dict[str, Any]:
        """Parse the generated content into a structured format"""
        lines = content.strip().split('\n')
        
        # Extract title (first # heading)
        title = ""
        sections = []
        current_section = {"heading": "", "content": ""}
        
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
            elif line.startswith('## '):
                # Save previous section if it exists
                if current_section["heading"]:
                    sections.append(current_section.copy())
                # Start new section
                current_section = {
                    "heading": line[3:].strip(),
                    "content": ""
                }
            else:
                # Add content to current section
                if current_section["heading"]:
                    current_section["content"] += line + "\n"
                    
        # Add the last section
        if current_section["heading"]:
            sections.append(current_section)
            
        return {
            "title": title,
            "raw_content": content,
            "sections": sections
        }