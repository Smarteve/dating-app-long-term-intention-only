import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from logging.config import dictConfig
from typing import Any


request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)

_STANDARD_LOG_RECORD_FIELDS = frozenset(
    logging.makeLogRecord({}).__dict__,
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        request_id = request_id_context.get()
        if request_id is not None:
            log["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_FIELDS and key != "message":
                log[key] = value

        if record.exc_info is not None:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, default=str)


def configure_logging(log_level: str) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": JsonFormatter,
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": sys.stdout,
                },
            },
            "root": {
                "handlers": ["stdout"],
                "level": log_level,
            },
        },
    )
