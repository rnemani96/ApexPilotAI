"""
ApexPilot AI - Master Stealth Overlay HUD
==========================================
Includes:
1. Dynamic Frameless Window Resizing (Edge detection + QSizeGrip)
2. Instant Interruption / Abort (Rapid-fire interviewer question switching)
3. Multi-Provider Streaming & Speculative Race Mode Display
4. GhostPilot Screen-Share Invisibility (WDA_EXCLUDEFROMCAPTURE)
5. LeetCode Screen Snip & Live Audio Question Detector
"""

import sys
import re
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QLineEdit, QSlider, QFrame, QApplication,
    QProgressBar, QSizeGrip
)
from PySide6.QtCore import Qt, QPoint, QRect, Signal, QThread, Slot, QTimer
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QCursor

from core.win32_stealth import stealth_layer
from core.context_store import context_store
from core.llm_client import llm_client
from core.audio_capture import audio_engine
from core.qa_cache import qa_cache
from core.pdf_exporter import pdf_exporter
from ui.snip_overlay import SnipOverlay
from ui.teleprompter_bar import TeleprompterBar
from ui.settings_dialog import SettingsDialog
import logging

logger = logging.getLogger("ApexPilot.Overlay")

EDGE_MARGIN = 8  # Pixels border margin for hit testing resize edges


class StreamingWorker(QThread):
    """Background worker that streams LLM tokens with instant abort support."""

    token_received = Signal(str)
    stream_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, mode: str, query: str):
        super().__init__()
        self.mode = mode
        self.query = query
        self._is_aborted = False

    def abort(self):
        self._is_aborted = True
        llm_client.abort_active_streams()

    def run(self):
        try:
            for token in llm_client.stream_response(self.mode, self.query):
                if self._is_aborted:
                    break
                self.token_received.emit(token)
            self.stream_finished.emit()
        except Exception as e:
            if not self._is_aborted:
                self.error_occurred.emit(str(e))


