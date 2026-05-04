import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.routers import capture, listings, stats

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.app_name)
    init_db()
    logger.info("Database initialized")

    # Start hotkey listener if running locally with display access
    hotkey_listener = None
    try:
        from backend.capture.hotkey import AsyncHotkeyListener

        async def on_hotkey():
            logger.info("Hotkey capture triggered")
            from backend.capture.screen import capture_screen
            from backend.extraction.qwen_local import QwenLocalExtractor
            from backend.database import get_session
            from backend.models import Listing

            screenshot_path = capture_screen()
            extractor = QwenLocalExtractor()
            raw_listings = await extractor.extract_listings(screenshot_path)
            logger.info("Hotkey extraction found %d listings", len(raw_listings))

        hotkey_listener = AsyncHotkeyListener(on_hotkey)
        loop = asyncio.get_event_loop()
        hotkey_listener.start(loop)
        logger.info("Hotkey listener active: %s", settings.capture_hotkey)
    except Exception as e:
        logger.warning("Could not start hotkey listener (no display?): %s", e)

    yield

    if hotkey_listener:
        hotkey_listener.stop()
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="Compare Toyota Prius prices from Facebook Marketplace using local AI vision",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings.router)
app.include_router(capture.router)
app.include_router(stats.router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "extraction_backend": settings.extraction_backend,
        "model": settings.ollama_model if settings.extraction_backend == "ollama" else settings.openai_model,
    }
