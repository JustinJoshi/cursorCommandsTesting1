import base64
import json
import logging
from pathlib import Path
from typing import Any

import httpx

from backend.config import settings
from backend.extraction.base import BaseExtractor
from backend.extraction.prompts import (
    DETAIL_EXTRACTION_USER,
    LISTING_EXTRACTION_SYSTEM,
    LISTING_EXTRACTION_USER,
)

logger = logging.getLogger(__name__)


class OpenAIVisionExtractor(BaseExtractor):
    """Extracts listing data using OpenAI GPT-4o Vision API (fallback)."""

    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("PRIUS_OPENAI_API_KEY must be set to use OpenAI backend")
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.client = httpx.AsyncClient(timeout=60.0)

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    async def _call_openai(
        self, system: str, user_text: str, image_path: Path | None = None
    ) -> str:
        messages = [{"role": "system", "content": system}]

        if image_path:
            image_b64 = self._encode_image(image_path)
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            )
        else:
            messages.append({"role": "user", "content": user_text})

        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 4096,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _parse_json_response(self, raw: str) -> Any:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        return json.loads(cleaned)

    async def extract_listings(self, image_path: Path) -> list[dict[str, Any]]:
        raw = await self._call_openai(
            LISTING_EXTRACTION_SYSTEM, LISTING_EXTRACTION_USER, image_path
        )

        try:
            result = self._parse_json_response(raw)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from OpenAI: %s", e)
            return []

        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return [result]
        return []

    async def extract_detail(self, image_path: Path) -> dict[str, Any]:
        raw = await self._call_openai(
            LISTING_EXTRACTION_SYSTEM, DETAIL_EXTRACTION_USER, image_path
        )

        try:
            result = self._parse_json_response(raw)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse detail JSON from OpenAI: %s", e)
            return {}

        if isinstance(result, dict):
            return result
        if isinstance(result, list) and result:
            return result[0]
        return {}

    async def analyze_price(self, listing: dict[str, Any]) -> dict[str, Any]:
        prompt = f"""Analyze this Toyota Prius listing and assess the deal quality.

Listing:
- Year: {listing.get('year')}
- Model: {listing.get('model')}
- Trim: {listing.get('trim', 'Unknown')}
- Price: ${listing.get('price')}
- Mileage: {listing.get('mileage', 'Unknown')}
- Description: {listing.get('description', 'None provided')}

Provide your analysis as JSON with these fields:
- deal_rating: One of "great", "good", "fair", "overpriced"
- estimated_market_value: Your estimate of fair market value as a number
- summary: A 2-3 sentence analysis of the deal quality, noting any red flags or positives
- confidence: Your confidence level "high", "medium", or "low"

Return ONLY valid JSON."""

        raw = await self._call_openai(LISTING_EXTRACTION_SYSTEM, prompt)

        try:
            return self._parse_json_response(raw)
        except json.JSONDecodeError:
            return {
                "deal_rating": "unknown",
                "estimated_market_value": None,
                "summary": "Analysis failed.",
                "confidence": "low",
            }

    def get_model_name(self) -> str:
        return f"openai/{self.model}"
