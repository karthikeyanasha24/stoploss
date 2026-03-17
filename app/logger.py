"""
Logging configuration. Does not log API keys.
Keeps a ring buffer of recent log lines for live dashboard display.
"""
import logging
import sys
from collections import deque
from pathlib import Path

from . import config

# Ring buffer of last N log lines for /api/logs
LOG_BUFFER: deque[dict] = deque(maxlen=500)


class RingBufferHandler(logging.Handler):
    """Appends formatted log records to LOG_BUFFER for API consumption."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            # Redact API keys from log text
            if config.API_KEY:
                msg = msg.replace(config.API_KEY, "***")
            LOG_BUFFER.append({
                "ts": record.created,
                "level": record.levelname,
                "name": record.name,
                "msg": msg,
            })
        except Exception:
            pass


def configure_logging() -> None:
    Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)
    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    logging.basicConfig(
        level=level,
        format=fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(Path(config.LOG_DIR) / "version_b.log", encoding="utf-8"),
        ],
    )
    buf = RingBufferHandler()
    buf.setLevel(level)
    buf.setFormatter(logging.Formatter(fmt))
    logging.getLogger().addHandler(buf)
