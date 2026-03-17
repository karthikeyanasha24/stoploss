"""
Persistent settings storage for dashboard. Replaces .env for user-configured values.
Stores: settings.json (config), uploaded_credentials.json (Google service account).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

_SETTINGS_FILENAME = "settings.json"
_CREDENTIALS_FILENAME = "uploaded_credentials.json"


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _settings_path() -> Path:
    return _data_dir() / _SETTINGS_FILENAME


def _credentials_path() -> Path:
    return _data_dir() / _CREDENTIALS_FILENAME


def get_settings() -> Optional[Dict[str, Any]]:
    """Load settings from data/settings.json. Returns None if file missing or invalid."""
    p = _settings_path()
    if not p.is_file():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to data/settings.json."""
    _data_dir().mkdir(parents=True, exist_ok=True)
    p = _settings_path()
    with open(p, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def save_credentials(content: bytes) -> bool:
    """Save uploaded credentials JSON to data/uploaded_credentials.json. Returns True on success."""
    try:
        json.loads(content.decode("utf-8"))  # validate JSON
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    _data_dir().mkdir(parents=True, exist_ok=True)
    p = _credentials_path()
    with open(p, "wb") as f:
        f.write(content)
    return True


def get_credentials_path() -> Optional[Path]:
    """Return path to stored credentials if they exist."""
    p = _credentials_path()
    return p if p.is_file() else None


def has_stored_settings() -> bool:
    """True if settings.json exists and has content."""
    s = get_settings()
    return s is not None and len(s) > 0
