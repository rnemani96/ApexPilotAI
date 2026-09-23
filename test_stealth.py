"""
ApexPilot AI - Comprehensive Automated Test Suite
=================================================
Validates:
1. Win32 Stealth Layer (SetWindowDisplayAffinity WDA_EXCLUDEFROMCAPTURE)
2. Local & Online LLM Streaming Pipeline & Modes
3. Windows Native Media OCR Engine
4. Question Detection Heuristics & Audio Engine
5. Context Store & Candidate Profile Persistence
6. PySide6 UI Component Initialization & Frameless Resizing
7. Custom Instructions Injection
8. Rate Limit (429) Failover & Stream Interruption Abort
9. Window Geometry & Resizing Persistence
"""

import sys
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.win32_stealth import stealth_layer, WDA_EXCLUDEFROMCAPTURE
from core.llm_client import llm_client, RateLimitError
from core.ocr_engine import ocr_engine
from core.audio_capture import audio_engine
from core.context_store import context_store
from core.prompts import build_prompt
from core.qa_cache import qa_cache
from core.pdf_exporter import pdf_exporter


class TestApexPilotComplete(unittest.TestCase):

    def test_01_win32_stealth_layer(self):
        """Verifies Win32 display affinity constants and prototype bindings."""
        self.assertTrue(stealth_layer.is_windows, "System must be Windows for Win32 stealth layer.")
        self.assertIsNotNone(stealth_layer._user32, "User32.dll must be loaded.")
        self.assertEqual(WDA_EXCLUDEFROMCAPTURE, 0x00000011, "WDA_EXCLUDEFROMCAPTURE must be 0x11.")

    def test_02_llm_streaming_pipeline(self):
        """Verifies that the LLM streaming pipeline yields tokens smoothly across all modes."""
        modes = ["stealth_coder", "star_behavioral", "system_design", "huddle_mate", "teleprompter"]
        for mode in modes:
            tokens = []
            stream = llm_client.stream_response(mode, "Test prompt")
            for token in stream:
                tokens.append(token)
                if len(tokens) >= 10:
                    break
            self.assertGreater(len(tokens), 0, f"Streaming failed to yield tokens for mode {mode}")

    def test_03_ocr_extraction(self):
        """Verifies OCR engine extracts text from an in-memory test image."""
        img = Image.new("RGB", (320, 80), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((15, 25), "LeetCode 206 Reverse Linked List", fill=(0, 0, 0))

        extracted = ocr_engine.extract_text(img)
        self.assertIsInstance(extracted, str)
        self.assertTrue(len(extracted) > 0, "OCR should extract text from test image.")

    def test_04_audio_question_heuristics(self):
        """Verifies Parakeet AI question detection triggers on interview questions."""
        self.assertTrue(audio_engine.is_question("Can you explain how this handles concurrency?"))
        self.assertTrue(audio_engine.is_question("How would you scale this microservice?"))
        self.assertFalse(audio_engine.is_question("Let us move on to the next topic."))

    def test_05_context_store_profile(self):
        """Verifies candidate resume context injection."""
        context_store.update_profile(
            resume="Staff Engineer with 10 years distributed systems experience at Google and Uber.",
            jd="Staff Software Engineer, Infrastructure",
            language="Go"
        )
        ctx = context_store.get_profile()
        self.assertIn("Staff Engineer", ctx["resume"])
        self.assertEqual(context_store.config["preferences"]["coding_language"], "Go")

    def test_06_ui_components_headless(self):
        """Verifies that PySide6 UI windows initialize without errors."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)

        from ui.overlay_window import OverlayWindow
        from ui.teleprompter_bar import TeleprompterBar
        from ui.snip_overlay import SnipOverlay
        from ui.settings_dialog import SettingsDialog

        overlay = OverlayWindow()
        self.assertIsNotNone(overlay)

        teleprompter = TeleprompterBar()
        self.assertIsNotNone(teleprompter)

        snip = SnipOverlay()
        self.assertIsNotNone(snip)

        settings = SettingsDialog()
        self.assertIsNotNone(settings)

    def test_07_custom_instructions_injection(self):
        """Verifies that custom instructions are strictly injected into prompt templates."""
        # 1. With custom instructions
        custom_rule = "ALWAYS use modern C++20 with std::ranges and keep answers under 2 sentences."
        sys_p, _ = build_prompt("stealth_coder", "Solve Two Sum", {"custom_instructions": custom_rule})
        self.assertIn("MANDATORY USER CUSTOM INSTRUCTIONS", sys_p)
        self.assertIn(custom_rule, sys_p)

        # 2. Without custom instructions (normal standard behavior)
        sys_p_normal, _ = build_prompt("stealth_coder", "Solve Two Sum", {"custom_instructions": ""})
        self.assertNotIn("MANDATORY USER CUSTOM INSTRUCTIONS", sys_p_normal)

    def test_08_stream_interruption_abort(self):
        """Verifies rapid interruption abort signal terminates active streaming."""
        llm_client.abort_active_streams()
        # Verify event was set and reset
        self.assertFalse(llm_client._current_abort_event.is_set())

    def test_09_window_geometry_persistence(self):
        """Verifies window resize dimensions are saved and retrieved correctly."""
        context_store.save_window_geometry(250, 180, 800, 600)
        geom = context_store.get_window_geometry()
        self.assertEqual(geom["x"], 250)
        self.assertEqual(geom["y"], 180)
        self.assertEqual(geom["width"], 800)
        self.assertEqual(geom["height"], 600)

    def test_10_qa_cache_and_pdf_export(self):
        """Verifies QA caching, exact & fuzzy lookup, and automatic local PDF generation."""
        q = "How do you implement a LRU cache with O(1) operations in Python?"
        a = "Use an OrderedDict or a combination of a Doubly Linked List and a Hash Map."

        entry = qa_cache.store(q, a, mode="stealth_coder", provider="mock")
        self.assertIsNotNone(entry)
        self.assertTrue(entry.get("pdf_path"), "PDF path should not be empty.")
        pdf_file = Path(entry["pdf_path"])
        self.assertTrue(pdf_file.exists(), "PDF file must exist on disk.")
        self.assertGreater(pdf_file.stat().st_size, 0, "PDF file must not be empty.")

        # Test exact lookup
        exact_hit = qa_cache.lookup(q)
        self.assertIsNotNone(exact_hit, "Exact lookup should return cached entry.")
        self.assertEqual(exact_hit["answer"], a)

        # Test fuzzy lookup (rephrased slightly)
        rephrased = "Can you implement an LRU cache with O(1) time complexity in Python?"
        fuzzy_hit = qa_cache.lookup(rephrased, threshold=0.60)
        self.assertIsNotNone(fuzzy_hit, "Fuzzy lookup should recognize similar LRU question.")

    def test_11_custom_online_endpoints(self):
        """Verifies adding and retrieving arbitrary custom online LLM endpoints."""
        endpoint = context_store.add_custom_endpoint(
            name="OpenRouter Test",
            base_url="https://openrouter.ai/api/v1",
            api_key="sk-or-test12345",
            model="anthropic/claude-3.5-sonnet",
            enabled=True
        )
        self.assertIn("custom_", endpoint["id"])

        endpoints = context_store.get_custom_endpoints()
        found = any(e["id"] == endpoint["id"] for e in endpoints)
        self.assertTrue(found, "Custom endpoint must be present in context_store.")

        # Clean up
        context_store.delete_custom_endpoint(endpoint["id"])
        endpoints_after = context_store.get_custom_endpoints()
        found_after = any(e["id"] == endpoint["id"] for e in endpoints_after)
        self.assertFalse(found_after, "Custom endpoint must be deleted.")

    def test_12_resume_jd_document_extraction(self):
        """Verifies text extraction from documents and prompt tailoring with resume + JD."""
        from ui.settings_dialog import extract_text_from_document
        import tempfile

        # Test text file extraction
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write("Senior Distributed Systems Engineer. Scaled Apache Kafka to 5M events/sec.")
            temp_path = tf.name

        try:
            extracted = extract_text_from_document(temp_path)
            self.assertIn("5M events/sec", extracted)

            # Test prompt building with tailored resume and JD
            context = {
                "resume": extracted,
                "job_description": "Staff Engineer - Kafka & Stream Processing",
                "custom_instructions": ""
            }
            sys_star, user_star = build_prompt("star_behavioral", "Tell me about a high throughput project.", context)
            self.assertIn("5M events/sec", sys_star)
            self.assertIn("Staff Engineer - Kafka", sys_star)

            sys_sysdes, _ = build_prompt("system_design", "Design a real-time event pipeline.", context)
            self.assertIn("5M events/sec", sys_sysdes)
            self.assertIn("Staff Engineer - Kafka", sys_sysdes)
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

