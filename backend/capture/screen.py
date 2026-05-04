import logging
import time
from pathlib import Path

import mss
import mss.tools

from backend.config import settings

logger = logging.getLogger(__name__)


def get_screenshots_dir() -> Path:
    path = Path(settings.screenshots_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def capture_screen(monitor: int | None = None) -> Path:
    """Capture the screen and save as PNG. Returns path to saved screenshot."""
    monitor_idx = monitor if monitor is not None else settings.capture_monitor

    screenshots_dir = get_screenshots_dir()
    timestamp = int(time.time() * 1000)
    filename = f"capture_{timestamp}.png"
    filepath = screenshots_dir / filename

    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_idx >= len(monitors):
            logger.warning(
                "Monitor %d not found, using primary (total: %d)",
                monitor_idx,
                len(monitors),
            )
            monitor_idx = 0

        target_monitor = monitors[monitor_idx]
        screenshot = sct.grab(target_monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))

    logger.info("Screenshot saved: %s (%dx%d)", filepath, screenshot.width, screenshot.height)
    return filepath


def capture_region(x: int, y: int, width: int, height: int) -> Path:
    """Capture a specific screen region. Returns path to saved screenshot."""
    screenshots_dir = get_screenshots_dir()
    timestamp = int(time.time() * 1000)
    filename = f"region_{timestamp}.png"
    filepath = screenshots_dir / filename

    region = {"left": x, "top": y, "width": width, "height": height}

    with mss.mss() as sct:
        screenshot = sct.grab(region)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))

    logger.info("Region captured: %s (%dx%d)", filepath, width, height)
    return filepath


def list_monitors() -> list[dict[str, int]]:
    """List available monitors and their dimensions."""
    with mss.mss() as sct:
        return [
            {
                "index": i,
                "left": m["left"],
                "top": m["top"],
                "width": m["width"],
                "height": m["height"],
            }
            for i, m in enumerate(sct.monitors)
        ]
