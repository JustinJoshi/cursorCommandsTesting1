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


class QwenLocalExtractor(BaseExtractor):
    """Extracts listing data using Qwen2.5-VL via local Ollama instance."""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.client = httpx.AsyncClient(timeout=120.0)

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    async def _call_ollama(self, prompt: str, image_path: Path) -> str:
        image_b64 = self._encode_image(image_path)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4096,
            },
        }

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        return response.json()["response"]

    def _parse_json_response(self, raw: str) -> Any:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]  # remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        return json.loads(cleaned)

    async def extract_listings(self, image_path: Path) -> list[dict[str, Any]]:
        prompt = f"{LISTING_EXTRACTION_SYSTEM}\n\n{LISTING_EXTRACTION_USER}"
        raw_response = await self._call_ollama(prompt, image_path)
        logger.debug("Raw Ollama response: %s", raw_response[:500])

        try:
            result = self._parse_json_response(raw_response)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from model: %s", e)
            logger.error("Raw response: %s", raw_response)
            return []

        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return [result]
        return []

    async def extract_detail(self, image_path: Path) -> dict[str, Any]:
        prompt = f"{LISTING_EXTRACTION_SYSTEM}\n\n{DETAIL_EXTRACTION_USER}"
        raw_response = await self._call_ollama(prompt, image_path)

        try:
            result = self._parse_json_response(raw_response)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse detail JSON: %s", e)
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

Consider factors like: typical depreciation for that year, mileage vs average, known issues for that model year, hybrid battery age concerns, and regional pricing.

Return ONLY valid JSON. No markdown, no explanation."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1024,
            },
        }

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json=payload,
        )
        response.raise_for_status()
        raw = response.json()["response"]

        try:
            return self._parse_json_response(raw)
        except json.JSONDecodeError:
            logger.error("Failed to parse price analysis: %s", raw)
            return {
                "deal_rating": "unknown",
                "estimated_market_value": None,
                "summary": "Analysis failed - could not parse model response.",
                "confidence": "low",
            }

    def get_model_name(self) -> str:
        return f"ollama/{self.model}"
