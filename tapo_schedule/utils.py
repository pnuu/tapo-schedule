"""Utility functions."""

import time


def get_set_device_info_payload(terminal_uuid, params=None):
    """Get 'set_device_info' payload."""
    return {
        "method": "set_device_info",
        "params": params,
        "requestTimeMils": int(round(time.time() * 1000)),
        "terminalUUID": terminal_uuid
    }
