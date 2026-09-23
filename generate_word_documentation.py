"""
ApexPilot AI - Word Document (.docx) Generator
==============================================
Generates an executive, beautifully styled Microsoft Word manual (.docx)
with embedded high-resolution application screenshots, structured tables,
callout boxes, and comprehensive technical documentation covering:
- Full System Capabilities & GhostPilot Invisibility
- See-Through Transparency & Click-Through Meeting Interaction
- Installation Guide (Installer, Portable, Virtual Environment)
- Setup & Configuration (Local LLMs, Online API Pools, Resume/JD Loaders)
- Real-World Interview Workflows & Hotkey Reference
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "docs" / "images"
OUTPUT_DOCX = BASE_DIR / "ApexPilot_AI_Comprehensive_Documentation.docx"


def set_cell_background(cell, hex_color: str):
    """Sets cell background shading."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout_box(doc, text: str, title: str = "KEY HIGHLIGHT"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, "F0F9FF")  # Light blue
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Left border styling in XML
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="0284C7"/>\n'
        f'  <w:top w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:bottom w:val="none"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15

    r_title = p.add_run(f"📌 {title}: ")
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(2, 132, 199)
    r_title.font.size = Pt(10.5)

    r_text = p.add_run(text)
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = RGBColor(30, 41, 59)


def add_image_if_exists(doc, img_name: str, caption: str, width_inches: float = 6.0):
    img_path = IMG_DIR / img_name
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_path), width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(14)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(100, 116, 139)
    else:
        p_err = doc.add_paragraph(f"[Image file not found: {img_name}]")
        p_err.runs[0].font.color.rgb = RGBColor(220, 38, 38)


def style_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "0284C7")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(row_data):
            row_cells[col_idx].text = text
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=140, right=140)
            p = row_cells[col_idx].paragraphs[0]
            for r in p.runs:
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(30, 41, 59)

    # Set column widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)


