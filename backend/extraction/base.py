from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseExtractor(ABC):
    """Abstract interface for vision model extractors."""

    @abstractmethod
    async def extract_listings(self, image_path: Path) -> list[dict[str, Any]]:
        """Extract multiple listings from a Marketplace search results screenshot."""
        ...

    @abstractmethod
    async def extract_detail(self, image_path: Path) -> dict[str, Any]:
        """Extract full details from a single listing detail screenshot."""
        ...

    @abstractmethod
    async def analyze_price(self, listing: dict[str, Any]) -> dict[str, Any]:
        """Generate AI price analysis for a listing."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the name/identifier of the model being used."""
        ...
