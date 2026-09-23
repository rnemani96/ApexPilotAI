"""
ApexPilot AI - Win32 Stealth Layer
===================================
Provides hardware-level screen share invisibility (GhostPilot AI feature),
click-through overlay transparency, and non-activating window styles.

Features:
- SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE):
  Completely hides window from Zoom, MS Teams, Google Meet, Discord, OBS, WebRTC screen shares.
- WS_EX_TRANSPARENT: Click-through mode so cursor passes straight to IDE/browser.
- WS_EX_NOACTIVATE: Window never steals keyboard focus from active code editor.
- WS_EX_TOOLWINDOW: Hidden from Windows Alt+Tab switcher and taskbar.
"""

import sys
import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger("ApexPilot.Stealth")

# Win32 Constants
GWL_EXSTYLE = -20
GWL_STYLE = -16

# Extended Window Styles
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008

# Display Affinity Flags
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Windows 10 version 2004+ / Windows 11


class Win32Stealth:
    """Manages low-level Windows display affinity and window properties for stealth operation."""

    def __init__(self):
        self.is_windows = sys.platform == "win32"
        if self.is_windows:
            self._user32 = ctypes.windll.user32
            self._kernel32 = ctypes.windll.kernel32
            self._setup_prototypes()
        else:
            self._user32 = None
            self._kernel32 = None

    def _setup_prototypes(self):
        """Set up 64-bit safe ctypes function prototypes."""
        try:
            # SetWindowDisplayAffinity(HWND, DWORD) -> BOOL
            self._user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
            self._user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

            # GetWindowLongPtrW / SetWindowLongPtrW for 64-bit compatibility
            if hasattr(self._user32, "GetWindowLongPtrW"):
                self._get_window_long = self._user32.GetWindowLongPtrW
                self._set_window_long = self._user32.SetWindowLongPtrW
            else:
                self._get_window_long = self._user32.GetWindowLongW
                self._set_window_long = self._user32.SetWindowLongW

            self._get_window_long.argtypes = [wintypes.HWND, ctypes.c_int]
            self._get_window_long.restype = ctypes.c_ssize_t

            self._set_window_long.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
            self._set_window_long.restype = ctypes.c_ssize_t

        except Exception as e:
            logger.warning(f"Failed to configure Win32 prototypes: {e}")

    def enable_screen_share_invisibility(self, hwnd: int) -> bool:
        """
        GhostPilot AI Core Feature:
        Excludes the given window from screen sharing, screen recording, and screenshot capture.
        The window remains 100% visible on the physical monitor, but is completely invisible
        to Zoom, MS Teams, Google Meet, Discord, OBS, and Windows Snipping Tool.
        """
        if not self.is_windows or not hwnd:
            return False

        try:
            # First try WDA_EXCLUDEFROMCAPTURE (Win10 2004+ / Win11)
            result = self._user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), WDA_EXCLUDEFROMCAPTURE)
            if result:
                logger.info(f"Screen-share protection ENABLED for HWND {hex(hwnd)} (WDA_EXCLUDEFROMCAPTURE)")
                return True
            
            # Fallback to WDA_MONITOR for older Windows 10 builds
            error_code = self._kernel32.GetLastError()
            logger.warning(f"WDA_EXCLUDEFROMCAPTURE failed (err {error_code}), trying WDA_MONITOR fallback...")
            fallback = self._user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), WDA_MONITOR)
            if fallback:
                logger.info(f"Screen-share protection enabled via WDA_MONITOR for HWND {hex(hwnd)}")
                return True
            else:
                logger.error(f"SetWindowDisplayAffinity completely failed (err {self._kernel32.GetLastError()})")
                return False
        except Exception as e:
            logger.error(f"Exception while setting display affinity: {e}")
            return False

    def disable_screen_share_invisibility(self, hwnd: int) -> bool:
        """Restores standard window display affinity (visible to screen shares)."""
        if not self.is_windows or not hwnd:
            return False
        try:
            return bool(self._user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), WDA_NONE))
        except Exception as e:
            logger.error(f"Failed to disable display affinity: {e}")
            return False

    def set_click_through(self, hwnd: int, enable: bool) -> bool:
        """
        Toggles WS_EX_TRANSPARENT style.
        When True: mouse clicks pass directly through to the background IDE or web browser.
        When False: clicks interact normally with the HUD buttons and inputs.
        """
        if not self.is_windows or not hwnd:
            return False

        try:
            current_exstyle = self._get_window_long(wintypes.HWND(hwnd), GWL_EXSTYLE)
            if enable:
                new_exstyle = current_exstyle | WS_EX_TRANSPARENT | WS_EX_LAYERED
            else:
                new_exstyle = current_exstyle & ~WS_EX_TRANSPARENT

            res = self._set_window_long(wintypes.HWND(hwnd), GWL_EXSTYLE, new_exstyle)
            logger.info(f"Click-through set to {enable} for HWND {hex(hwnd)}")
            return res != 0
        except Exception as e:
            logger.error(f"Failed to toggle click-through: {e}")
            return False

    def apply_stealth_window_styles(self, hwnd: int, click_through: bool = False) -> bool:
        """
        Applies full suite of stealth window styles:
        - WS_EX_TOOLWINDOW: Removes from Alt+Tab task switcher
        - WS_EX_NOACTIVATE: Prevents stealing keyboard focus from active editor
        - WS_EX_TOPMOST: Stays pinned above all other windows
        - WS_EX_LAYERED: Required for alpha transparency
        """
        if not self.is_windows or not hwnd:
            return False

        try:
            current_exstyle = self._get_window_long(wintypes.HWND(hwnd), GWL_EXSTYLE)
            target_style = current_exstyle | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_TOPMOST | WS_EX_LAYERED

            if click_through:
                target_style |= WS_EX_TRANSPARENT

            self._set_window_long(wintypes.HWND(hwnd), GWL_EXSTYLE, target_style)
            return True
        except Exception as e:
            logger.error(f"Failed to apply stealth styles: {e}")
            return False


# Singleton instance
stealth_layer = Win32Stealth()
