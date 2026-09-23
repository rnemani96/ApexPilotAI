"""
ApexPilot AI - Screen Snipping Overlay (StealthCoder)
=====================================================
Hotkey-triggered fullscreen crosshair overlay.
Allows user to drag a rectangle around any LeetCode problem, code snippet,
or diagram. Automatically captures the region, executes OCR, and routes
the extracted text to the AI reasoning engine.
"""

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QFont
from core.ocr_engine import ocr_engine
from core.win32_stealth import stealth_layer
import logging

logger = logging.getLogger("ApexPilot.Snip")


class SnipOverlay(QWidget):
    """Fullscreen snip overlay for LeetCode problem capture."""

    snip_completed = Signal(str)  # Emits extracted OCR text

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self.start_pos: QPoint = None
        self.current_pos: QPoint = None
        self.is_snipping = False

    def start_snip(self):
        """Displays fullscreen overlay across all monitors."""
        # Hide while taking base screenshot to avoid capturing the overlay itself
        self.hide()
        QApplication.processEvents()

        screen = QApplication.primaryScreen()
        geometry = screen.virtualGeometry()
        self.setGeometry(geometry)
        self.show()

        # GhostPilot shield: make sure even the snipping overlay is hidden from screen share
        if self.winId():
            stealth_layer.enable_screen_share_invisibility(int(self.winId()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Semi-transparent dark overlay
        painter.fillRect(self.rect(), QColor(10, 15, 25, 120))

        if self.start_pos and self.current_pos:
            rect = QRect(self.start_pos, self.current_pos).normalized()

            # Clear selection rectangle
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Neon cyan bounding box
            pen = QPen(QColor(0, 220, 255), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)

            # Dimensions badge
            w, h = rect.width(), rect.height()
            if w > 20 and h > 20:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(20, 25, 35, 200))
                badge_rect = QRect(rect.left(), rect.top() - 25, 90, 22)
                painter.drawRoundedRect(badge_rect, 4, 4)

                painter.setPen(QColor(0, 220, 255))
                painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, f"{w} × {h}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.current_pos = event.pos()
            self.is_snipping = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            # Cancel on right click
            self.close()

    def mouseMoveEvent(self, event):
        if self.is_snipping:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_snipping:
            self.is_snipping = False
            rect = QRect(self.start_pos, self.current_pos).normalized()
            self.hide()

            if rect.width() > 30 and rect.height() > 30:
                # Capture exact screen pixels
                global_rect = QRect(self.mapToGlobal(rect.topLeft()), self.mapToGlobal(rect.bottomRight()))
                bbox = (global_rect.left(), global_rect.top(), global_rect.right(), global_rect.bottom())

                # Capture and run OCR
                img = ocr_engine.capture_screen(bbox=bbox)
                extracted_text = ocr_engine.extract_text(img)

                if not extracted_text:
                    extracted_text = "[Problem Image Captured - Run OCR or Solve directly]"

                self.snip_completed.emit(extracted_text)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
