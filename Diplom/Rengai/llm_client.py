"""LLM клиент для Rengai Chat (Ollama)."""

from __future__ import annotations

import json
from typing import Any, Dict, Generator, List

import requests

from Rengai.config import config


class LLMClient:
    """Клиент для работы с Ollama (OpenAI-compatible API)."""

    def __init__(self) -> None:
        self._api_config = config.api_config

    def chat_stream(
        self, messages: List[Dict[str, str]]
    ) -> Generator[str, None, None]:
        """Отправляет сообщения и получает ответ от Ollama.
        :param messages: История сообщений.
        :returns: Генератор чанков ответа.
        """
        base_url = self._api_config.get("base_url", "http://127.0.0.1:11434")
        model = self._api_config.get("model", "llama3.1:8b")

        url = f"{base_url}/api/chat"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=120)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "content" in data.get("message", {}):
                            content = data["message"]["content"]
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
        except requests.RequestException as e:
            yield f"Ошибка подключения: {str(e)}\nПроверь, что Ollama запущен на {base_url}"


llm_client = LLMClient()