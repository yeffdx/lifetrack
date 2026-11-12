import os
import secrets
from pathlib import Path


class Config:
    """Configuration read from the environment; secrets are never committed."""

    # A deployment supplies a stable secret through the environment. The fallback
    # keeps local startup possible without embedding a reusable secret in source.
    SECRET_KEY = os.environ.get("LIFETRACK_SECRET_KEY") or secrets.token_urlsafe(32)
    DATABASE_URL = os.environ.get(
        "LIFETRACK_DATABASE_URL",
        f"sqlite:///{Path.cwd() / 'lifetrack.sqlite3'}",
    )
    SQL_ECHO = False
    DEBUG = os.environ.get("FLASK_DEBUG") == "1"
    CSRF_ENABLED = True
