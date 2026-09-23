"""
ApexPilot AI - Main Application Entry Point
============================================
Ultra-low-latency, local-first stealth interview and meeting copilot for Windows.
Combines GhostPilot AI, StealthCoder, Parakeet AI, HuddleMate, and Final Round AI.
"""

import sys
import os
from pathlib import Path
import logging

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ApexPilot")

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter
from PySide6.QtCore import Qt

from ui.overlay_window import OverlayWindow
from core.hotkey_manager import hotkey_manager
from core.audio_capture import audio_engine
from core.llm_client import llm_client


def create_tray_icon(app: QApplication, overlay: OverlayWindow) -> QSystemTrayIcon:
    """Creates system tray icon for silent stealth operation."""
    # Create simple programmatically drawn shield icon
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(2, 132, 199))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 24, 24, 6, 6)
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "A")
    painter.end()

    tray = QSystemTrayIcon(QIcon(pixmap), app)
    tray.setToolTip("ApexPilot AI - Stealth Copilot Active")

    menu = QMenu()
    show_action = menu.addAction("Show/Hide Overlay (Ctrl+Alt+H)")
    show_action.triggered.connect(lambda: overlay.setVisible(not overlay.isVisible()))

    snip_action = menu.addAction("Snip LeetCode Screen (Ctrl+Alt+S)")
    snip_action.triggered.connect(overlay.start_snip)

    tele_action = menu.addAction("Toggle Teleprompter (Ctrl+Alt+T)")
    tele_action.triggered.connect(overlay._toggle_teleprompter_mode)

    menu.addSeparator()
    quit_action = menu.addAction("Exit ApexPilot")
    quit_action.triggered.connect(app.quit)

    tray.setContextMenu(menu)
    tray.show()
    return tray


def main():
    logger.info("Initializing ApexPilot AI Engine...")

    # High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("ApexPilot AI")
    app.setQuitOnLastWindowClosed(False)  # Remains active in tray when hidden

    # Check local LLM status
    online, status_msg, models = llm_client.check_health()
    logger.info(f"Local LLM Status: {status_msg}")

    # Initialize Master Stealth HUD
    overlay = OverlayWindow()
    overlay.show()

    # Create tray icon
    tray = create_tray_icon(app, overlay)

    # Wire Global Hotkeys
    def on_panic():
        if overlay.isVisible() or overlay.teleprompter_bar.isVisible():
            overlay.hide()
            overlay.teleprompter_bar.hide()
        else:
            overlay.show()

    hotkey_manager.panic_triggered.connect(on_panic)
    hotkey_manager.snip_triggered.connect(overlay.start_snip)
    hotkey_manager.teleprompter_triggered.connect(overlay._toggle_teleprompter_mode)
    hotkey_manager.copy_triggered.connect(overlay.copy_clean_code)
    hotkey_manager.solve_triggered.connect(overlay._on_submit_query)
    hotkey_manager.click_through_triggered.connect(overlay._toggle_click_through)
    hotkey_manager.start()

    # Start audio capture engine
    audio_engine.start_capture()

    logger.info("ApexPilot AI initialized successfully.")
    logger.info("Press Ctrl+Alt+H for Panic Hide/Show | Ctrl+Alt+S to Snip LeetCode")

    try:
        exit_code = app.exec()
    finally:
        hotkey_manager.stop()
        audio_engine.stop_capture()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