class OverlayWindow(QWidget):
    """The central stealth HUD for ApexPilot AI with frameless resizing and rapid interruption handling."""

    audio_transcript_received = Signal(str, str)
    audio_question_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.current_mode = "stealth_coder"
        self.is_click_through = False
        self.latest_full_response = ""
        self._teleprompter_answer_started = False
        self.drag_position = QPoint()
        self.worker: StreamingWorker = None
        self.audio_transcript_received.connect(self._display_audio_transcript)
        self.audio_question_received.connect(self._display_audio_question)

        # Resizing states
        self.resizing = False
        self.resize_edge = None  # 'left', 'right', 'top', 'bottom', 'top_left', etc.
        self.drag_start_pos = QPoint()
        self.drag_start_geom = QRect()

        # Child overlays
        self.snip_overlay = SnipOverlay()
        self.snip_overlay.snip_completed.connect(self._on_snip_completed)

        self.teleprompter_bar = TeleprompterBar()
        self.teleprompter_bar.expand_requested.connect(self._show_main_hud)

        self._restore_geometry()
        self._init_ui()
        self._apply_saved_opacity()
        self._setup_audio_hooks()

    def _apply_saved_opacity(self):
        opacity = float(
            context_store.config.get("preferences", {}).get("window_opacity", 0.92)
        )
        value = round(max(0.2, min(1.0, opacity)) * 100)
        self.opacity_slider.setValue(value)
        self._on_opacity_change(value)

    def _restore_geometry(self):
        geom = context_store.get_window_geometry()
        self.setGeometry(
            geom.get("x", 200),
            geom.get("y", 150),
            max(geom.get("width", 740), 450),
            max(geom.get("height", 640), 380)
        )

    def _init_ui(self):
        self.setMinimumSize(450, 380)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(EDGE_MARGIN, EDGE_MARGIN, EDGE_MARGIN, EDGE_MARGIN)

        # Background Container Card with dark obsidian glass styling
        self.card = QFrame(self)
        self.card.setObjectName("MainCard")
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: rgba(13, 17, 23, 245);
                border: 1px solid rgba(56, 189, 248, 160);
                border-radius: 12px;
            }
        """)
        self.card.setMouseTracking(True)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)

        # 1. Top Stealth Header Bar
        header_layout = QHBoxLayout()

        self.shield_badge = QLabel("🛡️ SHIELD: VERIFYING WINDOWS CAPTURE PROTECTION")
        self.shield_badge.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.15); color: #10b981; "
            "border: 1px solid #10b981; border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 11px;"
        )
        header_layout.addWidget(self.shield_badge)

        header_layout.addStretch()

        # Teleprompter Toggle
        self.teleprompter_btn = QPushButton("👁️ Teleprompter")
        self.teleprompter_btn.setStyleSheet(self._button_style("#0284c7"))
        self.teleprompter_btn.clicked.connect(self._toggle_teleprompter_mode)
        header_layout.addWidget(self.teleprompter_btn)

        # Click-Through Toggle
        self.click_thru_btn = QPushButton("🖱️ Click-Thru: OFF")
        self.click_thru_btn.setStyleSheet(self._button_style("#334155"))
        self.click_thru_btn.clicked.connect(self._toggle_click_through)
        header_layout.addWidget(self.click_thru_btn)

        # Settings Button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(30, 26)
        self.settings_btn.setStyleSheet(self._button_style("#1e293b"))
        self.settings_btn.clicked.connect(self._open_settings)
        header_layout.addWidget(self.settings_btn)

        # Minimize/Panic Button
        self.hide_btn = QPushButton("✕")
        self.hide_btn.setFixedSize(30, 26)
        self.hide_btn.setStyleSheet(self._button_style("#dc2626"))
        self.hide_btn.clicked.connect(self._exit_application)
        header_layout.addWidget(self.hide_btn)

        card_layout.addLayout(header_layout)

        # 2. Mode Switcher Bar
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(6)

        self.btn_coder = QPushButton("💻 StealthCoder")
        self.btn_star = QPushButton("🎯 STAR Behavioral")
        self.btn_sys = QPushButton("🏛️ System Design")
        self.btn_meeting = QPushButton("🤝 HuddleMate")

        self.mode_buttons = {
            "stealth_coder": self.btn_coder,
            "star_behavioral": self.btn_star,
            "system_design": self.btn_sys,
            "huddle_mate": self.btn_meeting
        }

        for mode_key, btn in self.mode_buttons.items():
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda checked, m=mode_key: self.set_mode(m))
            mode_layout.addWidget(btn)

        card_layout.addLayout(mode_layout)
        self._update_mode_buttons()

        self.audio_status_label = QLabel(
            "🎙 System audio: listening (transcript appears after speech ends)"
        )
        self.audio_status_label.setStyleSheet(
            "color: #67e8f9; font-size: 10px; padding: 2px 4px;"
        )
        self.audio_status_label.setToolTip(
            "System audio is captured through WASAPI loopback or Stereo Mix. "
            "Recognized speech appears here."
        )
        card_layout.addWidget(self.audio_status_label)

        # 3. Live Question Alert Banner (Parakeet AI)
        self.question_banner = QFrame()
        self.question_banner.setStyleSheet("""
            QFrame {
                background-color: rgba(245, 158, 11, 0.15);
                border: 1px solid #f59e0b;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        qb_layout = QHBoxLayout(self.question_banner)
        qb_layout.setContentsMargins(8, 4, 8, 4)

        self.question_label = QLabel("⚡ Interviewer question detected: '...'")
        self.question_label.setStyleSheet("color: #fbbf24; font-size: 11px; font-weight: 500;")
        qb_layout.addWidget(self.question_label, stretch=1)

        self.auto_solve_btn = QPushButton("⚡ Auto-Solve")
        self.auto_solve_btn.setStyleSheet("background-color: #f59e0b; color: #000000; font-weight: bold; border-radius: 4px; padding: 3px 10px;")
        self.auto_solve_btn.clicked.connect(self._solve_detected_question)
        qb_layout.addWidget(self.auto_solve_btn)

        self.dismiss_qb_btn = QPushButton("✕")
        self.dismiss_qb_btn.setFixedSize(20, 20)
        self.dismiss_qb_btn.setStyleSheet("background: transparent; color: #fbbf24; border: none;")
        self.dismiss_qb_btn.clicked.connect(self.question_banner.hide)
        qb_layout.addWidget(self.dismiss_qb_btn)

        self.question_banner.hide()
        card_layout.addWidget(self.question_banner)

        # 4. Action Toolbar (Snip LeetCode, Copy Clean Code, Language Picker, Custom Instruction tag)
        action_layout = QHBoxLayout()

        self.snip_btn = QPushButton("📷 Snip LeetCode Screen (Ctrl+Alt+S)")
        self.snip_btn.setStyleSheet("background-color: #0284c7; color: #ffffff; border-radius: 6px; padding: 6px 12px; font-weight: bold;")
        self.snip_btn.clicked.connect(self.start_snip)
        action_layout.addWidget(self.snip_btn)

        self.copy_btn = QPushButton("📋 Copy Clean Code")
        self.copy_btn.setStyleSheet("background-color: #1e293b; color: #38bdf8; border: 1px solid #0284c7; border-radius: 6px; padding: 6px 12px; font-weight: bold;")
        self.copy_btn.clicked.connect(self.copy_clean_code)
        action_layout.addWidget(self.copy_btn)

        self.pdf_btn = QPushButton("📁 Saved PDFs")
        self.pdf_btn.setStyleSheet("background-color: #1e293b; color: #10b981; border: 1px solid #059669; border-radius: 6px; padding: 6px 10px; font-weight: bold;")
        self.pdf_btn.clicked.connect(pdf_exporter.open_saved_folder)
        action_layout.addWidget(self.pdf_btn)

        action_layout.addStretch()

        # Opacity Slider
        action_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(92)
        self.opacity_slider.setFixedWidth(80)
        self.opacity_slider.valueChanged.connect(self._on_opacity_change)
        action_layout.addWidget(self.opacity_slider)

        # Tooltips for user-friendly guidance
        self.shield_badge.setToolTip(
            "Uses Windows display-affinity protection when the OS accepts it. "
            "The badge reports the verified result."
        )
        self.teleprompter_btn.setToolTip("Dock into a discreet single-line reader under your webcam (Ctrl+Alt+T)")
        self.click_thru_btn.setToolTip("Toggle click-through mode so clicks pass directly through to your editor")
        self.settings_btn.setToolTip("Open Settings: Configure local/online LLM APIs, custom rules, and profile")
        self.hide_btn.setToolTip("Exit ApexPilot AI and stop all background services")
        self.snip_btn.setToolTip("Screen Snip Tool: Select any LeetCode problem or diagram (Ctrl+Alt+S)")
        self.copy_btn.setToolTip("Silent Copy: Copies clean code without markdown comments to clipboard (Ctrl+Alt+C)")
        self.pdf_btn.setToolTip("Open Folder: Browse all locally saved Q&A PDF documents")
        self.opacity_slider.setToolTip("Adjust window transparency (20% to 100%)")

        card_layout.addLayout(action_layout)

        # 5. Live Streaming Response Area
        self.response_browser = QTextBrowser()
        self.response_browser.setStyleSheet("""
            QTextBrowser {
                background-color: rgba(22, 27, 34, 0.95);
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 14px;
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        self.response_browser.setOpenExternalLinks(True)

        # Friendly startup welcome card
        welcome_md = """### 🦅 ApexPilot AI — Stealth Copilot Active

**Ready for your technical or behavioral interview.**
- 📷 **Snip Code / Problem:** Press `Ctrl + Alt + S` to highlight any problem on screen.
- 🎙️ **Live Audio Detection:** Interacting with interviewers auto-triggers answers.
- 👁️ **Teleprompter Mode:** Press `Ctrl + Alt + T` for a sleek top-bezel eye-contact reader.
- 📋 **Silent Copy:** Press `Ctrl + Alt + C` to copy clean solutions instantly.
- 🛡️ **Screen-share protection:** Windows capture exclusion is requested and verified when supported.
- 📁 **Instant Q&A Cache & PDF:** All solved problems are cached with 0ms retrieval and saved as PDFs.

*Type your question below or press **Ctrl + Alt + S** to begin.*
"""
        self.response_browser.setMarkdown(welcome_md)
        card_layout.addWidget(self.response_browser, stretch=1)

        # 6. Streaming Progress Indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #38bdf8; } QProgressBar { border: none; background: transparent; }")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        card_layout.addWidget(self.progress_bar)

        # 7. Bottom Input Bar with QSizeGrip
        bottom_layout = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.query_input.setPlaceholderText("Type follow-up question or press Ctrl+Alt+S to snip...")
        self.query_input.setStyleSheet("""
            QLineEdit {
                background-color: #161b22;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #38bdf8; }
        """)
        self.query_input.returnPressed.connect(self._on_submit_query)
        bottom_layout.addWidget(self.query_input, stretch=1)

        self.send_btn = QPushButton("⚡ Solve")
        self.send_btn.setStyleSheet("background-color: #0284c7; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold;")
        self.send_btn.clicked.connect(self._on_submit_query)
        self.send_btn.setToolTip("Submit query to reasoning engine")
        bottom_layout.addWidget(self.send_btn)

        # Resizing Grip
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent;")
        bottom_layout.addWidget(self.size_grip, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        card_layout.addLayout(bottom_layout)

        # 8. User-Friendly Shortcut Guide Footer
        footer_layout = QHBoxLayout()
        hint_label = QLabel("⌨️ <b>Ctrl+Alt+S</b> Snip &bull; <b>Ctrl+Alt+X</b> Click-Thru &bull; <b>Ctrl+Alt+T</b> Teleprompter &bull; <b>Ctrl+Alt+H</b> Panic &bull; <i>Drag borders to resize</i>")
        hint_label.setStyleSheet("color: #64748b; font-size: 10px;")
        footer_layout.addWidget(hint_label)
        footer_layout.addStretch()
        card_layout.addLayout(footer_layout)

        main_layout.addWidget(self.card)

    def _button_style(self, bg: str, text: str = "#ffffff") -> str:
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border-radius: 4px;
                border: none;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {bg}; }}
        """

    def showEvent(self, event):
        super().showEvent(event)
        if self.winId():
            hwnd = int(self.winId())
            stealth_layer.apply_stealth_window_styles(
                hwnd,
                click_through=self.is_click_through,
                allow_activation=True,
            )
            self._protect_from_screen_capture(hwnd)
            QTimer.singleShot(0, lambda: self._protect_from_screen_capture(hwnd))
            QTimer.singleShot(250, lambda: self._protect_from_screen_capture(hwnd))

    def _protect_from_screen_capture(self, hwnd: int, attempt: int = 0):
        """Apply capture exclusion after the native HWND is fully realized."""
        if not self.isVisible() or not self.winId():
            return
        if stealth_layer.enable_screen_share_invisibility(hwnd):
            self.shield_badge.setText("🛡️ SHIELD: SCREEN-SHARE PROTECTION ACTIVE")
            return
        if attempt < 3:
            QTimer.singleShot(
                100,
                lambda: self._protect_from_screen_capture(hwnd, attempt + 1),
            )
        else:
            self.shield_badge.setText("⚠️ SHIELD: WINDOWS PROTECTION UNAVAILABLE")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        context_store.save_window_geometry(self.x(), self.y(), self.width(), self.height())

    def moveEvent(self, event):
        super().moveEvent(event)
        context_store.save_window_geometry(self.x(), self.y(), self.width(), self.height())

    # --- Border Resize Hit Testing ---
    def _get_edge_at(self, pos: QPoint) -> Optional[str]:
        """Calculates which border edge or corner the cursor is currently hovering over."""
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = EDGE_MARGIN + 4

        on_left = x < m
        on_right = x > w - m
        on_top = y < m
        on_bottom = y > h - m

        if on_left and on_top: return "top_left"
        if on_right and on_top: return "top_right"
        if on_left and on_bottom: return "bottom_left"
        if on_right and on_bottom: return "bottom_right"
        if on_left: return "left"
        if on_right: return "right"
        if on_top: return "top"
        if on_bottom: return "bottom"
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_edge_at(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.drag_start_pos = event.globalPosition().toPoint()
                self.drag_start_geom = self.geometry()
            else:
                self.resizing = False
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.resizing and self.resize_edge:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            geom = QRect(self.drag_start_geom)

            if "right" in self.resize_edge:
                geom.setWidth(max(self.minimumWidth(), self.drag_start_geom.width() + delta.x()))
            elif "left" in self.resize_edge:
                new_w = max(self.minimumWidth(), self.drag_start_geom.width() - delta.x())
                geom.setLeft(self.drag_start_geom.right() - new_w)

            if "bottom" in self.resize_edge:
                geom.setHeight(max(self.minimumHeight(), self.drag_start_geom.height() + delta.y()))
            elif "top" in self.resize_edge:
                new_h = max(self.minimumHeight(), self.drag_start_geom.height() - delta.y())
                geom.setTop(self.drag_start_geom.bottom() - new_h)

            self.setGeometry(geom)
            return

        # Update cursor shape based on hover position
        if not event.buttons():
            edge = self._get_edge_at(event.pos())
            if edge in ("left", "right"):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif edge in ("top", "bottom"):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif edge in ("top_left", "bottom_right"):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edge in ("top_right", "bottom_left"):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            else:
                self.unsetCursor()

        # Normal window dragging
        if event.buttons() == Qt.MouseButton.LeftButton and not self.resizing:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_edge = None
        self.unsetCursor()

    # --- Live Audio Question Detection ---
    def _setup_audio_hooks(self):
        audio_engine.register_callbacks(
            on_speech=self._on_audio_speech,
            on_question=self._on_audio_question
        )

    def _on_audio_speech(self, speaker: str, text: str):
        self.audio_transcript_received.emit(speaker, text)

    @Slot(str, str)
    def _display_audio_transcript(self, speaker: str, text: str):
        source = "System" if speaker.lower() in ("system", "interviewer") else "Microphone"
        self.audio_status_label.setText(f"🎙 {source} audio captured: {text}")
        context_store.add_transcript_entry(speaker, text)

    def _on_audio_question(self, question_text: str):
        self.audio_question_received.emit(question_text)

    @Slot(str)
    def _display_audio_question(self, question_text: str):
        self.question_label.setText(f"⚡ Question detected: \"{question_text[:75]}...\"")
        self.detected_question_text = question_text
        self.question_banner.show()
        self._auto_solve_detected_question()

    def _auto_solve_detected_question(self):
        if getattr(self, "detected_question_text", ""):
            self.execute_query(self.detected_question_text)

    def _solve_detected_question(self):
        self.question_banner.hide()
        if hasattr(self, "detected_question_text"):
            self.execute_query(self.detected_question_text)

    def set_mode(self, mode: str):
        self.current_mode = mode
        self._update_mode_buttons()

    def _update_mode_buttons(self):
        for m, btn in self.mode_buttons.items():
            if m == self.current_mode:
                btn.setStyleSheet("background-color: #0284c7; color: #ffffff; border: 1px solid #38bdf8; border-radius: 4px; font-weight: bold; font-size: 11px;")
            else:
                btn.setStyleSheet("background-color: #1e293b; color: #94a3b8; border: 1px solid #334155; border-radius: 4px; font-size: 11px;")

    def start_snip(self):
        self.snip_overlay.start_snip()

    def _on_snip_completed(self, text: str):
        self.show()
        if text and text.strip():
            if text.startswith("[OCR failed]"):
                self.query_input.setPlaceholderText(text)
                self.query_input.clear()
                return
            self.query_input.setText(text)
            self.execute_query(text)

    def _on_submit_query(self):
        query = self.query_input.text().strip()
        if query:
            self.execute_query(query)

    def execute_query(self, query: str):
        """
        Executes query with:
        1. Instant QA Cache Lookup (0ms latency, zero API costs)
        2. Rapid Interruption Handling (aborts previous stream if still running)
        3. Real-time streaming from local/online LLM
        4. Automatic local PDF generation on completion
        """
        if self.worker and self.worker.isRunning():
            logger.info(
                "Interruption detected! Aborting previous stream before starting the new answer..."
            )
            self.worker.abort()
            if not self.worker.wait(3000):
                logger.warning(
                    "Previous answer is still stopping; deferring the new question."
                )
                QTimer.singleShot(100, lambda: self.execute_query(query))
                return
            self.worker.deleteLater()
            self.worker = None

        # 1. Check QA Cache for Instant Response
        cached = qa_cache.lookup(query, mode=self.current_mode)
        if cached:
            cached_answer = cached.get("answer", "")
            pdf_path = cached.get("pdf_path", "")
            self.latest_full_response = cached_answer

            badge = "⚡ **[INSTANT CACHE HIT — 0ms Latency | Saved Local PDF]**\n\n"
            if pdf_path:
                badge += f"*📄 Local PDF Archive: `{pdf_path}`*\n\n---\n\n"
            self.response_browser.setMarkdown(badge + cached_answer)
            self.progress_bar.hide()

            if self.teleprompter_bar.isVisible():
                self.teleprompter_bar.set_content(cached_answer)
                self._teleprompter_answer_started = True
            return

        # 2. Not in cache -> Stream from LLM
        self.current_query = query
        self.latest_full_response = ""
        self.response_browser.setMarkdown(f"⚡ **Generating optimal solution ({self.current_mode})...**\n\n")
        self.progress_bar.show()
        if self.teleprompter_bar.isVisible():
            self.teleprompter_bar.set_content("Listening for the answer...")
        self._teleprompter_answer_started = False

        self.worker = StreamingWorker(self.current_mode, query)
        self.worker.token_received.connect(self._on_token)
        self.worker.stream_finished.connect(self._on_stream_finished)
        self.worker.error_occurred.connect(self._on_stream_error)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    @Slot()
    def _on_worker_finished(self):
        """Release a worker only after Qt confirms its thread has stopped."""
        worker = self.sender()
        if worker is self.worker and not worker.isRunning():
            worker.deleteLater()
            self.worker = None

    @Slot(str)
    def _on_token(self, token: str):
        self.latest_full_response += token
        self.response_browser.setMarkdown(self.latest_full_response)
        sb = self.response_browser.verticalScrollBar()
        sb.setValue(sb.maximum())

        if self.teleprompter_bar.isVisible():
            if not self._teleprompter_answer_started:
                self.teleprompter_bar.set_content(token)
                self._teleprompter_answer_started = True
            else:
                self.teleprompter_bar.append_token(token)

    @Slot()
    def _on_stream_finished(self):
        self.progress_bar.hide()
        if self.teleprompter_bar.isVisible():
            self.teleprompter_bar.set_content(self.latest_full_response)

        # Auto-save question & solution to local cache and generate local PDF
        if hasattr(self, "current_query") and self.current_query and self.latest_full_response:
            # Do not permanently cache an outage notice as if it were an answer.
            # The next attempt should be able to use a newly available provider.
            cacheable = not self.latest_full_response.lstrip().startswith(
                ("⚠️ **[All configured endpoints offline", "### Offline fallback")
            )
            if not cacheable:
                return
            try:
                qa_cache.store(self.current_query, self.latest_full_response, self.current_mode, "ai")
            except Exception as e:
                logger.warning(f"Failed to auto-archive Q&A to PDF/cache: {e}")

    @Slot(str)
    def _on_stream_error(self, err: str):
        self.progress_bar.hide()
        self.response_browser.append(f"\n\n**Error:** {err}")

    def copy_clean_code(self):
        """Extracts code block from latest response and copies it cleanly to clipboard."""
        code_blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", self.latest_full_response)
        clipboard = QApplication.clipboard()
        if code_blocks:
            clean_code = code_blocks[0].strip()
            clipboard.setText(clean_code)
            self.copy_btn.setText("✅ Code Copied!")
        else:
            clipboard.setText(self.latest_full_response)
            self.copy_btn.setText("✅ Text Copied!")

        from PySide6.QtCore import QTimer
        QTimer.singleShot(1800, lambda: self.copy_btn.setText("📋 Copy Clean Code"))

    def _toggle_click_through(self):
        self.is_click_through = not self.is_click_through
        if self.winId():
            stealth_layer.set_click_through(int(self.winId()), self.is_click_through)

        if self.is_click_through:
            self.click_thru_btn.setText("🖱️ Click-Thru: ON (Ctrl+Alt+X)")
            self.click_thru_btn.setStyleSheet(self._button_style("#10b981"))
        else:
            self.click_thru_btn.setText("🖱️ Click-Thru: OFF")
            self.click_thru_btn.setStyleSheet(self._button_style("#334155"))

    def _toggle_teleprompter_mode(self):
        """Manually toggle the teleprompter; protection status never hides it."""
        if self.teleprompter_bar.isVisible():
            self.teleprompter_bar.hide()
            self.show()
        else:
            self.hide()
            if self.latest_full_response:
                self.teleprompter_bar.set_content(self.latest_full_response)
            self.teleprompter_bar.show()

    def _show_main_hud(self):
        self.teleprompter_bar.hide()
        self.show()

    def _exit_application(self):
        """Stop active work and terminate the application from the close button."""
        if self.worker and self.worker.isRunning():
            self.worker.abort()
            if not self.worker.wait(5000):
                logger.warning("Answer worker did not stop before application shutdown.")
        self.snip_overlay.close()
        self.teleprompter_bar.close()
        app = QApplication.instance()
        if app:
            app.quit()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def _on_opacity_change(self, val: int):
        opacity = max(0.2, min(1.0, val / 100.0))
        self.setWindowOpacity(opacity)
        self.teleprompter_bar.set_opacity(opacity)
        context_store.config.setdefault("preferences", {})["window_opacity"] = opacity
        context_store.save()
