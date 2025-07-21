import os
from functools import lru_cache
from pathlib import Path
from pydantic import BaseSettings, AnyUrl, Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    bot_token: str = Field(..., env="BOT_TOKEN")
    cryptopay_token: str = Field(..., env="CRYPTOPAY_TOKEN")
    database_url: AnyUrl = Field("sqlite+aiosqlite:///./database.db", env="DATABASE_URL")

    # WireGuard
    wg_interface: str = Field("wg0", env="WG_INTERFACE")
    wg_server_public_ip: str = Field("127.0.0.1", env="WG_SERVER_PUBLIC_IP")
    wg_server_port: int = Field(51820, env="WG_SERVER_PORT")

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()