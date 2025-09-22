"""Logging system for Ren Browser.

Provides centralized logging for application events, errors, and
Reticulum network activities.
"""

import datetime

import RNS

APP_LOGS: list[str] = []
ERROR_LOGS: list[str] = []
RET_LOGS: list[str] = []
_original_rns_log = RNS.log


def log_ret(msg, *args, **kwargs):
    """Log Reticulum messages with timestamp.

    Args:
        msg: Log message.
        *args: Additional arguments passed to original RNS.log.
        **kwargs: Additional keyword arguments passed to original RNS.log.

    """
    timestamp = datetime.datetime.now().isoformat()
    RET_LOGS.append(f"[{timestamp}] {msg}")
    return _original_rns_log(msg, *args, **kwargs)


def setup_rns_logging():
    """Set up RNS log replacement. Call this after RNS.Reticulum initialization."""
    global _original_rns_log
    # Only set up if not already done and if RNS.log is not already our function
    if RNS.log != log_ret and _original_rns_log != log_ret:
        _original_rns_log = RNS.log
        RNS.log = log_ret


def log_error(msg: str):
    """Log error messages to both error and application logs.

    Args:
        msg: Error message to log.

    """
    timestamp = datetime.datetime.now().isoformat()
    ERROR_LOGS.append(f"[{timestamp}] {msg}")
    APP_LOGS.append(f"[{timestamp}] ERROR: {msg}")


def log_app(msg: str):
    """Log application messages.

    Args:
        msg: Application message to log.

    """
    timestamp = datetime.datetime.now().isoformat()
    APP_LOGS.append(f"[{timestamp}] {msg}")
