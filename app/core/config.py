from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Robotics ABC Dashboard API"
    app_version: str = "0.0.1"
    api_v1_prefix: str = "/api/v1"
    api_v2_prefix: str = "/api/v2"
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'robot_orders.db'}"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://api-ssu-abc.ssammwu.info",
        "https://ssu-abc-store-kiosk.ssammwu.info",
        "https://ssu-abc-store-dashboard.ssammwu.info"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
