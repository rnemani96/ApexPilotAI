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
    r"^\s*(how|what|why|where|when|who|which)\b(?:\s+\w+){2,}",
    r"\bcan you (explain|tell|describe|walk|write|show|implement)\b",
    r"\bcould you (explain|tell|describe|walk|write|show|implement)\b",
    r"\b(can|could|would|will) you (explain|tell|describe|walk|write|show|implement|design|scale|handle|compare)\b",
    r"\btell me about\b",
    r"\bwalk me through\b",
    r"\bwhat is your approach to\b",
    r"\bhow would you (design|optimize|solve|scale|handle|test)\b",
    r"\bwhat are the trade-offs\b",
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
        self.energy_threshold = 0.005  # Quiet meeting/system audio VAD threshold
        # Keep enough context for speech recognition to hear a complete
        # interview question. Shorter windows frequently produce fragments.
        self.max_segment_seconds = 6.0
        self.silence_duration_seconds = 0.8
        self._streams = []
        self._loopback_thread = None
        self._loopback_stop = threading.Event()
        self._last_speech_at = 0.0
        self._speech_buffers = {}
        self._speech_started = {}
        self._speech_last_voice = {}
        self._question_fragments = []
        self._question_fragment_ended_at = 0.0
        self._last_detected_question = ""
        self._question_timer = None
        self._question_lock = threading.Lock()
        self._buffer_lock = threading.Lock()
        self._transcription_queue = queue.Queue()
        self._transcription_thread = None
        self._transcriber_warning_logged = False
        self._last_rms_log_at = {}

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
        if speaker.lower() not in ("interviewer", "system"):
            return

        # Recognition may return adjacent pieces of one question. Join only
        # nearby fragments, then trigger once on the best available context.
        now = time.monotonic()
        if now - self._question_fragment_ended_at > 8.0:
            self._question_fragments = []
        self._question_fragments.append(text.strip())
        self._question_fragment_ended_at = now
        combined = " ".join(part for part in self._question_fragments if part)
        with self._question_lock:
            if self._question_timer:
                self._question_timer.cancel()
                self._question_timer = None
        if not self.is_question(combined):
            return

        normalized = re.sub(r"\s+", " ", combined).strip().lower()
        if normalized == self._last_detected_question:
            return
        with self._question_lock:
            # Wait briefly for the remaining recognition segment. This avoids
            # answering a partial question while the interviewer is speaking.
            self._question_timer = threading.Timer(
                1.0, self._emit_pending_question, args=(combined, normalized)
            )
            self._question_timer.daemon = True
            self._question_timer.start()

    def _emit_pending_question(self, question: str, normalized: str):
        """Emit one complete-enough interviewer question after a quiet gap."""
        with self._question_lock:
            if normalized == self._last_detected_question:
                return
            self._last_detected_question = normalized
            self._question_fragments = []
            self._question_timer = None
        if self._on_question_detected:
            self._on_question_detected(question)

    def start_capture(self, system_audio_only: bool = False):
        """Starts capture, optionally excluding the local microphone."""
        if self.is_capturing:
            return
        self.is_capturing = True
        self._transcription_thread = threading.Thread(
            target=self._transcription_worker,
            daemon=True,
        )
        self._transcription_thread.start()
        self._thread = threading.Thread(
            target=self._capture_worker,
            args=(system_audio_only,),
            daemon=True,
        )
        self._thread.start()
        logger.info("Audio capture engine started.")

    def stop_capture(self):
        """Stops audio capture."""
        self.is_capturing = False
        self._loopback_stop.set()
        with self._question_lock:
            if self._question_timer:
                self._question_timer.cancel()
                self._question_timer = None
        for stream in self._streams:
            try:
                stream.stop()
                stream.close()
            except Exception as e:
                logger.warning(f"Failed to close audio stream: {e}")
        self._streams.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._loopback_thread and self._loopback_thread.is_alive():
            self._loopback_thread.join(timeout=1.0)
        self._loopback_thread = None
        self._transcription_queue.put(None)
        if self._transcription_thread and self._transcription_thread.is_alive():
            self._transcription_thread.join(timeout=2.0)
        logger.info("Audio capture engine stopped.")

    def _capture_worker(self, system_audio_only: bool = False):
        """Start system output capture and optionally microphone capture."""
        try:
            import sounddevice as sd

            devices = sd.query_devices()
            logger.info("Available audio devices: %d", len(devices))

            if not system_audio_only:
                mic_stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    blocksize=self.chunk_size,
                    dtype="float32",
                    callback=lambda data, frames, time_info, status: self._audio_callback(
                        "candidate", data, status, self.sample_rate
                    ),
                )
                mic_stream.start()
                self._streams.append(mic_stream)

            # Windows WASAPI loopback captures interviewer/system audio. It is
            # optional because devices and host APIs vary by machine.
            if sys.platform == "win32":
                try:
                    self._loopback_stop.clear()
                    if self._start_soundcard_loopback():
                        system_stream = None
                    else:
                        system_stream = self._open_system_audio_stream(sd, devices)
                    if system_stream is None and self._loopback_thread is None:
                        logger.info(
                            "System-audio capture device not available; "
                            "microphone capture remains active."
                        )
                    else:
                        loopback_stream, device_name = system_stream
                        self._streams.append(loopback_stream)
                        logger.info("System-audio capture started from %s.", device_name)
                except Exception as e:
                    logger.info("WASAPI loopback capture unavailable: %s", e)

            if system_audio_only:
                logger.info("System-audio-only capture requested; microphone capture disabled.")
            else:
                logger.info("Microphone capture started.")
        except Exception as e:
            logger.warning("Audio capture unavailable: %s", e)
            self.is_capturing = False

        while self.is_capturing:
            time.sleep(0.1)

    def _start_soundcard_loopback(self) -> bool:
        """Start speaker loopback capture when PortAudio exposes no loopback input."""
        try:
            import soundcard as sc
        except ImportError:
            logger.info(
                "Optional soundcard loopback backend is not installed; "
                "trying Stereo Mix/PortAudio."
            )
            return False

        try:
            speaker = sc.default_speaker()
            if speaker is None:
                return False
            loopback = sc.get_microphone(
                speaker.name,
                include_loopback=True,
            )
            if loopback is None:
                return False
        except Exception as exc:
            logger.info("Soundcard loopback device unavailable: %s", exc)
            return False

        def capture_loop():
            logger.info("System-audio capture started from WASAPI loopback: %s", speaker.name)
            try:
                with loopback.recorder(
                    samplerate=self.sample_rate,
                    channels=2,
                    blocksize=self.chunk_size,
                ) as recorder:
                    while self.is_capturing and not self._loopback_stop.is_set():
                        data = recorder.record(numframes=self.chunk_size)
                        self._audio_callback(
                            "interviewer",
                            data,
                            None,
                            self.sample_rate,
                        )
            except Exception as exc:
                logger.warning("WASAPI loopback capture stopped: %s", exc)

        self._loopback_thread = threading.Thread(
            target=capture_loop,
            name="ApexPilot-WASAPI-Loopback",
            daemon=True,
        )
        self._loopback_thread.start()
        return True

    @staticmethod
    def _find_system_audio_device(devices):
        """Find WASAPI loopback first, then Windows Stereo Mix as a fallback."""
        candidates = AudioCaptureEngine._find_system_audio_devices(devices)
        return candidates[0] if candidates else None

    @staticmethod
    def _find_system_audio_devices(devices):
        """Return usable system-audio candidates in preferred order."""
        loopbacks = []
        stereo_mix = None
        for index, device in enumerate(devices):
            name = str(device.get("name", "")).lower()
            host_api = int(device.get("hostapi", -1))
            if int(device.get("max_input_channels", 0)) <= 0:
                continue
            if "loopback" in name and host_api == 2:
                selected = dict(device)
                selected["index"] = index
                selected["is_loopback"] = True
                loopbacks.append(selected)
            if "stereo mix" in name:
                stereo_mix = dict(device)
                stereo_mix["index"] = index
                stereo_mix["is_loopback"] = False
        return loopbacks + ([stereo_mix] if stereo_mix else [])

    def _open_system_audio_stream(self, sd, devices):
        """Open the first working loopback or Stereo Mix device."""
        for device in self._find_system_audio_devices(devices):
            native_rate = int(float(device.get("default_samplerate") or self.sample_rate))
            rates = list(dict.fromkeys((self.sample_rate, native_rate)))
            channel_count = min(2, int(device["max_input_channels"]))
            channels = list(dict.fromkeys((channel_count, 1)))
            for rate in rates:
                for channel_count in channels:
                    stream_options = {
                        "samplerate": rate,
                        "channels": channel_count,
                        "blocksize": max(1, int(rate * 0.1)),
                        "dtype": "float32",
                        "device": int(device["index"]),
                        "callback": lambda data, frames, time_info, status, source_rate=rate:
                            self._audio_callback(
                                "interviewer", data, status, source_rate
                            ),
                    }
                    if device["is_loopback"]:
                        stream_options["extra_settings"] = sd.WasapiSettings()
                    try:
                        stream = sd.InputStream(**stream_options)
                        stream.start()
                        return stream, device["name"]
                    except Exception as e:
                        logger.info(
                            "System-audio device '%s' unavailable at %s Hz/%s ch: %s",
                            device["name"],
                            rate,
                            channel_count,
                            e,
                        )
        return None

    def _audio_callback(self, speaker: str, data, status, source_rate=None):
        """Buffer speech segments and send completed segments to transcription."""
        if status:
            logger.debug("Audio status (%s): %s", speaker, status)
        if data is None or len(data) == 0:
            return

        samples = np.asarray(data, dtype=np.float32)
        if source_rate and int(source_rate) != self.sample_rate:
            samples = self._resample(samples, int(source_rate), self.sample_rate)
        rms = float(np.sqrt(np.mean(np.square(samples))))
        now = time.monotonic()
        mono = samples.mean(axis=1) if samples.ndim > 1 else samples

        with self._buffer_lock:
            if now - self._last_rms_log_at.get(speaker, 0.0) >= 5.0:
                logger.info(
                    "Audio level (%s): RMS=%.5f, VAD threshold=%.5f",
                    speaker,
                    rms,
                    self.energy_threshold,
                )
                self._last_rms_log_at[speaker] = now
            if rms >= self.energy_threshold:
                if (
                    self._speech_started.get(speaker)
                    and now - self._speech_started[speaker] >= self.max_segment_seconds
                ):
                    self._queue_speech_segment(speaker, now)
                self._last_speech_at = now
                self._speech_started.setdefault(speaker, now)
                self._speech_last_voice[speaker] = now
                self._speech_buffers.setdefault(speaker, bytearray()).extend(
                    (np.clip(mono, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()
                )
            elif (
                self._speech_started.get(speaker)
                and now - self._speech_last_voice.get(speaker, now) >= self.silence_duration_seconds
            ):
                self._queue_speech_segment(speaker, now)

    def _queue_speech_segment(self, speaker: str, now: float):
        """Queue the current segment and reset it for following speech."""
        audio_bytes = bytes(self._speech_buffers.pop(speaker, bytearray()))
        started = self._speech_started.pop(speaker, now)
        self._speech_last_voice.pop(speaker, None)
        if now - started >= 0.4 and audio_bytes:
            self._transcription_queue.put((speaker, audio_bytes))
            logger.info(
                "Queued %s speech segment for transcription (%.1fs, %d bytes).",
                speaker,
                now - started,
                len(audio_bytes),
            )

    @staticmethod
    def _resample(samples, source_rate: int, target_rate: int):
        """Resample callback audio so transcription always receives 16 kHz PCM."""
        if source_rate == target_rate or len(samples) == 0:
            return samples
        source = np.asarray(samples, dtype=np.float32)
        source_mono = source.mean(axis=1) if source.ndim > 1 else source
        target_length = max(1, int(round(len(source_mono) * target_rate / source_rate)))
        source_positions = np.linspace(0.0, 1.0, len(source_mono), endpoint=False)
        target_positions = np.linspace(0.0, 1.0, target_length, endpoint=False)
        return np.interp(target_positions, source_positions, source_mono).astype(np.float32)

    def _transcription_worker(self):
        """Transcribe completed speech segments off the sounddevice callback."""
        while True:
            item = self._transcription_queue.get()
            if item is None:
                return
            speaker, audio_bytes = item
            logger.info("Transcribing %s speech segment.", speaker)
            text = self._transcribe(audio_bytes)
            if text:
                logger.info("Transcript received (%s): %s", speaker, text)
                self.submit_transcript(speaker, text)
            else:
                logger.info("No transcript returned for %s speech segment.", speaker)

    def _transcribe(self, audio_bytes: bytes) -> str:
        """Use online recognition first, then a local PocketSphinx fallback."""
        samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        if samples.size == 0:
            return ""
        raw_rms = float(np.sqrt(np.mean(np.square(samples))) / 32768.0)
        if raw_rms < self.energy_threshold:
            logger.info("Skipping transcription for near-silent audio (RMS=%.5f).", raw_rms)
            return ""
        try:
            import speech_recognition as sr
        except ImportError:
            if not self._transcriber_warning_logged:
                logger.warning(
                    "Speech transcription is unavailable. Install SpeechRecognition "
                    "to convert meeting audio into questions."
                )
                self._transcriber_warning_logged = True
            return ""

        try:
            recognizer = sr.Recognizer()
            normalized = self._normalize_pcm(audio_bytes)
            audio = sr.AudioData(normalized, self.sample_rate, 2)
            try:
                text = recognizer.recognize_google(audio, language="en-US").strip()
                if text:
                    return text
            except (sr.UnknownValueError, sr.RequestError) as e:
                logger.info(
                    "Google recognition unavailable (%s); trying local recognition.",
                    e.__class__.__name__,
                )

            try:
                text = recognizer.recognize_sphinx(audio).strip()
                if self._is_credible_transcript(text):
                    logger.info("Local recognition returned usable text.")
                    return text
                logger.info("Local recognition returned low-confidence text; discarding it.")
                return ""
            except (sr.UnknownValueError, sr.RequestError, ImportError, OSError):
                return ""
        except Exception as e:
            logger.warning("Speech transcription failed: %s", e)
            return ""

    @staticmethod
    def _normalize_pcm(audio_bytes: bytes) -> bytes:
        """Remove DC offset and normalize quiet 16-bit PCM before recognition."""
        samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        if samples.size == 0:
            return audio_bytes
        samples -= float(np.mean(samples))
        peak = float(np.max(np.abs(samples)))
        if 0 < peak < 26214.0:
            samples *= 26214.0 / peak
        return np.clip(samples, -32768, 32767).astype(np.int16).tobytes()

    @staticmethod
    def _is_credible_transcript(text: str) -> bool:
        """Reject empty or obviously fragmented recognizer output."""
        words = re.findall(r"[A-Za-z']+", text or "")
        if len(words) < 2:
            return False
        if len(set(word.lower() for word in words)) == 1 and len(words) > 2:
            return False
        alpha_chars = sum(character.isalpha() for character in text)
        return alpha_chars >= 0.65 * max(1, len(text))

    def submit_transcript(self, speaker: str, text: str):
        """Dispatch text from an optional speech-to-text adapter."""
        self.simulate_speech_input(speaker, text)


# Singleton instance
audio_engine = AudioCaptureEngine()
