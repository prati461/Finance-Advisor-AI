"""
LLM Client

Unified client for Google Gemini and OpenAI LLM providers.
Gracefully degrades to a None/disabled mode when no API key is configured.

Primary: Google Gemini (gemini-1.5-flash)
Fallback: OpenAI (gpt-4o-mini)
Disabled: Returns None so callers can fall back to the analytics engine.

All calls are wrapped in try/except so the application never breaks
when the LLM is unavailable.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from backend.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Config-driven LLM client supporting Gemini and OpenAI."""

    def __init__(self):
        self.provider = settings.llm_provider
        self.gemini_key = settings.gemini_api_key
        self.openai_key = settings.openai_api_key
        self.gemini_model = settings.llm_model
        self.openai_model = settings.openai_model
        self._gemini = None
        self._openai = None

    @property
    def available(self) -> bool:
        """Whether any LLM provider is configured."""
        if self.provider == "gemini":
            return bool(self.gemini_key)
        if self.provider == "openai":
            return bool(self.openai_key)
        return False

    def _get_gemini(self):
        """Lazily initialize the Gemini client."""
        if self._gemini is None and self.gemini_key:
            try:
                # ``google-genai`` is the package declared in requirements.txt.
                # Keep the import lazy so an unset optional API key never affects
                # application startup.
                from google import genai

                self._gemini = genai.Client(api_key=self.gemini_key)
            except Exception as exc:
                logger.error("Failed to init Gemini: %s", exc)
                self._gemini = None
        return self._gemini

    def _get_openai(self):
        """Lazily initialize the OpenAI client."""
        if self._openai is None and self.openai_key:
            try:
                from openai import OpenAI

                self._openai = OpenAI(api_key=self.openai_key)
            except Exception as exc:
                logger.error("Failed to init OpenAI: %s", exc)
                self._openai = None
        return self._openai

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Generate a text response from the configured LLM provider.

        Returns None if no provider is available or the call fails.
        """
        if self.provider == "gemini" or (self.gemini_key and not self.openai_key):
            return self._generate_gemini(prompt, system, max_tokens, temperature)
        if self.provider == "openai" or self.openai_key:
            return self._generate_openai(prompt, system, max_tokens, temperature)
        return None

    def _generate_gemini(
        self, prompt: str, system: Optional[str], max_tokens: int, temperature: float
    ) -> Optional[str]:
        client = self._get_gemini()
        if not client:
            return None
        try:
            from google.genai import types

            response = client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text
        except Exception as exc:
            logger.error("Gemini generation failed: %s", exc)
            return None

    def _generate_openai(
        self, prompt: str, system: Optional[str], max_tokens: int, temperature: float
    ) -> Optional[str]:
        client = self._get_openai()
        if not client:
            return None
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except Exception as exc:
            logger.error("OpenAI generation failed: %s", exc)
            return None

    def generate_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> Optional[Dict[str, Any]]:
        """Generate a JSON response, parsing the model output."""
        text = self.generate(prompt, system, max_tokens, temperature)
        if not text:
            return None
        try:
            # Strip markdown code fences if present
            cleaned = text.strip()
            if cleaned.startswith("```"):
                # Remove leading fence line
                lines = cleaned.split("\n")
                lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines)
            return json.loads(cleaned)
        except Exception as exc:
            logger.warning("LLM JSON parse failed: %s. Raw: %.200s", exc, text[:200])
            return None


# Singleton
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Return the singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
