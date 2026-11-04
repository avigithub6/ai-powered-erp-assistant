import json

import httpx

from app.ai.prompts.system_prompt import SYSTEM_PROMPT
from app.config import settings


class OllamaClient:
    async def select_tool(self, question: str) -> dict:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            "options": {
                "temperature": 0,
            },
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
                json=payload,
            )

            response.raise_for_status()
            result = response.json()

        if not isinstance(result, dict):
            raise TypeError("Invalid Ollama response format")

        message = result.get("message")

        if not isinstance(message, dict):
            raise TypeError("Invalid Ollama message format")

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Ollama returned an empty response")

        parsed = json.loads(content)

        if not isinstance(parsed, dict):
            raise TypeError("Invalid Ollama tool selection format")

        return parsed