def generate_word_doc():
    print("[*] Generating Comprehensive Microsoft Word Document (.docx)...")
    doc = Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)

    # -------------------------------------------------------------
    # Cover / Header Title
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("🦅 ApexPilot AI")
    r_title.font.size = Pt(26)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(2, 132, 199)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(6)
    r_sub = p_sub.add_run("Comprehensive System Manual: Capabilities, Installation & Setup Guide")
    r_sub.font.size = Pt(14)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(14)
    r_meta = p_meta.add_run(f"Version 2.0.0 • Windows 10/11 64-bit Edition • Published: {datetime.now().strftime('%B %d, %Y')}")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)

    # Executive Overview Callout
    add_callout_box(
        doc,
        "ApexPilot AI is an ultra-low-latency, 100% undetectable stealth interview and meeting copilot for Windows. "
        "It combines the flagship features of GhostPilot AI (screen-share invisibility & webcam teleprompter), "
        "StealthCoder (<25ms native OCR coding copilot), Parakeet AI (dual-channel WASAPI live audio capture + VAD), "
        "HuddleMate (meeting executive summaries), and Final Round AI (resume-powered STAR behavioral & system design answers).",
        "EXECUTIVE OVERVIEW"
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # Section 1: Feature Matrix
    # -------------------------------------------------------------
    h1 = doc.add_heading("1. Unified Feature Matrix vs. Market Alternatives", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "ApexPilot AI unifies the strengths of competing tools while eliminating their detection risks, "
        "cloud latency bottlenecks, and subscription paywalls:"
    )

    matrix_headers = ["Capability", "Market Pioneer", "ApexPilot AI Superpower & Implementation"]
    matrix_widths = [1.8, 1.3, 3.4]
    matrix_data = [
        ["Screen-Share Invisibility", "GhostPilot AI", "Win32 SetWindowDisplayAffinity (WDA_EXCLUDEFROMCAPTURE: 0x11). 100% invisible to Zoom, Teams, Meet, Discord, OBS."],
        ["Webcam Teleprompter", "GhostPilot AI", "Horizontal reader bar anchored to top monitor bezel so you maintain direct eye contact while reading talking points."],
        ["Native Screen OCR", "StealthCoder", "Sub-25ms native hardware OCR via Windows.Media.Ocr. No heavy Python or Tesseract dependencies."],
        ["Algorithmic Solver", "StealthCoder", "Generates optimal approach, Big-O Time & Space complexity, speakable step-by-step points, and edge cases."],
        ["Dual-Channel Audio & VAD", "Parakeet AI", "WASAPI loopback (interviewer voice) + microphone (candidate voice) with real-time Voice Activity Detection."],
        ["Audio Question Detection", "Parakeet AI", "NLP heuristic regex engine detects interview questions ('How would you scale...', 'Can you explain...') in real time."],
        ["Meeting Executive Notes", "HuddleMate", "Auto-generates meeting summaries, key decisions, action items, and live proactive talking points."],
        ["Resume & JD Personalization", "Final Round AI", "1-click PDF/TXT/MD document loaders ingest candidate resume and target JD to ground answers in authentic past metrics."],
        ["STAR Behavioral Engine", "Final Round AI", "Structures behavioral answers strictly as Situation, Task, Action, Result, and Key Takeaway."],
        ["Offline Local LLMs", "ApexPilot Core", "Sub-second streaming connectors for Ollama (qwen2.5-coder, llama3.2), LM Studio, llama.cpp, and built-in Mock."],
        ["Speculative Race Duel", "ApexPilot Core", "Concurrently races Local LLM vs Online LLM; fastest to stream first token wins and displays."],
        ["Automatic 429 Failover", "ApexPilot Core", "Automatically rotates through unlimited online providers (OpenAI, Grok, Groq, Claude, Gemini) on rate limits."],
        ["0ms Response Q&A Cache", "ApexPilot Core", "Exact & Jaccard token similarity matching against prior questions to serve answers in 0ms with zero token cost."],
        ["Vector PDF Archiving", "ApexPilot Core", "Every question and solution is automatically compiled into high-resolution vector PDFs in saved_interviews/."]
    ]
    table_matrix = doc.add_table(rows=1, cols=3)
    style_table(table_matrix, matrix_widths, matrix_headers, matrix_data)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # Section 2: See-Through & Click-Through Meeting Interaction
    # -------------------------------------------------------------
    h2 = doc.add_heading("2. See-Through Transparency & Click-Through Meeting Interaction", level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "A common challenge with desktop interview assistants is managing screen real estate. When placed over "
        "a Zoom call, Microsoft Teams grid, or code editor, normal windows block your view and intercept mouse clicks. "
        "ApexPilot AI incorporates a dedicated dual-layer transparency and click-through engine:"
    )

    doc.add_heading("2.1 See-Through Transparency (Opacity Slider)", level=2)
    doc.add_paragraph(
        "• Located on the top toolbar of the HUD is a smooth Opacity Slider adjustable from 20% to 100%.\n"
        "• By dragging the slider down to 50%–70%, the dark obsidian interface becomes translucent.\n"
        "• You can clearly see meeting participants, shared presentations, web documentation, or code editor lines "
        "directly underneath the AI solution window without having to minimize or reposition it."
    )

    doc.add_heading("2.2 Click-Through Mode (Ctrl + Alt + X)", level=2)
    doc.add_paragraph(
        "• When an overlay floats over a meeting, it normally captures your mouse clicks. ApexPilot AI uses the Windows "
        "WS_EX_TRANSPARENT extended style to enable complete Click-Through Mode.\n"
        "• Pressing Ctrl + Alt + X toggles Click-Through Mode ON and OFF instantly.\n"
        "• While ON, all mouse events (clicks, scrolls, selections, double-clicks) pass completely through ApexPilot AI "
        "into whatever window is behind it.\n"
        "• You can mute/unmute your microphone in Zoom, click buttons in Microsoft Teams, scroll through meeting chat, "
        "or write code in VS Code right through the floating AI answer window!\n"
        "• Pressing Ctrl + Alt + X again instantly restores full mouse interaction with the HUD."
    )

    add_callout_box(
        doc,
        "Even when the window is made see-through and you are actively clicking through it into your meeting, "
        "Windows Desktop Window Manager (DWM) continues to apply WDA_EXCLUDEFROMCAPTURE. Other participants on "
        "Zoom, Microsoft Teams, Google Meet, Discord, or OBS still CANNOT see ApexPilot AI!",
        "STEALTH GUARANTEE"
    )

    # -------------------------------------------------------------
    # Section 3: Detailed Capabilities Breakdown
    # -------------------------------------------------------------
    h3 = doc.add_heading("3. Detailed Capabilities Breakdown", level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)

    doc.add_heading("3.1 GhostPilot Screen-Share Invisibility Engine", level=2)
    doc.add_paragraph(
        "ApexPilot AI interfaces directly with the Windows kernel via ctypes:\n"
        "   SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)  # 0x00000011\n\n"
        "Introduced in Windows 10 (version 2004+) and Windows 11, this call instructs the Windows Desktop Window Manager (DWM) "
        "to separate the application's render surface from the video capture compositor. All desktop capture pipelines "
        "(DirectX Desktop Duplication API, Windows Graphics Capture, GDI BitBlt, WebRTC) receive a blank transparent frame "
        "for the area occupied by ApexPilot AI. The window renders normally on your physical display output only."
    )

    doc.add_heading("3.2 StealthCoder Vision & Native OCR (<25ms)", level=2)
    doc.add_paragraph(
        "Pressing Ctrl + Alt + S triggers the LeetCode screen snip tool. The screen dims and a neon-cyan crosshair appears. "
        "Dragging a bounding box over any problem title, description, or diagram automatically captures the screen region. "
        "The image is processed with Lanczos upscaling and contrast enhancement, then parsed locally using native "
        "Windows.Media.Ocr.OcrEngine in under 25 milliseconds."
    )
    add_image_if_exists(doc, "07_snip_tool_overlay.png", "Figure 1: Screen Snip Tool with <25ms Native Windows Media OCR")
    add_image_if_exists(doc, "01_stealth_hud_coding.png", "Figure 2: Master Stealth HUD in StealthCoder Mode (LeetCode LRU Cache Solution)")

    doc.add_heading("3.3 Dual-Context Ingestion: Tailoring Answers with Resume & JD", level=2)
    doc.add_paragraph(
        "Generic AI answers immediately sound artificial in senior engineering interviews. ApexPilot AI features 1-click "
        "document loaders for candidate resumes and target job descriptions (.pdf, .txt, .md). In STAR Behavioral Mode, "
        "it structures answers into Situation, Task, Action, Result, and Key Takeaway, citing your authentic past metrics "
        "(e.g., 'slashed p99 latency from 4.5s to 18ms; saved 40% in monthly compute costs') and past company scale."
    )
    add_image_if_exists(doc, "05_settings_resume_jd.png", "Figure 3: Settings - Resume & JD Context with 1-Click PDF/TXT/MD Loaders")
    add_image_if_exists(doc, "02_star_behavioral_resume.png", "Figure 4: STAR Behavioral Mode tailoring response to candidate resume metrics")

    doc.add_heading("3.4 Hybrid LLM Client, Speculative Race Duel & 429 Failover", level=2)
    doc.add_paragraph(
        "ApexPilot AI supports both offline local models (Ollama, LM Studio, llama.cpp) and cloud models (Groq 300+ tok/s, "
        "OpenAI GPT-4o, Claude 3.5 Sonnet, Grok-2, Gemini 2.0 Flash, DeepSeek, and unlimited custom endpoints).\n\n"
        "• Fastest-First Race Mode: Concurrently queries your local model and cloud model; the first stream to return tokens claims the UI and terminates the competitor thread.\n"
        "• Automatic 429 Failover: Seamlessly rotates to the next API key or fallback provider if HTTP 429 rate limits are received.\n"
        "• Rapid Interruption Abort: Submitting a new question immediately terminates active generation streams in under 50ms."
    )
    add_image_if_exists(doc, "03_settings_llm_routing.png", "Figure 5: Settings - Local LLM Engine, Fastest-First Race Mode & 429 Failover")
    add_image_if_exists(doc, "04_settings_online_apis.png", "Figure 6: Settings - Unlimited Online LLM API Pool")

    doc.add_heading("3.5 Webcam Teleprompter HUD (Natural Eye Contact)", level=2)
    doc.add_paragraph(
        "Pressing Ctrl + Alt + T replaces the main window with a slim, top-bezel reading capsule positioned directly "
        "beneath your monitor webcam. It displays 15–20 word glanceable bullet points so you maintain natural eye contact "
        "with interviewers while reading talking points."
    )
    add_image_if_exists(doc, "06_teleprompter_bar.png", "Figure 7: Webcam Teleprompter HUD anchored to top monitor bezel")

    doc.add_heading("3.6 Intelligent 0ms Q&A Cache & Local Vector PDF Archiving", level=2)
    doc.add_paragraph(
        "Every solved question is indexed in cache/qa_cache.json with exact and Jaccard token similarity matching. "
        "Repeated or slightly rephrased questions return in 0ms with zero token cost. In addition, every answer is "
        "automatically compiled into an archived vector PDF in saved_interviews/."
    )
    add_image_if_exists(doc, "08_saved_pdf_report.png", "Figure 8: Local PDF Interview Archive and Q&A Cache")

    # -------------------------------------------------------------
    # Section 4: Installation Guide
    # -------------------------------------------------------------
    h4 = doc.add_heading("4. Installation Guide & Packaging Options", level=1)
    h4.paragraph_format.space_before = Pt(14)
    h4.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "ApexPilot AI provides three deployment options depending on your environment:"
    )

    doc.add_heading("4.1 Method A: Standalone Windows Installer (Recommended)", level=2)
    doc.add_paragraph(
        "• Installer Path: installer_dist/ApexPilotAI_Setup.exe (45.6 MB)\n"
        "• Guided wizard installs to C:\\Program Files\\ApexPilot AI with Start Menu and Desktop shortcuts.\n"
        "• Registers an uninstaller in Windows Apps & Features.\n"
        "• Unattended Silent Install Command: ApexPilotAI_Setup.exe /VERYSILENT /NORESTART"
    )

    doc.add_heading("4.2 Method B: Standalone Portable Binary", level=2)
    doc.add_paragraph(
        "• Binary Location: dist/ApexPilotAI/ApexPilotAI.exe\n"
        "• Run directly from any folder or USB drive with zero installation required."
    )

    doc.add_heading("4.3 Method C: Virtual Environment (Developer Installation)", level=2)
    doc.add_paragraph(
        "• 1-Click Launcher: Double-click run.bat\n"
        "• Or manual setup in PowerShell:\n"
        "    python -m venv .venv\n"
        "    .\\.venv\\Scripts\\activate\n"
        "    pip install -r requirements.txt\n"
        "    python main.py"
    )

    # -------------------------------------------------------------
    # Section 5: Setup & Configuration Guide
    # -------------------------------------------------------------
    h5 = doc.add_heading("5. Setup & Configuration Walkthrough", level=1)
    h5.paragraph_format.space_before = Pt(14)
    h5.paragraph_format.space_after = Pt(6)

    doc.add_heading("5.1 Local LLM Setup (Ollama / LM Studio)", level=2)
    doc.add_paragraph(
        "1. Install Ollama from ollama.com.\n"
        "2. Run: ollama pull qwen2.5-coder:7b (or llama3.2:3b for smaller systems).\n"
        "3. In ApexPilot AI Settings -> Local & Routing, verify Provider is 'ollama', URL is 'http://127.0.0.1:11434', and Model is 'qwen2.5-coder:7b'.\n"
        "4. Click '⚡ Test Primary Connection' to verify status."
    )

    doc.add_heading("5.2 Online LLM API Key Pool Setup", level=2)
    doc.add_paragraph(
        "1. Open Settings -> Online API Pool.\n"
        "2. Paste API keys for your preferred providers (Groq, OpenAI, Anthropic Claude, xAI Grok, DeepSeek, Gemini).\n"
        "3. Under 'Add Custom Endpoint', configure any custom OpenAI-compatible server (OpenRouter, Mistral, Together AI).\n"
        "4. Enable 'Fastest-First Race Mode' and 'Automatic 429 Failover'."
    )

    doc.add_heading("5.3 Ingesting Resume & Target Job Description", level=2)
    doc.add_paragraph(
        "1. Open Settings -> Resume Context.\n"
        "2. Click '📂 Load Resume (.pdf, .txt, .md)' and select your resume file.\n"
        "3. Click '📂 Load JD (.pdf, .txt, .md)' and select the job description or paste it into the editor.\n"
        "4. Click 'Save & Apply'."
    )

    # -------------------------------------------------------------
    # Section 6: Global Hotkeys Reference
    # -------------------------------------------------------------
    h6 = doc.add_heading("6. Global Hotkeys Reference", level=1)
    h6.paragraph_format.space_before = Pt(14)
    h6.paragraph_format.space_after = Pt(6)

    hotkey_headers = ["Hotkey", "Action", "Description"]
    hotkey_widths = [1.8, 1.8, 2.9]
    hotkey_data = [
        ["Ctrl + Alt + H", "Panic / Boss Key", "Instantly hides or unhides the HUD with zero latency."],
        ["Ctrl + Alt + S", "Screen Snip OCR", "Drag crosshair over coding problem on screen (<25ms local OCR)."],
        ["Ctrl + Alt + T", "Teleprompter HUD", "Swaps between main HUD and top-bezel eye-contact teleprompter bar."],
        ["Ctrl + Alt + X", "Click-Through Toggle", "Toggles click-through so mouse clicks pass directly into Zoom/Teams."],
        ["Ctrl + Alt + C", "Silent Copy", "Copies clean code block directly to clipboard."],
        ["Ctrl + Alt + A", "Instant Solve", "Solves highlighted text or detected audio question."],
        ["Border Drag", "Resize HUD", "Drag any of the 8 border edges or corners to freely resize."]
    ]
    table_hotkeys = doc.add_table(rows=1, cols=3)
    style_table(table_hotkeys, hotkey_widths, hotkey_headers, hotkey_data)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # Section 7: Verification & Testing
    # -------------------------------------------------------------
    h7 = doc.add_heading("7. System Verification & Unit Test Suite", level=1)
    h7.paragraph_format.space_before = Pt(14)
    h7.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "ApexPilot AI includes an automated unit test suite verifying all 13 core subsystems:\n"
        "   .\\.venv\\Scripts\\python.exe test_stealth.py\n\n"
        "All 13 tests validate:\n"
        "• Win32 display affinity (WDA_EXCLUDEFROMCAPTURE: 0x11)\n"
        "• Real-time LLM streaming across 5 modes\n"
        "• Native Windows Media OCR text extraction\n"
        "• Context store & resume injection\n"
        "• Audio question boundary heuristics\n"
        "• Qt6 UI headless initialization\n"
        "• Custom instructions / persona rules enforcement\n"
        "• Rapid stream interruption cancellation abort\n"
        "• Window geometry persistence\n"
        "• QA cache exact & fuzzy lookup + vector PDF generation\n"
        "• Dynamic custom online LLM endpoints management\n"
        "• Document text extraction (.pdf, .txt, .md)\n"
        "• Click-through toggling and window opacity transparency"
    )

    doc.save(str(OUTPUT_DOCX))
    size_kb = OUTPUT_DOCX.stat().st_size / 1024
    print(f"[SUCCESS] Comprehensive Word Document generated successfully at:")
    print(f"          {OUTPUT_DOCX} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_word_doc()
