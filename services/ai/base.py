from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIProvider(ABC):
    """Abstract base class for AI service providers"""
    
    @abstractmethod
    async def generate_content(self, 
                              prompt: str, 
                              max_tokens: int = 1000,
                              temperature: float = 0.7) -> str:
        """Generate content based on a prompt"""
        pass