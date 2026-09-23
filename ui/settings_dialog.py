"""
ApexPilot AI - Settings & Profile Configuration
================================================
Configures:
- Local & Unlimited Online LLMs (Ollama, OpenAI/ChatGPT, Grok, Groq, Claude, DeepSeek, Gemini, OpenRouter, Mistral, Perplexity, Together AI, Custom)
- Rate Limit Auto-Failover (429) & Fastest-First Race Mode
- User Custom Instructions
- Candidate Resume & Job Description ingestion
- Coding Language, Saved PDF archives & Stealth preferences
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QSlider, QTabWidget,
    QWidget, QMessageBox, QGroupBox, QCheckBox, QScrollArea,
    QFrame
)
from PySide6.QtCore import Qt
from core.context_store import context_store
from core.llm_client import llm_client
from core.pdf_exporter import pdf_exporter
import logging

logger = logging.getLogger("ApexPilot.Settings")

PRESET_ENDPOINTS = {
    "OpenRouter": ("https://openrouter.ai/api/v1", "anthropic/claude-3.5-sonnet"),
    "Mistral AI": ("https://api.mistral.ai/v1", "mistral-large-latest"),
    "Perplexity": ("https://api.perplexity.ai", "sonar-pro"),
    "Together AI": ("https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
    "DeepInfra": ("https://api.deepinfra.com/v1/openai", "meta-llama/Meta-Llama-3.1-70B-Instruct"),
    "Custom Endpoint": ("https://your-api-domain.com/v1", "custom-model")
}


class SettingsDialog(QDialog):
    """Settings dialog covering Local & Unlimited Online LLMs, API pools, custom instructions, and profile."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ApexPilot AI - Configuration & API Pool")
        self.setFixedSize(720, 620)
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: #f8fafc; }
            QLabel { color: #cbd5e1; font-size: 12px; }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1e293b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #38bdf8;
            }
            QPushButton {
                background-color: #0284c7;
                color: #ffffff;
                border-radius: 6px;
                padding: 7px 14px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #0369a1; }
            QTabWidget::pane { border: 1px solid #334155; background: #0f172a; border-radius: 6px; }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 8px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 11px;
            }
            QTabBar::tab:selected { background: #0284c7; color: #ffffff; font-weight: bold; }
            QCheckBox { color: #f8fafc; font-size: 12px; }
        """)

        self.custom_endpoint_widgets = []
        self._init_ui()
        self._load_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Tab 1: Local LLM Engine & Routing
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)

        llm_group = QGroupBox("Primary / Local LLM Server")
        llm_group.setStyleSheet("QGroupBox { color: #38bdf8; font-weight: bold; border: 1px solid #334155; margin-top: 10px; padding: 12px; }")
        g_layout = QVBoxLayout(llm_group)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Primary Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["ollama", "llama_cpp", "lm_studio", "openai", "grok", "groq", "claude", "deepseek", "gemini", "mock"])
        h1.addWidget(self.provider_combo)
        g_layout.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Local Base URL:"))
        self.url_edit = QLineEdit()
        h2.addWidget(self.url_edit)
        g_layout.addLayout(h2)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Local Model:"))
        self.model_edit = QLineEdit()
        h3.addWidget(self.model_edit)
        g_layout.addLayout(h3)

        h_test = QHBoxLayout()
        self.test_btn = QPushButton("⚡ Test Primary Connection")
        self.test_btn.clicked.connect(self._test_connection)
        self.status_label = QLabel("Status: Ready to test")
        self.status_label.setStyleSheet("color: #94a3b8; font-style: italic;")
        h_test.addWidget(self.test_btn)
        h_test.addWidget(self.status_label, stretch=1)
        g_layout.addLayout(h_test)

        llm_layout.addWidget(llm_group)

        # Routing & Duel Engine Group
        route_group = QGroupBox("Fastest-First Race & 429 Failover")
        route_group.setStyleSheet("QGroupBox { color: #10b981; font-weight: bold; border: 1px solid #334155; margin-top: 10px; padding: 12px; }")
        rg_layout = QVBoxLayout(route_group)

        self.race_check = QCheckBox("⚡ Fastest-First Race Mode (Speculative Duel: Local vs Online LLM parallel race)")
        rg_layout.addWidget(self.race_check)

        self.failover_check = QCheckBox("🔄 Automatic 429 Rate-Limit Failover (Rotates to next API key/provider if rate-limited)")
        rg_layout.addWidget(self.failover_check)

        llm_layout.addWidget(route_group)

        # Coding Language
        h_lang = QHBoxLayout()
        h_lang.addWidget(QLabel("StealthCoder Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Python", "C++", "Java", "Go", "TypeScript", "Rust", "C#"])
        h_lang.addWidget(self.lang_combo)
        llm_layout.addLayout(h_lang)

        llm_layout.addStretch()
        self.tabs.addTab(llm_tab, "⚡ Local & Routing")

        # Tab 2: Online LLM API Pool (Pre-configured + Unlimited Custom Endpoints)
        api_tab = QWidget()
        api_scroll = QScrollArea(api_tab)
        api_scroll.setWidgetResizable(True)
        api_scroll_content = QWidget()
        self.api_layout = QVBoxLayout(api_scroll_content)

        self.api_layout.addWidget(QLabel("<b>Configure Online LLM API Keys for Auto-Failover & Fastest-First Duel:</b>"))

        self.api_inputs = {}
        providers_info = [
            ("openai", "OpenAI (ChatGPT)", "sk-...", "gpt-4o"),
            ("grok", "xAI (Grok)", "xai-...", "grok-2"),
            ("groq", "Groq (Ultra-Fast LPU 300+ tok/s)", "gsk_...", "llama-3.3-70b-versatile"),
            ("claude", "Anthropic (Claude)", "sk-ant-...", "claude-3-5-sonnet-20241022"),
            ("deepseek", "DeepSeek", "sk-...", "deepseek-chat"),
            ("gemini", "Google Gemini", "AIzaSy...", "gemini-2.0-flash")
        ]

        for p_id, p_label, placeholder, default_model in providers_info:
            box = QGroupBox(p_label)
            box.setStyleSheet("QGroupBox { color: #38bdf8; font-weight: bold; border: 1px solid #334155; margin-top: 6px; padding: 8px; }")
            blayout = QVBoxLayout(box)

            h_key = QHBoxLayout()
            enable_cb = QCheckBox("Enable")
            key_in = QLineEdit()
            key_in.setEchoMode(QLineEdit.EchoMode.Password)
            key_in.setPlaceholderText(placeholder)
            model_in = QLineEdit()
            model_in.setPlaceholderText(default_model)
            model_in.setFixedWidth(140)

            h_key.addWidget(enable_cb)
            h_key.addWidget(QLabel("API Key:"))
            h_key.addWidget(key_in, stretch=1)
            h_key.addWidget(QLabel("Model:"))
            h_key.addWidget(model_in)

            blayout.addLayout(h_key)
            self.api_layout.addWidget(box)

            self.api_inputs[p_id] = {
                "enable": enable_cb,
                "key": key_in,
                "model": model_in
            }

        # Unlimited Custom Endpoints Section
        custom_header = QLabel("<b>➕ Add Any Custom / Unlimited Online LLM Endpoint:</b>")
        custom_header.setStyleSheet("color: #a855f7; margin-top: 14px;")
        self.api_layout.addWidget(custom_header)

        add_box = QGroupBox("New Custom Endpoint")
        add_box.setStyleSheet("QGroupBox { color: #c084fc; font-weight: bold; border: 1px solid #475569; padding: 10px; }")
        ab_layout = QVBoxLayout(add_box)

        # Preset selector
        h_pre = QHBoxLayout()
        h_pre.addWidget(QLabel("Preset Template:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PRESET_ENDPOINTS.keys()))
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)
        h_pre.addWidget(self.preset_combo, stretch=1)
        ab_layout.addLayout(h_pre)

        # Name & URL
        h_n_u = QHBoxLayout()
        h_n_u.addWidget(QLabel("Name:"))
        self.new_endpoint_name = QLineEdit()
        self.new_endpoint_name.setPlaceholderText("e.g. OpenRouter")
        h_n_u.addWidget(self.new_endpoint_name)

        h_n_u.addWidget(QLabel("Base URL:"))
        self.new_endpoint_url = QLineEdit()
        self.new_endpoint_url.setPlaceholderText("https://openrouter.ai/api/v1")
        h_n_u.addWidget(self.new_endpoint_url, stretch=1)
        ab_layout.addLayout(h_n_u)

        # Key & Model
        h_k_m = QHBoxLayout()
        h_k_m.addWidget(QLabel("API Key:"))
        self.new_endpoint_key = QLineEdit()
        self.new_endpoint_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_endpoint_key.setPlaceholderText("sk-...")
        h_k_m.addWidget(self.new_endpoint_key, stretch=1)

        h_k_m.addWidget(QLabel("Model:"))
        self.new_endpoint_model = QLineEdit()
        self.new_endpoint_model.setPlaceholderText("model name")
        h_k_m.addWidget(self.new_endpoint_model)

        self.add_endpoint_btn = QPushButton("➕ Add Endpoint")
        self.add_endpoint_btn.setStyleSheet("background-color: #9333ea; color: white;")
        self.add_endpoint_btn.clicked.connect(self._add_custom_endpoint)
        h_k_m.addWidget(self.add_endpoint_btn)
        ab_layout.addLayout(h_k_m)

        self.api_layout.addWidget(add_box)

        # Container for Active Custom Endpoints
        self.custom_list_container = QVBoxLayout()
        self.api_layout.addLayout(self.custom_list_container)

        api_scroll.setWidget(api_scroll_content)
        t2_layout = QVBoxLayout(api_tab)
        t2_layout.addWidget(api_scroll)
        self.tabs.addTab(api_tab, "🌐 Online API Pool")

        # Tab 3: Custom User Instructions
        custom_tab = QWidget()
        custom_layout = QVBoxLayout(custom_tab)
        custom_layout.addWidget(QLabel("<b>Custom Instructions (Optional):</b>"))
        custom_layout.addWidget(QLabel("Provide custom rules or persona instructions. The AI will strictly follow these in every answer.\n(Leave blank to behave normally like all standard programs)."))

        self.custom_instructions_edit = QTextEdit()
        self.custom_instructions_edit.setPlaceholderText(
            "Examples:\n"
            "- 'Keep all coding solutions in modern C++20 with vector and unordered_map.'\n"
            "- 'Keep answers under 3 concise bullet points.'\n"
            "- 'Pretend I am a Principal Architect with 12 years of experience.'\n"
            "- 'Always analyze both average and worst-case time complexity at the very top.'"
        )
        custom_layout.addWidget(self.custom_instructions_edit)
        self.tabs.addTab(custom_tab, "✍️ Custom Instructions")

        # Tab 4: Candidate Resume Context (Final Round AI)
        resume_tab = QWidget()
        resume_layout = QVBoxLayout(resume_tab)
        resume_layout.addWidget(QLabel("Candidate Resume & Experience Context:"))
        self.resume_text = QTextEdit()
        self.resume_text.setPlaceholderText("Paste your resume summary, past company projects, metrics, and skills here...")
        resume_layout.addWidget(self.resume_text)

        resume_layout.addWidget(QLabel("Target Job Description (JD):"))
        self.jd_text = QTextEdit()
        self.jd_text.setPlaceholderText("Paste target role description, key tech stack requirements...")
        self.jd_text.setMaximumHeight(80)
        resume_layout.addWidget(self.jd_text)
        self.tabs.addTab(resume_tab, "📄 Resume Context")

        # Tab 5: Stealth & Hotkeys
        hotkey_tab = QWidget()
        hotkey_layout = QVBoxLayout(hotkey_tab)
        hotkey_layout.addWidget(QLabel("<b>GhostPilot & Stealth Controls:</b>"))
        hotkey_layout.addWidget(QLabel("• <b>Ctrl + Alt + H</b>: Instant Panic / Boss Key (Hide/Unhide HUD)"))
        hotkey_layout.addWidget(QLabel("• <b>Ctrl + Alt + S</b>: Screen Snipping Tool (OCR LeetCode Problem)"))
        hotkey_layout.addWidget(QLabel("• <b>Ctrl + Alt + A</b>: Instant Generate Answer on Highlight/Last Question"))
        hotkey_layout.addWidget(QLabel("• <b>Ctrl + Alt + T</b>: Toggle Minimalist Webcam Teleprompter"))
        hotkey_layout.addWidget(QLabel("• <b>Ctrl + Alt + C</b>: Silent Copy Code / Answer to Clipboard"))
        hotkey_layout.addSpacing(10)
        hotkey_layout.addWidget(QLabel("<b>Dynamic Resizing:</b> Drag any border or corner of the HUD to resize freely."))
        hotkey_layout.addSpacing(10)

        # PDF Folder Button in Settings
        self.open_pdf_btn = QPushButton("📁 Open Saved PDF Question Archives")
        self.open_pdf_btn.setStyleSheet("background-color: #059669; color: white; padding: 8px 16px;")
        self.open_pdf_btn.clicked.connect(pdf_exporter.open_saved_folder)
        hotkey_layout.addWidget(self.open_pdf_btn)

        hotkey_layout.addStretch()
        self.tabs.addTab(hotkey_tab, "🛡️ Stealth & Storage")

        main_layout.addWidget(self.tabs)

        # Bottom Action Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save & Apply")
        self.save_btn.clicked.connect(self._save_and_close)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #334155;")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

        # Initialize first preset
        self._on_preset_selected("OpenRouter")

    def _on_preset_selected(self, preset_name: str):
        if preset_name in PRESET_ENDPOINTS:
            url, model = PRESET_ENDPOINTS[preset_name]
            self.new_endpoint_name.setText(preset_name)
            self.new_endpoint_url.setText(url)
            self.new_endpoint_model.setText(model)

    def _add_custom_endpoint(self):
        name = self.new_endpoint_name.text().strip()
        url = self.new_endpoint_url.text().strip()
        key = self.new_endpoint_key.text().strip()
        model = self.new_endpoint_model.text().strip()

        if not name or not url:
            QMessageBox.warning(self, "Invalid Endpoint", "Please specify both a Name and Base URL.")
            return

        endpoint = context_store.add_custom_endpoint(name, url, key, model, enabled=True)
        self._render_custom_endpoint_item(endpoint)

        self.new_endpoint_key.clear()
        QMessageBox.information(self, "Endpoint Added", f"Custom endpoint '{name}' added to pool successfully!")

    def _render_custom_endpoint_item(self, endpoint: dict):
        e_id = endpoint.get("id")
        frame = QFrame()
        frame.setStyleSheet("QFrame { background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 6px; margin-top: 4px; }")
        flayout = QHBoxLayout(frame)
        flayout.setContentsMargins(6, 4, 6, 4)

        enable_cb = QCheckBox(endpoint.get("name", "Custom"))
        enable_cb.setChecked(endpoint.get("enabled", True))
        enable_cb.toggled.connect(lambda val, eid=e_id: self._toggle_custom_endpoint(eid, val))
        flayout.addWidget(enable_cb)

        url_lbl = QLabel(f"URL: {endpoint.get('base_url')[:30]}...")
        url_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        flayout.addWidget(url_lbl, stretch=1)

        model_lbl = QLabel(f"Model: {endpoint.get('model')}")
        model_lbl.setStyleSheet("color: #38bdf8; font-size: 11px;")
        flayout.addWidget(model_lbl)

        del_btn = QPushButton("🗑️")
        del_btn.setFixedSize(26, 22)
        del_btn.setStyleSheet("background: #dc2626; color: white; border: none; border-radius: 4px;")
        del_btn.clicked.connect(lambda checked, eid=e_id, f=frame: self._delete_custom_endpoint(eid, f))
        flayout.addWidget(del_btn)

        self.custom_list_container.addWidget(frame)
        self.custom_endpoint_widgets.append((e_id, frame, enable_cb))

    def _toggle_custom_endpoint(self, endpoint_id: str, enabled: bool):
        for e in context_store.config.get("custom_endpoints", []):
            if e.get("id") == endpoint_id:
                e["enabled"] = enabled
        context_store.save()

    def _delete_custom_endpoint(self, endpoint_id: str, frame: QFrame):
        context_store.delete_custom_endpoint(endpoint_id)
        frame.deleteLater()
        self.custom_endpoint_widgets = [t for t in self.custom_endpoint_widgets if t[0] != endpoint_id]

    def _load_values(self):
        llm = context_store.get_llm_config()
        self.provider_combo.setCurrentText(llm.get("provider", "ollama"))
        self.url_edit.setText(llm.get("base_url", "http://127.0.0.1:11434"))
        self.model_edit.setText(llm.get("model", "qwen2.5-coder:7b"))

        routing = context_store.get_routing_config()
        self.race_check.setChecked(routing.get("fastest_first_race", False))
        self.failover_check.setChecked(routing.get("auto_failover_on_rate_limit", True))

        online_providers = context_store.get_online_providers()
        for p_id, widgets in self.api_inputs.items():
            if p_id in online_providers:
                p_cfg = online_providers[p_id]
                widgets["enable"].setChecked(p_cfg.get("enabled", False))
                widgets["key"].setText(p_cfg.get("api_key", ""))
                widgets["model"].setText(p_cfg.get("model", ""))

        # Load Custom Endpoints
        for endpoint in context_store.get_custom_endpoints():
            self._render_custom_endpoint_item(endpoint)

        self.custom_instructions_edit.setPlainText(context_store.get_custom_instructions())

        profile = context_store.get_profile()
        self.resume_text.setPlainText(profile.get("resume", ""))
        self.jd_text.setPlainText(profile.get("job_description", ""))

        prefs = context_store.config.get("preferences", {})
        self.lang_combo.setCurrentText(prefs.get("coding_language", "Python"))

    def _test_connection(self):
        context_store.config["llm"]["provider"] = self.provider_combo.currentText()
        context_store.config["llm"]["base_url"] = self.url_edit.text()
        context_store.config["llm"]["model"] = self.model_edit.text()

        self.status_label.setText("Testing connection...")
        online, msg, models = llm_client.check_health()
        if online:
            self.status_label.setText(f"✅ {msg}")
            self.status_label.setStyleSheet("color: #00ffaa; font-weight: bold;")
        else:
            self.status_label.setText(f"❌ {msg}")
            self.status_label.setStyleSheet("color: #ff5555;")

    def _save_and_close(self):
        context_store.config["llm"]["provider"] = self.provider_combo.currentText()
        context_store.config["llm"]["base_url"] = self.url_edit.text().strip()
        context_store.config["llm"]["model"] = self.model_edit.text().strip()
        context_store.config["preferences"]["coding_language"] = self.lang_combo.currentText()

        context_store.config["routing"]["fastest_first_race"] = self.race_check.isChecked()
        context_store.config["routing"]["auto_failover_on_rate_limit"] = self.failover_check.isChecked()

        for p_id, widgets in self.api_inputs.items():
            if p_id in context_store.config["online_providers"]:
                context_store.config["online_providers"][p_id]["enabled"] = widgets["enable"].isChecked()
                context_store.config["online_providers"][p_id]["api_key"] = widgets["key"].text().strip()
                if widgets["model"].text().strip():
                    context_store.config["online_providers"][p_id]["model"] = widgets["model"].text().strip()

        context_store.set_custom_instructions(self.custom_instructions_edit.toPlainText().strip())

        context_store.config["profile"]["resume"] = self.resume_text.toPlainText().strip()
        context_store.config["profile"]["job_description"] = self.jd_text.toPlainText().strip()
        context_store.save()
        self.accept()
