"""
ApexPilot AI - Screenshot & Visual Asset Generator
==================================================
Instantiates actual PySide6 application windows and widgets with realistic
interview scenarios to capture pixel-perfect, high-DPI screenshots for
the comprehensive User Guide.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap

# Ensure workspace root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from ui.overlay_window import OverlayWindow
from ui.settings_dialog import SettingsDialog
from ui.teleprompter_bar import TeleprompterBar
from core.context_store import context_store

IMG_DIR = BASE_DIR / "docs" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)


def capture_all():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")

    print("[*] Generating Application Screenshots...")

    # -------------------------------------------------------------
    # 1. Main Stealth HUD - Coding Mode (LeetCode LRU Cache)
    # -------------------------------------------------------------
    print("[1/8] Capturing 01_stealth_hud_coding.png...")
    hud = OverlayWindow()
    hud.resize(760, 640)
    hud.set_mode("stealth_coder")
    hud.query_input.setText("Design a high-throughput LRU Cache with O(1) get & put operations.")

    sample_coding_solution = """### ⚡ Intuition & Approach
- Use a **Hash Map** combined with a **Doubly Linked List** to achieve **O(1)** time complexity for both `get` and `put`.
- The hash map stores keys mapped directly to node references in the linked list. The doubly linked list maintains the temporal usage order (Most Recently Used at head, Least Recently Used at tail).
- **Time Complexity**: **O(1)** amortized for all operations.
- **Space Complexity**: **O(Capacity)** auxiliary memory.

