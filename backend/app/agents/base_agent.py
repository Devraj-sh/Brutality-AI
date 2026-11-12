from typing import Any, Dict, Optional
from app.services.ai_service import BaseAIService, get_ai_service

class BaseAgent:
    def __init__(self, name: str, ai_service: Optional[BaseAIService] = None):
        self.name = name
        self.ai = ai_service or get_ai_service()

    def get_system_prompt(self) -> str:
        raise NotImplementedError

    def log(self, message: str) -> None:
        print(f"[{self.name}] {message}")
