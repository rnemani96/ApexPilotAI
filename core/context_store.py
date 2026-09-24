"""
ApexPilot AI - Context & Configuration Store
=============================================
Manages persistent candidate profile, interview settings, custom instructions,
online LLM API keys (ChatGPT, Grok, Claude, Groq, DeepSeek, Gemini),
rate-limit failover configuration, and window geometry.
"""

import json
import copy
import time
import threading
from pathlib import Path
import logging

logger = logging.getLogger("ApexPilot.Context")

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

DEFAULT_CONFIG = {
    "llm": {
        "provider": "ollama",  # 'ollama', 'llama_cpp', 'lm_studio', 'openai', 'grok', 'groq', 'claude', 'deepseek', 'gemini', 'mock'
        "base_url": "http://127.0.0.1:11434",
        "model": "qwen2.5:3b",
        "temperature": 0.2,
        "max_tokens": 1500,
        "timeout_seconds": 15
    },
    "online_providers": {
        "openai": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o",
            "enabled": False
        },
        "grok": {
            "api_key": "",
            "base_url": "https://api.x.ai/v1",
            "model": "grok-2",
            "enabled": False
        },
        "groq": {
            "api_key": "",
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.3-70b-versatile",
            "enabled": False
        },
        "claude": {
            "api_key": "",
            "base_url": "https://api.anthropic.com/v1",
            "model": "claude-3-5-sonnet-20241022",
            "enabled": False
        },
        "deepseek": {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "enabled": False
        },
        "gemini": {
            "api_key": "",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model": "gemini-2.0-flash",
            "enabled": False
        }
    },
    "custom_endpoints": [
        # Unlimited custom online LLM endpoints (OpenRouter, Mistral, Perplexity, Together, Local LAN, etc.)
    ],
    "routing": {
        "auto_failover_on_rate_limit": True,
        "fastest_first_race": False  # Speculative duel between Local LLM and Online LLM
    },
    "custom_instructions": "",  # Optional user instructions to override or guide answer style
    "preferences": {
        "coding_language": "Python",
        "window_opacity": 0.92,
        "screen_share_shield": True,
        "click_through": False,
        "teleprompter_mode": False,
        "system_audio_only": False,
        "speech_languages": ["en-US", "en-IN", "en-GB"],
        "whisper_model": "small.en"
    },
    "window_geometry": {
        "x": 200,
        "y": 150,
        "width": 740,
        "height": 640
    },
    "hotkeys": {
        "panic_hide": "ctrl+alt+h",
        "snip_ocr": "ctrl+alt+s",
        "generate_answer": "ctrl+alt+a",
        "toggle_teleprompter": "ctrl+alt+t",
        "silent_copy": "ctrl+alt+c"
    },
    "profile": {
        "candidate_name": "Senior Software Engineer",
        "resume": "8+ years experience building distributed microservices, low-latency trading pipelines, and cloud native architectures in Python, Go, and C++. Led migration from monolith to Kubernetes saving 40% compute costs.",
        "job_description": "Staff Software Engineer - Distributed Systems. Looking for deep knowledge in high-throughput messaging, database internals, and concurrency."
    }
}


class ContextStore:
    """Manages persistent candidate profile, interview settings, and active session transcript."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load()
        self.session_transcript = []
        self._save_lock = threading.Lock()

    def _load(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return self._deep_merge(copy.deepcopy(DEFAULT_CONFIG), data)
            except Exception as e:
                logger.error(f"Error loading config, using defaults: {e}")
        return copy.deepcopy(DEFAULT_CONFIG)

    @staticmethod
    def _deep_merge(defaults: dict, overrides: dict) -> dict:
        """Merge nested configuration sections without dropping default keys."""
        for key, value in overrides.items():
            if isinstance(value, dict) and isinstance(defaults.get(key), dict):
                ContextStore._deep_merge(defaults[key], value)
            else:
                defaults[key] = value
        return defaults

    def save(self):
        """Persists current configuration to disk."""
        with self._save_lock:
            temp_path = self.config_path.with_name(
                f"{self.config_path.name}.{threading.get_ident()}.tmp"
            )
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2)
                for attempt in range(3):
                    try:
                        temp_path.replace(self.config_path)
                        logger.debug("Saved config to disk.")
                        break
                    except PermissionError:
                        if attempt == 2:
                            raise
                        time.sleep(0.05 * (attempt + 1))
            except Exception as e:
                logger.error(f"Failed to save config: {e}")
            finally:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def get_llm_config(self) -> dict:
        return self.config.get("llm", DEFAULT_CONFIG["llm"])

    def get_online_providers(self) -> dict:
        return self.config.get("online_providers", DEFAULT_CONFIG["online_providers"])

    def get_custom_endpoints(self) -> list[dict]:
        return self.config.get("custom_endpoints", [])

    def add_custom_endpoint(self, name: str, base_url: str, api_key: str, model: str, enabled: bool = True) -> dict:
        endpoint = {
            "id": f"custom_{int(time.time() * 1000)}",
            "name": name,
            "base_url": base_url.rstrip("/"),
            "api_key": api_key,
            "model": model,
            "enabled": enabled
        }
        if "custom_endpoints" not in self.config:
            self.config["custom_endpoints"] = []
        self.config["custom_endpoints"].append(endpoint)
        self.save()
        return endpoint

    def delete_custom_endpoint(self, endpoint_id: str):
        if "custom_endpoints" in self.config:
            self.config["custom_endpoints"] = [e for e in self.config["custom_endpoints"] if e.get("id") != endpoint_id]
            self.save()

    def get_routing_config(self) -> dict:
        return self.config.get("routing", DEFAULT_CONFIG["routing"])

    def get_custom_instructions(self) -> str:
        return self.config.get("custom_instructions", "").strip()

    def set_custom_instructions(self, instructions: str):
        self.config["custom_instructions"] = instructions
        self.save()

    def get_profile(self) -> dict:
        return self.config.get("profile", DEFAULT_CONFIG["profile"])

    def update_profile(self, resume: str = None, jd: str = None, language: str = None):
        if resume is not None:
            self.config["profile"]["resume"] = resume
        if jd is not None:
            self.config["profile"]["job_description"] = jd
        if language is not None:
            self.config["preferences"]["coding_language"] = language
        self.save()

    def save_window_geometry(self, x: int, y: int, width: int, height: int):
        self.config["window_geometry"] = {
            "x": x, "y": y, "width": width, "height": height
        }
        self.save()

    def get_window_geometry(self) -> dict:
        return self.config.get("window_geometry", DEFAULT_CONFIG["window_geometry"])

    def add_transcript_entry(self, speaker: str, text: str):
        self.session_transcript.append({"speaker": speaker, "text": text})
        if len(self.session_transcript) > 20:
            self.session_transcript.pop(0)

    def get_recent_transcript_text(self) -> str:
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in self.session_transcript])


context_store = ContextStore()
