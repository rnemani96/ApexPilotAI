"""
ApexPilot AI - Low-Level Global Hotkey Service
===============================================
Listens for global Windows keystrokes across all applications:
- Ctrl + Alt + H: Panic / Boss Key (Toggles overlay visibility)
- Ctrl + Alt + S: Trigger LeetCode Snipping Tool
- Ctrl + Alt + T: Toggle Webcam Teleprompter HUD
- Ctrl + Alt + C: Silent Copy Code to Clipboard
"""

import sys
import threading
from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger("ApexPilot.Hotkeys")


class GlobalHotkeyManager(QObject):
    """Bridges global keyboard hooks with PySide6 signals."""

    panic_triggered = Signal()
    snip_triggered = Signal()
    teleprompter_triggered = Signal()
    copy_triggered = Signal()
    solve_triggered = Signal()
    click_through_triggered = Signal()

    def __init__(self):
        super().__init__()
        self._is_active = False

    def start(self):
        """Starts background hotkey listener."""
        try:
            import keyboard

            keyboard.add_hotkey("ctrl+alt+h", lambda: self.panic_triggered.emit(), suppress=False)
            keyboard.add_hotkey("ctrl+alt+s", lambda: self.snip_triggered.emit(), suppress=False)
            keyboard.add_hotkey("ctrl+alt+t", lambda: self.teleprompter_triggered.emit(), suppress=False)
            keyboard.add_hotkey("ctrl+alt+c", lambda: self.copy_triggered.emit(), suppress=False)
            keyboard.add_hotkey("ctrl+alt+a", lambda: self.solve_triggered.emit(), suppress=False)
            keyboard.add_hotkey("ctrl+alt+x", lambda: self.click_through_triggered.emit(), suppress=False)

            self._is_active = True
            logger.info("Global hotkeys registered successfully (Ctrl+Alt+H, S, T, C, A, X)")
        except Exception as e:
            logger.warning(f"Could not register global hotkeys (may need administrator permissions): {e}")

    def stop(self):
        if self._is_active:
            try:
                import keyboard
                keyboard.unhook_all()
            except Exception:
                pass
            self._is_active = False


hotkey_manager = GlobalHotkeyManager()
