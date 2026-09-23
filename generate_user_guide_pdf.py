"""
ApexPilot AI - User Guide PDF Generator with Embedded Application Images
=========================================================================
Generates an executive, beautifully styled visual user guide in PDF format
with authentic high-resolution screenshots embedded inline.
"""

import sys
import base64
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument, QPdfWriter, QPageSize, QPageLayout
from PySide6.QtCore import QMarginsF

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PDF = BASE_DIR / "ApexPilot_AI_User_Guide.pdf"
IMG_DIR = BASE_DIR / "docs" / "images"


def img_to_b64_tag(img_name: str, caption: str = "", max_width: int = 560) -> str:
    img_path = IMG_DIR / img_name
    if not img_path.exists():
        return f"<p style='color: red;'>[Image missing: {img_name}]</p>"

    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    caption_html = f"<div style='font-size: 11px; color: #64748b; font-style: italic; margin-top: 6px;'>{caption}</div>" if caption else ""
    return f"""
    <div style="text-align: center; margin: 18px 0;">
        <img src="data:image/png;base64,{b64}" width="{max_width}" style="border: 1px solid #334155; border-radius: 6px;" />
        {caption_html}
    </div>
    """


def build_guide_html() -> str:
    now_str = datetime.now().strftime("%B %d, %Y")

    img_coding = img_to_b64_tag("01_stealth_hud_coding.png", "Figure 1: Master Stealth HUD in StealthCoder Mode (LeetCode LRU Cache Solution)")
    img_star = img_to_b64_tag("02_star_behavioral_resume.png", "Figure 2: STAR Behavioral Mode tailoring response to candidate resume metrics")
    img_routing = img_to_b64_tag("03_settings_llm_routing.png", "Figure 3: Settings - Local LLM Engine, Fastest-First Race Mode & 429 Failover")
    img_apis = img_to_b64_tag("04_settings_online_apis.png", "Figure 4: Settings - Unlimited Online LLM API Pool (Groq, OpenAI, Claude, Grok, Gemini)")
    img_resume = img_to_b64_tag("05_settings_resume_jd.png", "Figure 5: Settings - Resume Context with 1-Click PDF/TXT/MD Loaders")
    img_tele = img_to_b64_tag("06_teleprompter_bar.png", "Figure 6: Webcam Teleprompter HUD anchored to top monitor bezel for eye contact")
    img_snip = img_to_b64_tag("07_snip_tool_overlay.png", "Figure 7: Screen Snip Tool with <25ms Native Windows Media OCR")
    img_pdf = img_to_b64_tag("08_saved_pdf_report.png", "Figure 8: Local PDF Interview Archive and Q&A Cache")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                margin: 18mm;
            }}
            body {{
                font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
                color: #1e293b;
                line-height: 1.5;
                font-size: 12px;
            }}
            h1 {{
                color: #0284c7;
                font-size: 24px;
                border-bottom: 2.5px solid #0284c7;
                padding-bottom: 6px;
                margin-top: 0;
            }}
            h2 {{
                color: #0369a1;
                font-size: 16px;
                border-bottom: 1.5px solid #cbd5e1;
                padding-bottom: 4px;
                margin-top: 22px;
            }}
            h3 {{
                color: #0f172a;
                font-size: 13px;
                margin-top: 14px;
                margin-bottom: 4px;
            }}
            p, li {{
                color: #334155;
            }}
            .badge {{
                display: inline-block;
                background-color: #0284c7;
                color: #ffffff;
                padding: 3px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
            }}
            .card {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #0284c7;
                padding: 12px;
                margin: 14px 0;
                border-radius: 4px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12px 0;
                font-size: 11px;
            }}
            th, td {{
                border: 1px solid #cbd5e1;
                padding: 6px 10px;
                text-align: left;
            }}
            th {{
                background-color: #f1f5f9;
                color: #0f172a;
                font-weight: bold;
            }}
            code {{
                background-color: #e2e8f0;
                color: #0f172a;
                padding: 1px 4px;
                border-radius: 3px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11px;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #94a3b8;
                font-size: 10px;
                border-top: 1px solid #e2e8f0;
                padding-top: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>ApexPilot AI &mdash; User Guide & Visual Walkthrough</h1>
        <p><b>Executive Technical Interview Copilot Manual with Application Screenshots</b></p>
        <p><i>Generated on {now_str} &bull; Version 2.0.0 &bull; Windows 10/11 64-bit Edition</i></p>

        <div class="card">
            <b>ApexPilot AI Overview:</b><br>
            ApexPilot AI combines the best features of <b>GhostPilot AI</b> (100% Zoom/Teams screen-share invisibility),
            <b>StealthCoder</b> (<25ms native OCR coding copilot), <b>Parakeet AI</b> (low-latency audio question detection),
            <b>HuddleMate</b> (live meeting executive summaries), and <b>Final Round AI</b> (resume-powered STAR behavioral & system design answers).
        </div>

        <h2>1. Tailoring Answers with Candidate Resume & Job Description (JD)</h2>
        <p>
            Standard AI tools produce generic, easily detectable textbook answers. ApexPilot AI solves this through its
            <b>Dual-Context Ingestion Engine</b>. Your answers are deeply anchored in your authentic work history, past project scale,
            and quantifiable metrics, while directly matching the target employer's job description.
        </p>

        <h3>1-Click File Loading (.pdf, .txt, .md)</h3>
        <p>You can either paste your text or click the 1-click document loaders in Settings:</p>
        <ul>
            <li><b>📂 Load Resume (.pdf, .txt, .md)</b>: Automatically extracts text from single or multi-page PDF resumes using <code>pypdf</code>.</li>
            <li><b>📂 Load JD (.pdf, .txt, .md)</b>: Ingests the company's job requirements, required technologies, and seniority expectations.</li>
        </ul>

        {img_resume}

        <h3>How Dual-Context Ingestion Drives Responses</h3>
        <ul>
            <li><b>STAR Behavioral Mode</b>: Automatically formats questions into <b>Situation, Task, Action, Result, and Key Takeaway</b>, pulling exact metrics (e.g. <i>"reduced latency from 4.5s to 18ms; saved 40% in compute"</i>) from your resume.</li>
            <li><b>System Design Mode</b>: Designs scalable architectures utilizing technologies you have proven production experience with, aligning with the target company's cloud infrastructure.</li>
            <li><b>Teleprompter Mode</b>: Distills complex background experiences into 1-2 sentence glanceable cues for webcam eye contact.</li>
        </ul>

        {img_star}

        <h2>2. Master Stealth HUD & Coding Copilot</h2>
        <p>
            The primary interface is a frameless, dark obsidian HUD with dynamic 8-edge resizing and persistent dimensions.
            In <b>StealthCoder Mode</b>, it generates:
        </p>
        <ul>
            <li><b>Intuition & Approach</b>: Algorithmic strategy, time complexity O(...), space complexity O(...).</li>
            <li><b>Optimal Production Code</b>: Clean syntax-highlighted code in your chosen language (Python, C++, Java, Go, Rust, TypeScript).</li>
            <li><b>Speakable Step-by-Step Points</b>: Natural first-person explanations designed to be spoken aloud while live coding.</li>
            <li><b>Edge Cases & Dry Run</b>: Analysis of null inputs, single-node cases, and constraints.</li>
        </ul>

        {img_coding}

        <h2>3. Local LLMs & Speculative Race Routing</h2>
        <p>
            ApexPilot AI offers dual-engine support, allowing you to run 100% offline or harness ultra-fast cloud models:
        </p>
        <ul>
            <li><b>⚡ Fastest-First Speculative Duel</b>: Concurrently sends prompts to both your local LLM and cloud LLM; the fastest first token stream wins and renders in real-time.</li>
            <li><b>🔄 Automatic 429 Failover</b>: If an online provider encounters rate limits (HTTP 429), the engine automatically rotates to the next API key or fallback provider with zero interruption.</li>
        </ul>

        {img_routing}

        <h2>4. Unlimited Online LLM API Pool</h2>
        <p>
            Connect to any provider with zero configuration:
        </p>
        <ul>
            <li><b>Groq (300+ tok/s)</b>: Delivers sub-second solutions on specialized LPU hardware.</li>
            <li><b>OpenAI (GPT-4o)</b>: Premier system design and architecture reasoning.</li>
            <li><b>Anthropic (Claude 3.5 Sonnet)</b>: Exceptional complex algorithmic and edge-case mastery.</li>
            <li><b>Custom Endpoints</b>: Add unlimited OpenAI-compatible endpoints (OpenRouter, Mistral, Together AI, Perplexity).</li>
        </ul>

        {img_apis}

        <h2>5. Webcam Teleprompter & LeetCode Screen Snip</h2>
        <p>
            <b>Natural Eye Contact HUD:</b> Pressing <code>Ctrl + Alt + T</code> activates a discreet reading bar right under your webcam bezel.
        </p>

        {img_tele}

        <p>
            <b>Sub-25ms LeetCode Snip:</b> Pressing <code>Ctrl + Alt + S</code> lets you drag a crosshair over any coding problem. Text is extracted locally using native Windows Media OCR in under 25ms.
        </p>

        {img_snip}

        <h2>6. Q&A Instant Cache & Local PDF Archiving</h2>
        <p>
            Every solved question is indexed in <code>qa_cache.json</code> and compiled into an archived vector PDF in <code>saved_interviews/</code>.
            Rephrased questions return in <b>0ms with zero token cost</b>.
        </p>

        {img_pdf}

        <h2>7. Global Hotkeys & Controls Reference</h2>
        <table>
            <tr>
                <th>Hotkey</th>
                <th>Function</th>
                <th>Behavior</th>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + H</b></td>
                <td>Panic / Boss Key</td>
                <td>Instantly hides/restores the stealth HUD with zero latency.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + S</b></td>
                <td>Screen Snip OCR</td>
                <td>Snip any screen region; extracts text in &lt;25ms locally.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + T</b></td>
                <td>Teleprompter Bar</td>
                <td>Toggles top-bezel eye-contact teleprompter.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + C</b></td>
                <td>Silent Copy</td>
                <td>Copies clean code block directly to clipboard.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + A</b></td>
                <td>Instant Solve</td>
                <td>Solves current highlighted question or speech audio.</td>
            </tr>
            <tr>
                <td><b>Drag Borders</b></td>
                <td>Window Resize</td>
                <td>Freely resize HUD from any edge or corner.</td>
            </tr>
        </table>

        <h2>8. Getting Started</h2>
        <p><b>Running from Installer:</b> Run <code>d:\interAI\installer_dist\ApexPilotAI_Setup.exe</code>.</p>
        <p><b>Running in Development:</b> Double-click <code>run.bat</code> to launch within the virtual environment.</p>

        <div class="footer">
            ApexPilot AI Comprehensive User Guide &bull; Confidential Candidate Productivity Tool &bull; Page 1 of 1
        </div>
    </body>
    </html>
    """


def generate_guide_pdf():
    app = QApplication.instance() or QApplication(sys.argv)

    print("[*] Compiling ApexPilot AI Visual User Guide PDF...")
    html_content = build_guide_html()

    doc = QTextDocument()
    doc.setHtml(html_content)

    writer = QPdfWriter(str(OUTPUT_PDF))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    layout = QPageLayout(
        QPageSize(QPageSize.PageSizeId.A4),
        QPageLayout.Orientation.Portrait,
        QMarginsF(12, 12, 12, 12)
    )
    writer.setPageLayout(layout)

    doc.print_(writer)

    if OUTPUT_PDF.exists():
        size_kb = OUTPUT_PDF.stat().st_size / 1024
        print(f"[SUCCESS] Visual User Guide PDF generated at:")
        print(f"          {OUTPUT_PDF} ({size_kb:.1f} KB)")
    else:
        print("[ERROR] PDF generation failed!")


if __name__ == "__main__":
    generate_guide_pdf()
