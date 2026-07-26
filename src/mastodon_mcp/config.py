"""mastodon-mcp configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _default_data_dir() -> str:
    return str(Path(__file__).resolve().parents[2] / "data")


@dataclass
class Settings:
    server_name: str = "mastodon-mcp"
    backend_port: int = 10754
    instance: str = ""
    access_token: str = ""
    dry_run: bool = True
    require_outbox_approval: bool = True
    data_dir: str = ""
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        self.backend_port = int(os.getenv("MASTODON_BACKEND_PORT", self.backend_port))
        self.instance = (os.getenv("MASTODON_INSTANCE", self.instance) or "").rstrip("/")
        self.access_token = os.getenv("MASTODON_ACCESS_TOKEN", self.access_token) or ""
        dry = os.getenv("MASTODON_DRY_RUN", "1")
        self.dry_run = dry not in ("0", "false", "False", "no")
        req = os.getenv("MASTODON_REQUIRE_OUTBOX_APPROVAL", "1")
        self.require_outbox_approval = req not in ("0", "false", "False", "no")
        self.data_dir = os.getenv("MASTODON_DATA_DIR", "") or _default_data_dir()
        self.log_level = os.getenv("MASTODON_LOG_LEVEL", self.log_level)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