### 💻 Optimal Production Code (Python)
```python
class Node:
    __slots__ = ('key', 'val', 'prev', 'next')
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self._add_to_front(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

### 🗣️ Step-by-Step Explanation (Natural First-Person Talking Points)
- *"First, I use sentinel dummy head and tail nodes to eliminate edge cases when inserting or evicting."*
- *"When `get` is called, if the key exists, I splice the node out of its current position and prepend it directly behind the dummy head to mark it as most recently used."*
- *"For `put`, if the capacity is exceeded, I immediately evict `tail.prev` in O(1) time and purge it from our hash map."*

### 🧪 Edge Cases & Dry Run
- **Zero or 1 Capacity**: Tested and verified; sentinel nodes prevent null pointer exceptions.
- **Overwriting existing key**: Updates value and shifts node to front without expanding cache size.
"""
    hud.response_browser.setMarkdown(sample_coding_solution)
    hud.show()
    app.processEvents()
    hud.grab().save(str(IMG_DIR / "01_stealth_hud_coding.png"))
    hud.hide()

    # -------------------------------------------------------------
    # 2. STAR Behavioral Mode - Tailored via Resume & JD
    # -------------------------------------------------------------
    print("[2/8] Capturing 02_star_behavioral_resume.png...")
    hud_star = OverlayWindow()
    hud_star.resize(760, 640)
    hud_star.set_mode("star_behavioral")
    hud_star.query_input.setText("Tell me about a critical production bottleneck you resolved under tight deadlines.")

    sample_star_solution = """### 🎯 STAR Behavioral Response (Tailored to Candidate Resume & Staff JD)

- **Situation**:
  At my previous company, our real-time order matching pipeline experienced critical p99 latency spikes exceeding 4,500ms during market opening volume spikes. This risked breaching our high-availability SLA and impacted institutional trading clients.

- **Task**:
  As the Senior Distributed Systems Engineer owning backend latency, I was tasked with identifying the root bottleneck, designing a low-latency remediation, and restoring sub-50ms p99 response times within a 48-hour deadline.

- **Action**:
  - Attached **eBPF kernel probes** and CPU flame graphs to isolate lock contention within our multithreaded network ingestion layer.
  - Discovered TCP buffer starvation caused by head-of-line blocking in the synchronized queue.
  - Re-architected the ingestion worker into **partitioned, lock-free ring buffers** in Go using goroutines and zero-copy deserialization over Apache Kafka topics.
  - Implemented an adaptive backpressure circuit breaker to safeguard downstream microservices.

- **Result**:
  - Slashed p99 end-to-end latency from **4,500ms down to 18ms** (a 99.6% reduction).
  - Maintained **zero dropped packets** through a 10x traffic surge during high volatility.
  - Optimized resource utilization, directly saving **40% in monthly cloud compute costs** as highlighted on my resume.

- **Key Takeaway**:
  *"Deep kernel-level observability paired with decoupled, lock-free partitioning prevents microservice cascading failures under sudden traffic surges."*
"""
    hud_star.response_browser.setMarkdown(sample_star_solution)
    hud_star.show()
    app.processEvents()
    hud_star.grab().save(str(IMG_DIR / "02_star_behavioral_resume.png"))
    hud_star.hide()

    # -------------------------------------------------------------
    # 3. Settings Dialog - Tab 1: Local LLM Engine & Routing
    # -------------------------------------------------------------
    print("[3/8] Capturing 03_settings_llm_routing.png...")
    settings = SettingsDialog()
    settings.tabs.setCurrentIndex(0)
    settings.provider_combo.setCurrentText("ollama")
    settings.url_edit.setText("http://127.0.0.1:11434")
    settings.model_edit.setText("qwen2.5-coder:7b")
    settings.status_label.setText("✅ Ollama Online (4 models available)")
    settings.status_label.setStyleSheet("color: #00ffaa; font-weight: bold;")
    settings.race_check.setChecked(True)
    settings.failover_check.setChecked(True)
    settings.show()
    app.processEvents()
    settings.grab().save(str(IMG_DIR / "03_settings_llm_routing.png"))

    # -------------------------------------------------------------
    # 4. Settings Dialog - Tab 2: Online API Pool
    # -------------------------------------------------------------
    print("[4/8] Capturing 04_settings_online_apis.png...")
    settings.tabs.setCurrentIndex(1)
    if "groq" in settings.api_inputs:
        settings.api_inputs["groq"]["enable"].setChecked(True)
        settings.api_inputs["groq"]["key"].setText("gsk_ultraFastLPUKey300TokensPerSec")
    if "openai" in settings.api_inputs:
        settings.api_inputs["openai"]["enable"].setChecked(True)
        settings.api_inputs["openai"]["key"].setText("sk-proj-chatgptLiveAPIKeyProduction")
    if "grok" in settings.api_inputs:
        settings.api_inputs["grok"]["enable"].setChecked(True)
        settings.api_inputs["grok"]["key"].setText("xai-liveGrok2ProductionFastKey")
    app.processEvents()
    settings.grab().save(str(IMG_DIR / "04_settings_online_apis.png"))

    # -------------------------------------------------------------
    # 5. Settings Dialog - Tab 4: Resume Context & 1-Click Loaders
    # -------------------------------------------------------------
    print("[5/8] Capturing 05_settings_resume_jd.png...")
    settings.tabs.setCurrentIndex(3)
    settings.resume_text.setPlainText(
        "Senior Distributed Systems Engineer (8+ years experience).\n"
        "• Architected ultra-low latency event streaming backends using Python, Go, Kafka, Redis, and C++.\n"
        "• Led migration of core monolith to Kubernetes, cutting compute costs by 40% ($320k/yr).\n"
        "• Scaled real-time order matching pipeline to 5M events/sec with sub-20ms p99 latency.\n"
        "• Expert in distributed consensus (Raft/Paxos), database internals (PostgreSQL, Cassandra), and eBPF."
    )
    settings.jd_text.setPlainText(
        "Staff Software Engineer - Infrastructure & Distributed Systems.\n"
        "Requirements: Deep knowledge of high-throughput messaging (Kafka/Pulsar), microservices latency optimization, "
        "and concurrency. Must possess strong STAR behavioral leadership experience and architectural design skills."
    )
    app.processEvents()
    settings.grab().save(str(IMG_DIR / "05_settings_resume_jd.png"))
    settings.hide()

    # -------------------------------------------------------------
    # 6. Minimalist Teleprompter HUD (Webcam Eye-Contact Bar)
    # -------------------------------------------------------------
    print("[6/8] Capturing 06_teleprompter_bar.png...")
    tele = TeleprompterBar()
    tele.resize(680, 110)
    tele.set_content(
        "• Scaled Apache Kafka cluster to 5M events/sec with zero packet loss during peak market volatility.\n"
        "• Isolated thread starvation via eBPF kernel tracing, redesigning worker pool with lock-free ring buffers.\n"
        "• Reduced p99 latency by 99.6% (from 4.5s to 18ms), saving $320k in cloud compute annually."
    )
    tele.show()
    app.processEvents()
    tele.grab().save(str(IMG_DIR / "06_teleprompter_bar.png"))
    tele.hide()

    # -------------------------------------------------------------
    # 7. Screen Snipping & LeetCode OCR Tool
    # -------------------------------------------------------------
    print("[7/8] Capturing 07_snip_tool_overlay.png...")
    snip_mock = QWidget()
    snip_mock.setFixedSize(700, 420)
    snip_mock.setStyleSheet("background-color: #0b0f19;")
    s_layout = QVBoxLayout(snip_mock)
    s_layout.setContentsMargins(20, 20, 20, 20)

    # Simulated code problem on screen
    mock_problem = QFrame()
    mock_problem.setStyleSheet("background-color: #1e293b; border: 2px dashed #38bdf8; border-radius: 8px; padding: 15px;")
    mp_layout = QVBoxLayout(mock_problem)

    tag = QLabel("✂️ [SCREEN SNIP REGION DETECTED — NATIVE WINDOWS MEDIA OCR (<25ms)]")
    tag.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 12px;")
    mp_layout.addWidget(tag)

    code_txt = QLabel(
        "<b>146. LRU Cache (Medium)</b><br><br>"
        "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.<br>"
        "Implement the <code>LRUCache</code> class:<br>"
        "• <code>LRUCache(int capacity)</code> Initialize the LRU cache with positive size capacity.<br>"
        "• <code>int get(int key)</code> Return the value of the key if key exists, otherwise return -1.<br>"
        "• <code>void put(int key, int value)</code> Update or insert key-value pair. Evict LRU if capacity exceeded."
    )
    code_txt.setStyleSheet("color: #f1f5f9; font-size: 13px; line-height: 1.4;")
    mp_layout.addWidget(code_txt)
    s_layout.addWidget(mock_problem)

    info_snip = QLabel("💡 <i>Press <b>Ctrl + Alt + S</b> anywhere. Drag red crosshair over question. Text extracts in <25ms!</i>")
    info_snip.setStyleSheet("color: #94a3b8; font-size: 11px;")
    s_layout.addWidget(info_snip)

    snip_mock.show()
    app.processEvents()
    snip_mock.grab().save(str(IMG_DIR / "07_snip_tool_overlay.png"))
    snip_mock.hide()

    # -------------------------------------------------------------
    # 8. Local PDF Report / Saved Interviews Archive
    # -------------------------------------------------------------
    print("[8/8] Capturing 08_saved_pdf_report.png...")
    report_widget = QWidget()
    report_widget.setFixedSize(700, 480)
    report_widget.setStyleSheet("background-color: #0f172a; color: #f8fafc;")
    r_layout = QVBoxLayout(report_widget)
    r_layout.setContentsMargins(25, 25, 25, 25)

    hdr = QLabel("📁 ApexPilot AI - Saved Interview Archive & Vector PDF")
    hdr.setStyleSheet("color: #38bdf8; font-size: 16px; font-weight: bold;")
    r_layout.addWidget(hdr)

    card = QFrame()
    card.setStyleSheet("background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px;")
    c_layout = QVBoxLayout(card)

    pdf_title = QLabel("📄 Interview_Report_LRU_Cache_20260923_120035.pdf")
    pdf_title.setStyleSheet("color: #10b981; font-weight: bold; font-size: 13px;")
    c_layout.addWidget(pdf_title)

    meta_txt = QLabel("• <b>Mode:</b> StealthCoder &bull; <b>Model:</b> Groq Llama-3.3-70B &bull; <b>Latency:</b> 0ms (Cache Hit) &bull; <b>Status:</b> Archived")
    meta_txt.setStyleSheet("color: #94a3b8; font-size: 11px;")
    c_layout.addWidget(meta_txt)

    divider = QFrame()
    divider.setFrameShape(QFrame.Shape.HLine)
    divider.setStyleSheet("color: #334155;")
    c_layout.addWidget(divider)

    preview_body = QLabel(
        "<b>Question:</b> Design a high-throughput Least Recently Used (LRU) Cache in Python.<br><br>"
        "<b>Candidate Profile Match:</b> Aligned with Senior Distributed Systems resume context.<br>"
        "<b>Time Complexity:</b> O(1) &bull; <b>Space Complexity:</b> O(Capacity)<br>"
        "<b>Full Code & Speakable Explanation Archived Locally.</b>"
    )
    preview_body.setStyleSheet("color: #cbd5e1; font-size: 12px;")
    c_layout.addWidget(preview_body)

    r_layout.addWidget(card)

    note = QLabel("Location: <code>d:\\interAI\\saved_interviews\\</code> &bull; Click <b>'📁 Saved PDFs'</b> in HUD to open anytime.")
    note.setStyleSheet("color: #64748b; font-size: 11px;")
    r_layout.addWidget(note)

    report_widget.show()
    app.processEvents()
    report_widget.grab().save(str(IMG_DIR / "08_saved_pdf_report.png"))
    report_widget.hide()

    print("[SUCCESS] All 8 application screenshots successfully generated in 'docs/images/'!")


if __name__ == "__main__":
    capture_all()
