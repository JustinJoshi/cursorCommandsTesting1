from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Prius Price Tracker"
    debug: bool = True

    db_path: str = str(Path(__file__).parent / "data" / "prius_tracker.db")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5vl:7b"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    extraction_backend: str = "ollama"  # "ollama" or "openai"
    analysis_backend: str = "ollama"  # "ollama" or "openai"

    capture_hotkey: str = "<super>+<shift>+p"
    capture_monitor: int = 0  # 0 = primary monitor

    screenshots_dir: str = str(Path(__file__).parent / "data" / "screenshots")

    frontend_port: int = 5173
    backend_port: int = 8000

    class Config:
        env_file = ".env"
        env_prefix = "PRIUS_"


settings = Settings()
