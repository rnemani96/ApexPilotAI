"""
ApexPilot AI - Intelligent Interview Q&A Cache Engine
======================================================
Stores previously answered interview questions and solutions locally.
Features:
1. Exact & Fuzzy Semantic Similarity Lookup:
   When an interviewer asks a previously answered question, ApexPilot AI
   pulls the solution from cache instantly (0ms latency, zero API costs).
2. Automatic Local PDF Archiving:
   Every question and answer is automatically generated and saved as a local PDF.
"""

import json
import re
import string
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging
from core.pdf_exporter import pdf_exporter

logger = logging.getLogger("ApexPilot.QACache")

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "qa_cache.json"

STOPWORDS = {
    "can", "you", "could", "please", "tell", "me", "about", "how", "would",
    "what", "is", "your", "the", "a", "an", "to", "in", "of", "and", "or"
}


def normalize_query(text: str) -> str:
    """Normalizes question text for fuzzy & exact matching."""
    text = text.lower().strip()
    # Strip punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Remove extra spaces
    tokens = [w for w in text.split() if w and w not in STOPWORDS]
    return " ".join(tokens)


def token_similarity(q1: str, q2: str) -> float:
    """Calculates Jaccard similarity between two normalized question token sets."""
    s1 = set(q1.split())
    s2 = set(q2.split())
    if not s1 or not s2:
        return 0.0
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return intersection / float(union) if union > 0 else 0.0


class QACache:
    """Persistent local cache for interview questions and solutions."""

    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self.entries: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading QA cache: {e}")
                return []
        return []

    def _save_to_disk(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save QA cache: {e}")

    def lookup(self, raw_query: str, threshold: float = 0.80) -> Optional[dict]:
        """
        Looks up a question in cache.
        Returns the cached dictionary if an exact or high-similarity match is found;
        otherwise returns None.
        """
        norm_query = normalize_query(raw_query)
        if not norm_query:
            return None

        best_match = None
        best_score = 0.0

        for entry in reversed(self.entries):
            cached_norm = entry.get("normalized_question", "")

            # 1. Exact normalized match
            if norm_query == cached_norm:
                logger.info(f"Exact QA Cache Hit: '{raw_query[:50]}'")
                return entry

            # 2. Token Jaccard similarity
            sim = token_similarity(norm_query, cached_norm)
            if sim > best_score:
                best_score = sim
                best_match = entry

        if best_match and best_score >= threshold:
            logger.info(f"Fuzzy QA Cache Hit (Similarity {best_score:.2f}): '{raw_query[:50]}'")
            return best_match

        return None

    def store(self, raw_query: str, answer: str, mode: str = "stealth_coder", provider: str = "local") -> dict:
        """
        Stores question and answer in cache AND generates local PDF file.
        """
        norm_query = normalize_query(raw_query)
        timestamp = datetime.now().isoformat()

        # Generate local PDF file
        pdf_path = pdf_exporter.export_qa_pdf(raw_query, answer, mode, provider)
        pdf_path_str = str(pdf_path) if pdf_path else ""

        # Update if exact match already exists
        for entry in self.entries:
            if entry.get("normalized_question") == norm_query:
                entry["answer"] = answer
                entry["mode"] = mode
                entry["provider"] = provider
                entry["timestamp"] = timestamp
                entry["pdf_path"] = pdf_path_str
                self._save_to_disk()
                return entry

        # Append new entry
        new_entry = {
            "raw_question": raw_query,
            "normalized_question": norm_query,
            "answer": answer,
            "mode": mode,
            "provider": provider,
            "timestamp": timestamp,
            "pdf_path": pdf_path_str
        }
        self.entries.append(new_entry)
        self._save_to_disk()
        logger.info(f"Saved Q&A to cache and PDF: {pdf_path_str}")
        return new_entry

    def clear(self):
        self.entries = []
        self._save_to_disk()


# Singleton instance
qa_cache = QACache()
