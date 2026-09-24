"""
ApexPilot AI - Webcam Teleprompter HUD (GhostPilot AI Feature)
==============================================================
Slim, horizontal floating HUD placed directly below the monitor's webcam.
Enables candidate to read AI talking points while maintaining direct eye contact
with the interviewer. Uses Windows display-affinity protection when supported.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSlider, QApplication
from PySide6.QtCore import Qt, QPoint, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QBrush
from core.win32_stealth import stealth_layer
import logging

logger = logging.getLogger("ApexPilot.Teleprompter")


class TeleprompterBar(QWidget):
    """Floating teleprompter bar positioned directly under the webcam."""

    expand_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.drag_position = QPoint()
        self.bullets = ["ApexPilot Teleprompter Ready. Stand by for live talking points..."]
        self.current_index = 0
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(3500)
        self._scroll_timer.timeout.connect(self._scroll_to_next_bullet)

        self._init_ui()
        self._position_under_webcam()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        # Invisibility Shield Indicator
        self.shield_label = QLabel("🛡️ STEALTH")
        self.shield_label.setStyleSheet("color: #00ffaa; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.shield_label)

        # Nav Prev
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(22, 22)
        self.prev_btn.setStyleSheet("background: #252836; color: #8f9bb3; border-radius: 4px; border: none;")
        self.prev_btn.clicked.connect(self.prev_bullet)
        layout.addWidget(self.prev_btn)

        # Counter
        self.counter_label = QLabel("1/1")
        self.counter_label.setStyleSheet("color: #7982a9; font-size: 11px;")
        layout.addWidget(self.counter_label)

        # Nav Next
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(22, 22)
        self.next_btn.setStyleSheet("background: #252836; color: #8f9bb3; border-radius: 4px; border: none;")
        self.next_btn.clicked.connect(self.next_bullet)
        layout.addWidget(self.next_btn)

        # Main Teleprompter Text
        self.text_label = QLabel(self.bullets[0])
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 500;")
        self.text_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.text_label, stretch=1)

        # Dock/Expand to Main Window
        self.expand_btn = QPushButton("⛶ Main HUD")
        self.expand_btn.setFixedHeight(22)
        self.expand_btn.setStyleSheet(
            "background: #1e293b; color: #38bdf8; border: 1px solid #0284c7; "
            "border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold;"
        )
        self.expand_btn.clicked.connect(self.expand_requested.emit)
        layout.addWidget(self.expand_btn)

        self.setFixedHeight(46)
        self.setMinimumWidth(650)

    def _position_under_webcam(self):
        """Positions the HUD at top-center of primary screen directly below webcam."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 700) // 2
        y = 12  # 12px below top bezel
        self.setGeometry(x, y, 700, 46)

    def set_opacity(self, opacity: float):
        """Apply the shared HUD opacity to the teleprompter window."""
        self.setWindowOpacity(max(0.2, min(1.0, float(opacity))))

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        # Enforce GhostPilot screen-share invisibility
        if self.winId():
            hwnd = int(self.winId())
            self._protect_from_screen_capture(hwnd)
            stealth_layer.apply_stealth_window_styles(
                hwnd,
                click_through=False,
                allow_activation=True,
            )
            QTimer.singleShot(0, lambda: self._protect_from_screen_capture(hwnd))

    def _protect_from_screen_capture(self, hwnd: int, attempt: int = 0):
        """Try protection without changing the user's visibility choice."""
        if not self.isVisible() or not self.winId():
            return
        if stealth_layer.enable_screen_share_invisibility(hwnd):
            return
        if attempt < 3:
            QTimer.singleShot(
                100,
                lambda: self._protect_from_screen_capture(hwnd, attempt + 1),
            )
        else:
            self.shield_label.setText("⚠️ SHIELD UNAVAILABLE")

    def set_content(self, text: str):
        """Loads answer lines and starts automatic teleprompter scrolling."""
        lines = [line.strip().lstrip("-*•>0123456789. ") for line in text.split("\n") if line.strip()]
        if lines:
            self.bullets = lines
            self.current_index = 0
            self._update_display()
            self._scroll_timer.start()

    def append_token(self, token: str):
        """Streams live tokens directly into the teleprompter."""
        if not self.bullets:
            self.bullets = [""]
        self.bullets[-1] += token
        self._update_display()
        if not self._scroll_timer.isActive():
            self._scroll_timer.start()

    def prev_bullet(self):
        self._restart_scroll_timer()
        if self.current_index > 0:
            self.current_index -= 1
            self._update_display()

    def next_bullet(self):
        self._restart_scroll_timer()
        if self.current_index < len(self.bullets) - 1:
            self.current_index += 1
            self._update_display()

    def _scroll_to_next_bullet(self):
        """Advance continuously through the answer while it is visible."""
        if not self.isVisible() or len(self.bullets) <= 1:
            return
        self.current_index = (self.current_index + 1) % len(self.bullets)
        self._update_display()

    def _restart_scroll_timer(self):
        if self.isVisible() and len(self.bullets) > 1:
            self._scroll_timer.start()

    def _update_display(self):
        if 0 <= self.current_index < len(self.bullets):
            self.text_label.setText(self.bullets[self.current_index])
            self.counter_label.setText(f"{self.current_index + 1}/{len(self.bullets)}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # High-contrast dark obsidian capsule with neon cyan accent border
        bg_color = QColor(13, 17, 23, 235)
        border_color = QColor(56, 189, 248, 160)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(border_color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)

    # Window Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.prev_bullet()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Right:
            self.next_bullet()
            event.accept()
            return
        super().keyPressEvent(event)
