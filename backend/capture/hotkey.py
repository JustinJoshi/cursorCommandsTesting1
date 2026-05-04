import asyncio
import logging
import threading
from typing import Callable

from pynput import keyboard

from backend.config import settings

logger = logging.getLogger(__name__)


class HotkeyListener:
    """Listens for global hotkey to trigger screen capture."""

    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self._listener: keyboard.GlobalHotKeys | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        hotkey_str = settings.capture_hotkey
        logger.info("Registering hotkey: %s", hotkey_str)

        self._listener = keyboard.GlobalHotKeys({hotkey_str: self._on_hotkey})
        self._listener.start()
        logger.info("Hotkey listener started")

    def _on_hotkey(self) -> None:
        logger.info("Hotkey triggered")
        self.callback()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
            logger.info("Hotkey listener stopped")


class AsyncHotkeyListener:
    """Wraps HotkeyListener to work with asyncio callbacks."""

    def __init__(self, async_callback: Callable[[], any]):
        self._async_callback = async_callback
        self._loop: asyncio.AbstractEventLoop | None = None
        self._listener: HotkeyListener | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._listener = HotkeyListener(self._sync_callback)
        self._listener.start()

    def _sync_callback(self) -> None:
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(
                asyncio.ensure_future, self._async_callback()
            )

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
