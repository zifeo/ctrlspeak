"""
Low-level utility functions for permission checking to avoid circular dependencies.
"""

import sys
import time
from pynput import keyboard

def check_input_monitoring_permission_behavioral():
    """
    Check if the app has Input Monitoring permissions (kTCCServicePostEvent)
    using a behavioral test.
    """
    if sys.platform != "darwin":
        return True

    try:
        test_listener = keyboard.Listener(on_press=lambda k: None)
        test_listener.start()
        time.sleep(0.5)
        is_alive = test_listener.is_alive()
        test_listener.stop()
        return is_alive
    except Exception:
        return False
