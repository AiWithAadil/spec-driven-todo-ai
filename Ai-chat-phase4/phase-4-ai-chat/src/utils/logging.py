"""Structured logging module with request context."""

import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Optional, Any, Dict
from datetime import datetime

# Context variable for request_id
request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> str:
    """Get current request ID or generate new one."""
    request_id = request_id_context.get()
    if not request_id:
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
    return request_id


def set_request_id(request_id: str) -> None:
    """Set the request ID for current context."""
    request_id_context.set(request_id)


class StructuredLogger:
    """Logger with structured JSON output and request context."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    def _build_log_context(
        self,
        message: str,
        level: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build structured log context."""
        context = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "message": message,
            "request_id": get_request_id(),
        }
        if extra:
            context.update(extra)
        return context

    def info(self, message: str, **kwargs) -> None:
        """Log info level message."""
        context = self._build_log_context(message, "INFO", kwargs)
        self.logger.info(json.dumps(context))

    def error(self, message: str, **kwargs) -> None:
        """
        Log error level message (T077: structured error logging).

        Args:
            message: Error message
            **kwargs: Additional context (user_id, conversation_id, error_type, etc.)
        """
        context = self._build_log_context(message, "ERROR", kwargs)
        self.logger.error(json.dumps(context))

    def warning(self, message: str, **kwargs) -> None:
        """Log warning level message."""
        context = self._build_log_context(message, "WARNING", kwargs)
        self.logger.warning(json.dumps(context))

    def debug(self, message: str, **kwargs) -> None:
        """Log debug level message."""
        context = self._build_log_context(message, "DEBUG", kwargs)
        self.logger.debug(json.dumps(context))

    def metric(self, name: str, value: float, **kwargs) -> None:
        """
        Log metric (T083: performance monitoring).

        Args:
            name: Metric name (e.g., "endpoint_latency", "tool_invocation_time")
            value: Metric value (e.g., latency in milliseconds)
            **kwargs: Additional context (endpoint, status_code, tool_name, etc.)
        """
        context = self._build_log_context(f"metric:{name}", "METRIC", {**kwargs, "value": value})
        self.logger.info(json.dumps(context))


def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging for application."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
    )


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


class LogEndpointMetrics:
    """Context manager to log endpoint metrics."""

    def __init__(self, logger: StructuredLogger, endpoint: str):
        self.logger = logger
        self.endpoint = endpoint
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = (time.time() - self.start_time) * 1000
        status = "error" if exc_type else "success"
        self.logger.metric(
            "endpoint_latency",
            latency_ms,
            endpoint=self.endpoint,
            status=status,
        )
        if exc_type:
            self.logger.error(
                f"Endpoint error: {self.endpoint}",
                endpoint=self.endpoint,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
            )
        return False
