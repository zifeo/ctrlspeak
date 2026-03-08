import time
from pynput import keyboard
from rich.console import Console


from utils.permission_manager import check_keyboard_permissions


class KeyboardShortcutManager:
    """
    A class to manage keyboard shortcuts and hotkeys
    """

    def __init__(self):
        self.hotkey_listener = None
        self.shortcuts = {}
        self.is_running = True
        self.console = Console()

        # For triple-tap detection
        self.last_key_time = 0
        self.ctrl_tap_count = 0
        self.ctrl_tap_timeout = 0.5  # seconds between taps
        self.triple_tap_callback = None
        self.key_listener = None

    def check_permissions(self):
        """Check and request necessary accessibility permissions for keyboard control"""
        return check_keyboard_permissions(verbose=True)

    def register_shortcut(self, key_combination, callback):
        """
        Register a keyboard shortcut

        Args:
            key_combination (str): Key combination in pynput format (e.g., '<alt>+`')
            callback (function): Function to call when shortcut is pressed
        """
        self.shortcuts[key_combination] = callback

    def register_triple_ctrl_tap(self, callback):
        """
        Register a callback for when Ctrl is tapped three times in succession

        Args:
            callback (function): Function to call when triple-tap is detected
        """
        self.triple_tap_callback = callback

    def _on_key_press(self, key):
        """
        Internal handler for key press events to detect triple-tap
        """
        # Check if it's a ctrl key
        if (
            key == keyboard.Key.ctrl
            or key == keyboard.Key.ctrl_l
            or key == keyboard.Key.ctrl_r
        ):
            current_time = time.time()

            # If it's been too long since the last tap, reset the counter
            if current_time - self.last_key_time > self.ctrl_tap_timeout:
                self.ctrl_tap_count = 1
            else:
                self.ctrl_tap_count += 1

            self.last_key_time = current_time

            # If we've reached 3 taps, trigger the callback
            if self.ctrl_tap_count == 3 and self.triple_tap_callback:
                self.ctrl_tap_count = 0  # Reset counter
                return self.triple_tap_callback()

        return True  # Continue listening

    def _on_key_release(self, key):
        """
        Internal handler for key release events
        """
        # Just continue listening
        return True

    def start_listening(self):
        """Start listening for registered shortcuts and triple-tap"""
        # Start the regular hotkey listener if shortcuts are registered
        if self.shortcuts:
            self.hotkey_listener = keyboard.GlobalHotKeys(self.shortcuts)
            self.hotkey_listener.start()

        # Start the key listener for triple-tap detection
        if self.triple_tap_callback:
            self.key_listener = keyboard.Listener(
                on_press=self._on_key_press, on_release=self._on_key_release
            )
            self.key_listener.start()

        return True

    def stop_listening(self):
        """Stop listening for shortcuts"""
        if self.hotkey_listener:
            self.hotkey_listener.stop()

        if self.key_listener:
            self.key_listener.stop()

        self.is_running = False

    def join(self):
        """Join the hotkey listener thread"""
        if self.hotkey_listener:
            self.hotkey_listener.join()

        if self.key_listener:
            self.key_listener.join()
