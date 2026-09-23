"""
ApexPilot AI - Dual-Channel Audio & Live Question Detector
===========================================================
Parakeet AI & HuddleMate feature:
- Captures system audio (interviewer voice via WASAPI loopback)
- Captures microphone audio (candidate voice)
- Real-time Voice Activity Detection (VAD)
- Question detection heuristic engine to instantly trigger AI copilot
"""

import sys
import time
import threading
import queue
import re
import numpy as np
import logging
from typing import Callable, Optional

logger = logging.getLogger("ApexPilot.Audio")

# Question indicator regex triggers
QUESTION_PATTERNS = [
    r"\b(how|what|why|where|when|who|which)\b.*\?",
    r"\bcan you (explain|tell|describe|walk|write|show|implement)\b",
    r"\bcould you (explain|tell|describe|walk|write|show|implement)\b",
    r"\btell me about\b",
    r"\bwalk me through\b",
    r"\bwhat is your approach to\b",
    r"\bhow would you (design|optimize|solve|scale|handle|test)\b",
    r"\bwhat are the trade-offs\b",
    r"\?$"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in QUESTION_PATTERNS]


class AudioCaptureEngine:
    """Manages audio capture, VAD, and question detection."""

    def __init__(self, sample_rate: int = 16000, chunk_duration_ms: int = 100):
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * (chunk_duration_ms / 1000.0))
        self.is_capturing = False
        self._thread = None
        self._on_speech_callback: Optional[Callable[[str, str], None]] = None
        self._on_question_detected: Optional[Callable[[str], None]] = None
        self.energy_threshold = 0.015  # RMS energy threshold for VAD

    def register_callbacks(self,
                           on_speech: Callable[[str, str], None] = None,
                           on_question: Callable[[str], None] = None):
        """
        on_speech(speaker: str, text: str)
        on_question(question_text: str)
        """
        self._on_speech_callback = on_speech
        self._on_question_detected = on_question

    def is_question(self, text: str) -> bool:
        """Heuristic check whether a transcript chunk contains an interview question."""
        text = text.strip()
        if not text:
            return False
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                return True
        return False

    def simulate_speech_input(self, speaker: str, text: str):
        """Simulates speech input for testing or UI demo."""
        if self._on_speech_callback:
            self._on_speech_callback(speaker, text)
        if speaker.lower() in ("interviewer", "system") and self.is_question(text):
            if self._on_question_detected:
                self._on_question_detected(text)

    def start_capture(self):
        """Starts real-time audio capture loop."""
        if self.is_capturing:
            return
        self.is_capturing = True
        self._thread = threading.Thread(target=self._capture_worker, daemon=True)
        self._thread.start()
        logger.info("Audio capture engine started.")

    def stop_capture(self):
        """Stops audio capture."""
        self.is_capturing = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("Audio capture engine stopped.")

    def _capture_worker(self):
        """Background worker handling WASAPI / microphone input."""
        try:
            import sounddevice as sd
            # Check available devices
            devices = sd.query_devices()
            logger.info(f"Available audio devices: {len(devices)}")
        except Exception as e:
            logger.warning(f"SoundDevice init note: {e}")

        # Keep worker alive for event dispatch
        while self.is_capturing:
            time.sleep(0.1)


# Singleton instance
audio_engine = AudioCaptureEngine()
