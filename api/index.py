"""Vercel entrypoint: exposes the FastAPI app from src/filecrawler/web.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from filecrawler.web import app  # noqa: E402

__all__ = ["app"]
