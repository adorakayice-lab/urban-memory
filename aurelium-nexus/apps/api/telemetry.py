import os
import logging

logger = logging.getLogger('aurelium.telemetry')


def telemetry_enabled() -> bool:
    # Controlled by env var TELEMETRY_ENABLED ("1", "true"), default off
    v = os.getenv('TELEMETRY_ENABLED', 'false').lower()
    return v in ('1', 'true', 'yes')


def send_event(event_name: str, payload: dict | None = None):
    """Stub telemetry sender. In production, send to analytics backend.

    This function obeys `telemetry_enabled()` and will no-op when disabled.
    """
    if not telemetry_enabled():
        return
    payload = payload or {}
    # For now, just log; replace with a real telemetry client in prod.
    logger.info('telemetry event=%s payload=%s', event_name, payload)
