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
GA_ROOT = 2


class Win32Stealth:
    """Manages low-level Windows display affinity and window properties for stealth operation."""

    def __init__(self):
        self.is_windows = sys.platform == "win32"
        self._display_affinity_warned = False
        if self.is_windows:
            self._user32 = ctypes.WinDLL("user32", use_last_error=True)
            self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
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

            self._user32.IsWindow.argtypes = [wintypes.HWND]
            self._user32.IsWindow.restype = wintypes.BOOL

            self._user32.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]
            self._user32.GetAncestor.restype = wintypes.HWND

            self._user32.GetWindowDisplayAffinity.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
            self._user32.GetWindowDisplayAffinity.restype = wintypes.BOOL

            self._dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)
            self._dwmapi.DwmIsCompositionEnabled.argtypes = [ctypes.POINTER(wintypes.BOOL)]
            self._dwmapi.DwmIsCompositionEnabled.restype = ctypes.c_long

        except Exception as e:
            logger.warning(f"Failed to configure Win32 prototypes: {e}")

    def enable_screen_share_invisibility(self, hwnd: int) -> bool:
        """
        GhostPilot AI Core Feature:
        Requests Windows display-affinity exclusion for screen sharing and capture.
        The result is verified; callers must treat False as unprotected because
        capture applications and Windows versions do not all honor this API.
        """
        if not self.is_windows or not hwnd:
            return False

        try:
            if not self._user32.IsWindow(wintypes.HWND(hwnd)):
                logger.debug("Skipping display affinity for invalid HWND %s", hex(hwnd))
                return False
            root_hwnd = self._user32.GetAncestor(wintypes.HWND(hwnd), GA_ROOT)
            if int(root_hwnd or 0) != int(hwnd):
                logger.warning(
                    "Screen-share protection skipped because HWND %s is not a top-level window.",
                    hex(hwnd),
                )
                return False

            composition = wintypes.BOOL()
            if hasattr(self, "_dwmapi"):
                dwm_result = self._dwmapi.DwmIsCompositionEnabled(ctypes.byref(composition))
                if dwm_result != 0 or not composition.value:
                    logger.warning(
                        "Screen-share protection unavailable: DWM composition is disabled "
                        "or could not be queried (HRESULT %s).",
                        dwm_result,
                    )
                    return False

            # First try WDA_EXCLUDEFROMCAPTURE (Win10 2004+ / Win11)
            result = self._user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), WDA_EXCLUDEFROMCAPTURE)
            if result:
                affinity = wintypes.DWORD()
                verified = self._user32.GetWindowDisplayAffinity(
                    wintypes.HWND(hwnd),
                    ctypes.byref(affinity),
                )
                if verified and affinity.value == WDA_EXCLUDEFROMCAPTURE:
                    logger.info(
                        "Screen-share protection ENABLED for HWND %s (WDA_EXCLUDEFROMCAPTURE)",
                        hex(hwnd),
                    )
                    return True
                logger.warning(
                    "Windows accepted display-affinity setup but verification failed for HWND %s.",
                    hex(hwnd),
                )
                return False
            
            # Fallback to WDA_MONITOR for older Windows 10 builds
            error_code = ctypes.get_last_error()
            fallback = self._user32.SetWindowDisplayAffinity(wintypes.HWND(hwnd), WDA_MONITOR)
            if fallback:
                logger.info(
                    "Screen-share protection enabled via WDA_MONITOR for HWND %s",
                    hex(hwnd),
                )
                return True
            else:
                if not self._display_affinity_warned:
                    logger.warning(
                        "Screen-share protection is unavailable for this window "
                        "(Windows rejected WDA_EXCLUDEFROMCAPTURE with error %s "
                        "and WDA_MONITOR fallback also failed). This is an OS/DWM "
                        "limitation; the application will continue normally.",
                        error_code,
                    )
                    self._display_affinity_warned = True
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

    def apply_stealth_window_styles(
        self,
        hwnd: int,
        click_through: bool = False,
        allow_activation: bool = True,
    ) -> bool:
        """
        Applies full suite of stealth window styles:
        - WS_EX_TOOLWINDOW: Removes from Alt+Tab task switcher
        - WS_EX_NOACTIVATE: Optional for passive overlays that must not take focus
        - WS_EX_TOPMOST: Stays pinned above all other windows
        - WS_EX_LAYERED: Required for alpha transparency
        """
        if not self.is_windows or not hwnd:
            return False

        try:
            current_exstyle = self._get_window_long(wintypes.HWND(hwnd), GWL_EXSTYLE)
            target_style = current_exstyle | WS_EX_TOOLWINDOW | WS_EX_TOPMOST | WS_EX_LAYERED

            if allow_activation:
                target_style &= ~WS_EX_NOACTIVATE
            else:
                target_style |= WS_EX_NOACTIVATE

            if click_through:
                target_style |= WS_EX_TRANSPARENT
            else:
                target_style &= ~WS_EX_TRANSPARENT

            self._set_window_long(wintypes.HWND(hwnd), GWL_EXSTYLE, target_style)
            return True
        except Exception as e:
            logger.error(f"Failed to apply stealth styles: {e}")
            return False


# Singleton instance
stealth_layer = Win32Stealth()
