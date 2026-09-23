"""
ApexPilot AI - Ultra-Fast OCR & Screen Snip Engine
===================================================
StealthCoder feature: High-speed screen capture and text extraction.
Supports:
1. Windows 10/11 built-in Native Hardware-Accelerated OCR (Windows.Media.Ocr)
2. Image preprocessing (contrast enhancement, scaling) for crisp code OCR
3. Region snipping with sub-30ms capture
"""

import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path
from PIL import Image, ImageGrab, ImageEnhance, ImageOps
import logging

logger = logging.getLogger("ApexPilot.OCR")

SCRIPT_DIR = Path(__file__).resolve().parent
OCR_RUNNER_PS1 = SCRIPT_DIR / "ocr_runner.ps1"


class OCREngine:
    """High-speed screen capture and OCR engine."""

    def __init__(self):
        self._has_windows_media_ocr = sys.platform == "win32" and OCR_RUNNER_PS1.exists()
        self._temp_dir = Path(tempfile.gettempdir()) / "apexpilot_ocr"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def capture_screen(self, bbox: tuple[int, int, int, int] = None) -> Image.Image:
        """
        Captures full screen or region bounded by bbox (left, top, right, bottom).
        Uses high-speed Direct/GDI capture via Pillow.
        """
        try:
            img = ImageGrab.grab(bbox=bbox, all_screens=True)
            return img
        except Exception as e:
            logger.error(f"Failed to grab screen: {e}")
            return None

    def preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Enhances image contrast and resolution for LeetCode dark/light mode code readability."""
        try:
            # Convert to grayscale
            gray = image.convert("L")
            # Upscale if image is small to improve character recognition
            w, h = gray.size
            if w < 1000 and h < 800:
                gray = gray.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(1.8)
            return enhanced
        except Exception as e:
            logger.warning(f"Preprocessing warning: {e}")
            return image

    def extract_text(self, image: Image.Image) -> str:
        """
        Extracts text from the given PIL Image.
        Tries Windows.Media.Ocr first (native OS feature, sub-50ms), then fallbacks.
        """
        if image is None:
            return ""

        processed = self.preprocess_image_for_ocr(image)
        temp_img_path = self._temp_dir / f"snip_{int(time.time() * 1000)}.png"

        try:
            processed.save(temp_img_path, format="PNG")

            # Method 1: Windows 10/11 Native Windows.Media.Ocr via fast PowerShell runner
            if self._has_windows_media_ocr:
                text = self._run_windows_media_ocr(temp_img_path)
                if text and len(text.strip()) > 0:
                    return text.strip()

            # Method 2: Fallback to pytesseract if installed
            try:
                import pytesseract
                text = pytesseract.image_to_string(processed)
                if text and len(text.strip()) > 0:
                    return text.strip()
            except ImportError:
                pass

        except Exception as e:
            logger.error(f"OCR Extraction error: {e}")
        finally:
            if temp_img_path.exists():
                try:
                    temp_img_path.unlink()
                except Exception:
                    pass

        return ""

    def _run_windows_media_ocr(self, image_path: Path) -> str:
        """
        Invokes Windows.Media.Ocr via ocr_runner.ps1.
        Hardware-accelerated, runs locally on Windows without any heavy third-party binaries.
        """
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            proc = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(OCR_RUNNER_PS1),
                    "-ImagePath",
                    str(image_path)
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                timeout=6
            )
            if proc.returncode == 0:
                return proc.stdout.strip()
            else:
                logger.warning(f"Windows Media OCR script error: {proc.stderr}")
                return ""
        except Exception as e:
            logger.warning(f"Failed to invoke Windows.Media.Ocr: {e}")
            return ""


# Singleton instance
ocr_engine = OCREngine()
