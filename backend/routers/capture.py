import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.capture.screen import capture_screen, list_monitors
from backend.config import settings
from backend.database import get_session
from backend.extraction.base import BaseExtractor
from backend.models import CaptureStatus, Listing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/capture", tags=["capture"])

_capture_status = CaptureStatus(status="idle")


def get_extractor() -> BaseExtractor:
    if settings.extraction_backend == "openai":
        from backend.extraction.openai_vision import OpenAIVisionExtractor
        return OpenAIVisionExtractor()
    else:
        from backend.extraction.qwen_local import QwenLocalExtractor
        return QwenLocalExtractor()


@router.get("/status", response_model=CaptureStatus)
def get_capture_status():
    return _capture_status


@router.get("/monitors")
def get_monitors():
    return list_monitors()


@router.post("", response_model=CaptureStatus)
async def trigger_capture(
    monitor: int | None = None,
    session: Session = Depends(get_session),
):
    global _capture_status

    if _capture_status.status == "capturing":
        return CaptureStatus(status="busy", message="Capture already in progress")

    _capture_status = CaptureStatus(status="capturing", message="Taking screenshot...")

    try:
        screenshot_path = capture_screen(monitor)
        _capture_status = CaptureStatus(
            status="extracting", message="Analyzing screenshot with AI..."
        )

        extractor = get_extractor()
        raw_listings = await extractor.extract_listings(screenshot_path)

        saved_count = 0
        for raw in raw_listings:
            try:
                listing = Listing(
                    title=raw.get("title", "Unknown"),
                    price=float(raw.get("price", 0)),
                    year=int(raw.get("year", 0)),
                    model=raw.get("model", "Prius"),
                    trim=raw.get("trim"),
                    mileage=raw.get("mileage"),
                    description=raw.get("description"),
                    link=raw.get("link_text"),
                    source_screenshot=str(screenshot_path),
                )

                analysis = await extractor.analyze_price(raw)
                listing.ai_summary = analysis.get("summary")
                listing.deal_rating = analysis.get("deal_rating")
                listing.estimated_market_value = analysis.get("estimated_market_value")

                session.add(listing)
                saved_count += 1
            except (ValueError, TypeError) as e:
                logger.warning("Skipping invalid listing: %s - %s", raw, e)
                continue

        session.commit()
        _capture_status = CaptureStatus(
            status="done",
            message=f"Extracted {saved_count} listings",
            listings_found=saved_count,
        )

    except Exception as e:
        logger.exception("Capture failed")
        _capture_status = CaptureStatus(status="error", message=str(e))

    return _capture_status


@router.post("/batch", response_model=CaptureStatus)
async def trigger_batch_capture(
    count: int = 3,
    delay_seconds: float = 5.0,
    monitor: int | None = None,
    session: Session = Depends(get_session),
):
    """Capture multiple screenshots with a delay between each (for scrolling through listings)."""
    global _capture_status

    _capture_status = CaptureStatus(
        status="capturing", message=f"Batch capture: 0/{count} done"
    )

    total_saved = 0
    extractor = get_extractor()

    try:
        for i in range(count):
            if i > 0:
                await asyncio.sleep(delay_seconds)

            _capture_status = CaptureStatus(
                status="capturing",
                message=f"Capturing screenshot {i + 1}/{count}...",
            )

            screenshot_path = capture_screen(monitor)

            _capture_status = CaptureStatus(
                status="extracting",
                message=f"Analyzing screenshot {i + 1}/{count}...",
            )

            raw_listings = await extractor.extract_listings(screenshot_path)

            for raw in raw_listings:
                try:
                    listing = Listing(
                        title=raw.get("title", "Unknown"),
                        price=float(raw.get("price", 0)),
                        year=int(raw.get("year", 0)),
                        model=raw.get("model", "Prius"),
                        trim=raw.get("trim"),
                        mileage=raw.get("mileage"),
                        description=raw.get("description"),
                        link=raw.get("link_text"),
                        source_screenshot=str(screenshot_path),
                    )

                    analysis = await extractor.analyze_price(raw)
                    listing.ai_summary = analysis.get("summary")
                    listing.deal_rating = analysis.get("deal_rating")
                    listing.estimated_market_value = analysis.get("estimated_market_value")

                    session.add(listing)
                    total_saved += 1
                except (ValueError, TypeError) as e:
                    logger.warning("Skipping invalid listing: %s", e)
                    continue

            session.commit()

        _capture_status = CaptureStatus(
            status="done",
            message=f"Batch complete: {total_saved} listings from {count} captures",
            listings_found=total_saved,
        )

    except Exception as e:
        logger.exception("Batch capture failed")
        _capture_status = CaptureStatus(status="error", message=str(e))

    return _capture_status
