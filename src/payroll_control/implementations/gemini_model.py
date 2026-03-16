import time

from google import genai
from google.genai import types

from ..abstractions.cost_logger import CostLogger
from ..abstractions.language_model import LanguageModel
from ..config.settings import (
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_TEMPERATURE,
    MAX_RETRIES,
    RATE_LIMIT_RETRY_WAIT_SECONDS,
)


def _mask_key(key: str) -> str:
    if len(key) <= 12:
        return "***"
    return key[:8] + "..." + key[-4:]


class GeminiModel(LanguageModel):
    def __init__(self, api_key: str, model: str, cost_logger: CostLogger):
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._key_hint = _mask_key(api_key)
        self._cost_logger = cost_logger

    def _call_with_retry(self, contents: list, max_tokens: int | None = None) -> str:
        if max_tokens is None:
            max_tokens = GEMINI_MAX_OUTPUT_TOKENS
        for attempt in range(MAX_RETRIES):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        max_output_tokens=max_tokens,
                        temperature=GEMINI_TEMPERATURE,
                    ),
                )
                usage = response.usage_metadata
                if usage:
                    output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
                    self._cost_logger.log(
                        self._model,
                        usage.prompt_token_count or 0,
                        output_tokens,
                    )
                return response.text.strip()
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = RATE_LIMIT_RETRY_WAIT_SECONDS * (attempt + 1)
                    print(f"[RATE LIMIT] waiting {wait}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(wait)
                elif "API_KEY_INVALID" in str(e) or "key expired" in str(e).lower():
                    print(f"[KEY ERROR] key={self._key_hint} — {e}")
                    raise
                else:
                    raise
        raise RuntimeError("All Gemini retries exhausted.")

    def extract_from_image(self, image_bytes: bytes, prompt: str) -> str:
        return self._call_with_retry([
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        ])

    def extract_from_pdf(self, pdf_bytes: bytes, prompt: str) -> str:
        return self._call_with_retry([
            prompt,
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
        ])
