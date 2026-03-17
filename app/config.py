"""
Configuration: dashboard settings first, then .env, then defaults.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Import after dotenv so we can override with store
from . import settings_store


def _get(key: str, default: str = "") -> str:
    s = settings_store.get_settings()
    if s and key in s and s[key] is not None:
        return str(s[key]).strip()
    return os.getenv(key, default).strip()


def _get_int(key: str, default: int) -> int:
    val = _get(key, str(default))
    try:
        return int(val)
    except ValueError:
        return default


def _get_bool(key: str, default: bool) -> bool:
    val = _get(key, "true" if default else "false").lower()
    return val in ("true", "1", "yes", "on")


def _credentials_path() -> str:
    """Credentials: uploaded file first, else setting, else default credentials.json in project root.

    This also normalizes any accidentally hardcoded Windows-style absolute paths (e.g.
    C:\\Users\\karth\\Downloads\\STOP_LOSS\\version_b\\credentials.json) when running
    on non-Windows systems by collapsing them to just the filename and resolving them
    relative to the project root.
    """
    # 1) If user uploaded credentials via the UI, always prefer that stored file
    cred_path = settings_store.get_credentials_path()
    if cred_path:
        return str(cred_path)

    # 2) Next, use GOOGLE_CREDENTIALS_PATH from settings/.env if present
    p = _get("GOOGLE_CREDENTIALS_PATH", "").strip()
    base = Path(__file__).resolve().parents[1]

    if p:
        # If we're on a non-Windows system but the value looks like a Windows absolute
        # path (contains a drive letter), just keep the filename and resolve it under
        # the project root so it works cross-machine.
        if os.name != "nt" and (":\\" in p or ":/" in p):
            p = Path(p).name

        p_path = Path(p)
        return str(p_path if p_path.is_absolute() else base / p_path)

    # 3) Fallback: version_b/credentials.json in the project root
    return str(base / "credentials.json")


def _credentials_from_env() -> dict | None:
    """Build Google service account credentials dict from individual env vars.
    Returns None if any required var is missing. No credentials.json file needed.
    """
    project_id = _get("GOOGLE_PROJECT_ID", "").strip()
    private_key_id = _get("GOOGLE_PRIVATE_KEY_ID", "").strip()
    client_email = _get("GOOGLE_CLIENT_EMAIL", "").strip()
    # Prefer GOOGLE_PRIVATE_KEY_BASE64 (avoids newline/escaping issues on Render, etc.)
    private_key_b64 = _get("GOOGLE_PRIVATE_KEY_BASE64", "").strip()
    if private_key_b64:
        import base64
        try:
            private_key = base64.b64decode(private_key_b64).decode("utf-8")
        except Exception:
            return None
    else:
        private_key = _get("GOOGLE_PRIVATE_KEY", "").strip()
        # private_key may use literal \n in env; ensure newlines for PEM
        if "\\n" in private_key:
            private_key = private_key.replace("\\n", "\n")
    if not all([project_id, private_key_id, private_key, client_email]):
        return None
    info: dict = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": _get("GOOGLE_CLIENT_ID", "").strip() or "0",
        "auth_uri": _get("GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth").strip(),
        "token_uri": _get("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token").strip(),
        "auth_provider_x509_cert_url": _get("GOOGLE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs").strip(),
        "client_x509_cert_url": _get("GOOGLE_CLIENT_X509_CERT_URL", "").strip() or f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}",
        "universe_domain": _get("GOOGLE_UNIVERSE_DOMAIN", "googleapis.com").strip(),
    }
    return info


def _api_provider() -> str:
    return _get("API_PROVIDER", "tradier").lower()


def _api_base_url(provider: str) -> str:
    if provider == "alphavantage":
        return "https://www.alphavantage.co"
    if provider == "finnhub":
        return "https://finnhub.io/api/v1"
    if provider == "tradier":
        return "https://sandbox.tradier.com/v1" if _get_bool("PAPER_TRADING", True) else "https://api.tradier.com/v1"
    return "https://api.massive.com"


_API_PROVIDER = _api_provider()
_API_KEY_RAW = (
    _get("API_KEY")
    or (_get("ALPHAVANTAGE_API_KEY") if _API_PROVIDER == "alphavantage" else "")
    or (_get("MASSIVE_API_KEY") if _API_PROVIDER == "massive" else "")
    or (_get("TRADIER_API_KEY") if _API_PROVIDER == "tradier" else "")
    or _get("FINNHUB_API_KEY")
)

API_PROVIDER: str = _API_PROVIDER
API_KEY: str = _API_KEY_RAW
API_BASE_URL: str = _get("API_BASE_URL", _api_base_url(_API_PROVIDER))

GOOGLE_CREDENTIALS_PATH: str = _credentials_path()
GOOGLE_CREDENTIALS_FROM_ENV: dict | None = _credentials_from_env()
SPREADSHEET_ID: str = _get("SPREADSHEET_ID", "")

DB_PATH: str = _get("DB_PATH", "") or str(
    Path(__file__).resolve().parents[1] / "data" / "version_b.db"
)
if not Path(DB_PATH).is_absolute():
    DB_PATH = str(Path(__file__).resolve().parents[1] / DB_PATH)

POLLING_INTERVAL: int = _get_int("POLLING_INTERVAL", 300)
MARKET_TIMEZONE: str = _get("MARKET_TIMEZONE", "US/Eastern")
MARKET_OPEN: str = _get("MARKET_OPEN", "09:30")
MARKET_CLOSE: str = _get("MARKET_CLOSE", "16:00")

ANALYSIS_DAYS: int = _get_int("ANALYSIS_DAYS", 7)
STOP_PERCENTAGES: list = [15, 20, 25, 30, 35, 40]

MOCK_API: bool = _get_bool("MOCK_API", False)
PAPER_TRADING: bool = _get_bool("PAPER_TRADING", True)  # Tradier: sandbox vs live

LOG_LEVEL: str = _get("LOG_LEVEL", "INFO")
LOG_DIR: str = _get("LOG_DIR", "") or str(Path(__file__).resolve().parents[1] / "logs")
if not Path(LOG_DIR).is_absolute():
    LOG_DIR = str(Path(__file__).resolve().parents[1] / LOG_DIR)


def reload_config() -> None:
    """Re-read settings from store and update module-level config. Call after saving settings."""
    global API_PROVIDER, API_KEY, API_BASE_URL, GOOGLE_CREDENTIALS_PATH, GOOGLE_CREDENTIALS_FROM_ENV, SPREADSHEET_ID
    global POLLING_INTERVAL, MARKET_TIMEZONE, MARKET_OPEN, MARKET_CLOSE
    global ANALYSIS_DAYS, MOCK_API, PAPER_TRADING
    _api_prov = _api_provider()
    _key_raw = (
        _get("API_KEY")
        or (_get("ALPHAVANTAGE_API_KEY") if _api_prov == "alphavantage" else "")
        or (_get("MASSIVE_API_KEY") if _api_prov == "massive" else "")
        or (_get("TRADIER_API_KEY") if _api_prov == "tradier" else "")
        or _get("FINNHUB_API_KEY")
    )
    API_PROVIDER = _api_prov
    API_KEY = _key_raw
    API_BASE_URL = _get("API_BASE_URL", _api_base_url(API_PROVIDER))
    GOOGLE_CREDENTIALS_PATH = _credentials_path()
    GOOGLE_CREDENTIALS_FROM_ENV = _credentials_from_env()
    SPREADSHEET_ID = _get("SPREADSHEET_ID", "")
    POLLING_INTERVAL = _get_int("POLLING_INTERVAL", 300)
    MARKET_TIMEZONE = _get("MARKET_TIMEZONE", "US/Eastern")
    MARKET_OPEN = _get("MARKET_OPEN", "09:30")
    MARKET_CLOSE = _get("MARKET_CLOSE", "16:00")
    ANALYSIS_DAYS = _get_int("ANALYSIS_DAYS", 7)
    MOCK_API = _get_bool("MOCK_API", False)
    PAPER_TRADING = _get_bool("PAPER_TRADING", True)
