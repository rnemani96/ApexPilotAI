"""
ApexPilot AI - Comprehensive PDF Documentation Generator
=========================================================
Generates an executive, fully styled multi-page PDF documentation manual
covering all system features, architecture, stealth mechanics, local & online LLMs,
Q&A cache, and usage instructions.
"""

import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument, QPdfWriter, QPageSize, QPageLayout
from PySide6.QtCore import QMarginsF

OUTPUT_PDF = Path(__file__).resolve().parent / "ApexPilot_AI_Comprehensive_Documentation.pdf"


def build_documentation_html() -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                margin: 20mm;
            }}
            body {{
                font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
                color: #1e293b;
                line-height: 1.6;
                font-size: 13px;
            }}
            h1 {{
                color: #0284c7;
                font-size: 26px;
                border-bottom: 3px solid #0284c7;
                padding-bottom: 8px;
                margin-top: 0;
            }}
            h2 {{
                color: #0369a1;
                font-size: 18px;
                border-bottom: 1.5px solid #cbd5e1;
                padding-bottom: 5px;
                margin-top: 24px;
            }}
            h3 {{
                color: #0f172a;
                font-size: 14px;
                margin-top: 16px;
                margin-bottom: 6px;
            }}
            p, li {{
                color: #334155;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 14px 0;
                font-size: 12px;
            }}
            th {{
                background-color: #0284c7;
                color: #ffffff;
                text-align: left;
                padding: 8px;
                font-weight: bold;
            }}
            td {{
                border: 1px solid #cbd5e1;
                padding: 7px 8px;
            }}
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            .badge {{
                background-color: #e0f2fe;
                color: #0369a1;
                padding: 2px 6px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }}
            .code-block {{
                background-color: #0f172a;
                color: #38bdf8;
                font-family: 'Consolas', monospace;
                padding: 10px 14px;
                border-radius: 6px;
                font-size: 12px;
                margin: 10px 0;
            }}
            .highlight-box {{
                background-color: #f0fdf4;
                border-left: 4px solid #10b981;
                padding: 10px 14px;
                margin: 12px 0;
                border-radius: 4px;
            }}
            .warning-box {{
                background-color: #fffbeb;
                border-left: 4px solid #f59e0b;
                padding: 10px 14px;
                margin: 12px 0;
                border-radius: 4px;
            }}
            .footer {{
                text-align: center;
                color: #94a3b8;
                font-size: 10px;
                margin-top: 30px;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
            }}
        </style>
    </head>
    <body>

        <h1>🦅 ApexPilot AI — Complete System Manual</h1>
        <p><b>Executive Technical Documentation & User Guide</b> | Version 1.0.0 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="highlight-box">
            <b>Mission Statement:</b> ApexPilot AI is an ultra-low-latency, local-first stealth interview and meeting copilot for Windows.
            It unifies the flagship capabilities of <b>GhostPilot AI</b>, <b>StealthCoder</b>, <b>Parakeet AI</b>, <b>HuddleMate</b>, and <b>Final Round AI</b> into a single, high-performance architecture running on local and unlimited online LLMs.
        </div>

        <h2>1. Competitive Feature Matrix</h2>
        <table>
            <tr>
                <th>Feature Capability</th>
                <th>Inspiration</th>
                <th>ApexPilot AI Implementation</th>
            </tr>
            <tr>
                <td><b>Undetectable Screen Protection</b></td>
                <td>GhostPilot AI</td>
                <td>Win32 <code>SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)</code>. 100% invisible to Zoom, Google Meet, Microsoft Teams, Discord, OBS, WebRTC screen shares.</td>
            </tr>
            <tr>
                <td><b>Discreet Teleprompter HUD</b></td>
                <td>GhostPilot AI</td>
                <td>Sleek floating HUD positioned directly under the monitor's webcam so you maintain natural eye contact while reading speakable talking points.</td>
            </tr>
            <tr>
                <td><b>Screen Snip & Code OCR</b></td>
                <td>StealthCoder</td>
                <td>Press <code>Ctrl + Alt + S</code> to freeze screen and select any LeetCode problem. Built-in Windows Media OCR extracts text locally in &lt;25ms.</td>
            </tr>
            <tr>
                <td><b>Optimal Algorithmic Solver</b></td>
                <td>StealthCoder</td>
                <td>Generates optimal solution, Big-O Time & Space complexity, step-by-step speakable walkthrough, and dry-run edge cases.</td>
            </tr>
            <tr>
                <td><b>Dual-Channel Audio & VAD</b></td>
                <td>Parakeet AI</td>
                <td>Windows WASAPI loopback capture (interviewer audio) + candidate microphone streaming with Voice Activity Detection.</td>
            </tr>
            <tr>
                <td><b>Real-Time Question Detection</b></td>
                <td>Parakeet AI</td>
                <td>NLP heuristic engine detects questions in real time ("How would you scale...", "Can you explain...") and offers instant auto-solve.</td>
            </tr>
            <tr>
                <td><b>Meeting Executive Notes</b></td>
                <td>HuddleMate</td>
                <td>Auto-generates executive meeting summaries, key decisions, action items, and live proactive talking points.</td>
            </tr>
            <tr>
                <td><b>Resume Context Tailoring</b></td>
                <td>Final Round AI</td>
                <td>Ingests candidate resume and job description (JD) so solutions reference authentic past projects, tech stacks, and quantifiable metrics.</td>
            </tr>
            <tr>
                <td><b>STAR Method Engine</b></td>
                <td>Final Round AI</td>
                <td>Structures behavioral interview responses strictly as Situation, Task, Action, and Result.</td>
            </tr>
            <tr>
                <td><b>Intelligent 0ms QA Cache</b></td>
                <td>ApexPilot Core</td>
                <td>Exact and fuzzy token similarity matching against prior questions to serve cached answers instantly with 0ms latency and 0 API cost.</td>
            </tr>
            <tr>
                <td><b>Automatic Local PDF Archiving</b></td>
                <td>ApexPilot Core</td>
                <td>Every question and answer is automatically formatted into high-resolution vector PDFs saved to <code>saved_interviews/</code>.</td>
            </tr>
            <tr>
                <td><b>Speculative Duel (Fastest-First)</b></td>
                <td>ApexPilot Core</td>
                <td>Races Local LLM vs Online LLM in parallel; the fastest to yield tokens wins while the slower stream is aborted immediately.</td>
            </tr>
            <tr>
                <td><b>Automatic 429 Failover</b></td>
                <td>ApexPilot Core</td>
                <td>Rotates through unlimited online providers (OpenAI, Grok, Groq, Claude, DeepSeek, Gemini, OpenRouter) upon rate limits or quota errors.</td>
            </tr>
        </table>

        <h2>2. Global System Hotkeys</h2>
        <table>
            <tr>
                <th>Shortcut</th>
                <th>Function</th>
                <th>Description</th>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + H</b></td>
                <td>Panic / Boss Key</td>
                <td>Instantly hides or unhides the overlay HUD without closing the background process.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + S</b></td>
                <td>Screen Snipping Tool</td>
                <td>Freezes screen with crosshairs to drag-select any coding problem or diagram for OCR.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + T</b></td>
                <td>Webcam Teleprompter</td>
                <td>Toggles the minimalist top-bezel eye-contact teleprompter reader bar.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + C</b></td>
                <td>Silent Code Copy</td>
                <td>Strips markdown and comments and copies clean production code directly to clipboard.</td>
            </tr>
            <tr>
                <td><b>Ctrl + Alt + A</b></td>
                <td>Instant Solve</td>
                <td>Triggers reasoning engine on the current query or selected text.</td>
            </tr>
        </table>

        <h2>3. Stealth Mechanics & Anti-Detection Architecture</h2>
        <p>ApexPilot AI communicates directly with the Windows Desktop Window Manager (DWM) kernel API using <code>ctypes</code>:</p>
        <div class="code-block">
SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)  # 0x00000011
        </div>
        <p><b>How this protects you during live interviews:</b></p>
        <ul>
            <li><b>Zoom / Teams / Google Meet / Discord / OBS:</b> All desktop capture pipelines (DirectX Desktop Duplication API, Windows Graphics Capture, GDI BitBlt, WebRTC) receive a clean video buffer where ApexPilot AI is completely excluded.</li>
            <li><b>Physical Monitor:</b> The window is rendered by your GPU directly to your physical display output, remaining 100% visible and sharp to you.</li>
            <li><b>Click-Through Mode (<code>WS_EX_TRANSPARENT</code>):</b> Toggled via the HUD button to let mouse clicks pass directly through to your IDE or web browser.</li>
            <li><b>Non-Activating Focus (<code>WS_EX_NOACTIVATE</code>):</b> Clicking inside the HUD never steals keyboard focus from your code editor.</li>
            <li><b>Taskbar & Alt+Tab Hiding (<code>WS_EX_TOOLWINDOW</code>):</b> Prevents the application from showing in Windows Alt+Tab app switchers.</li>
        </ul>

        <h2>4. Local & Online LLM Connectivity</h2>
        <h3>Local LLM Setup (Private & Offline)</h3>
        <ul>
            <li><b>Ollama:</b> Default endpoint <code>http://127.0.0.1:11434</code> with models like <code>qwen2.5-coder:7b</code>, <code>llama3.2:3b</code>, <code>deepseek-r1:7b</code>.</li>
            <li><b>llama.cpp / llama-server:</b> Default endpoint <code>http://127.0.0.1:8080</code> for GGUF model execution.</li>
            <li><b>LM Studio / vLLM / LocalAI:</b> Standard OpenAI-compatible endpoint <code>http://127.0.0.1:1234/v1</code>.</li>
            <li><b>Built-in Mock Engine:</b> Works immediately out of the box with zero installation required.</li>
        </ul>

        <h3>Unlimited Online LLM Endpoints & Rate-Limit Failover</h3>
        <p>Under <b>Settings &rarr; Online API Pool</b>, users can configure any combination of APIs:</p>
        <ul>
            <li><b>OpenAI (ChatGPT):</b> <code>gpt-4o</code>, <code>gpt-4o-mini</code>, <code>o3-mini</code></li>
            <li><b>xAI (Grok):</b> <code>grok-2</code>, <code>grok-beta</code></li>
            <li><b>Groq (Ultra-Fast LPU):</b> <code>llama-3.3-70b-versatile</code> (generates at 300+ tokens/sec)</li>
            <li><b>Anthropic (Claude):</b> <code>claude-3-5-sonnet-20241022</code></li>
            <li><b>DeepSeek:</b> <code>deepseek-chat</code>, <code>deepseek-reasoner</code></li>
            <li><b>Google Gemini:</b> <code>gemini-2.0-flash</code></li>
            <li><b>Custom Endpoints:</b> Add OpenRouter, Mistral AI, Perplexity, Together AI, DeepInfra, or private LAN servers.</li>
        </ul>
        <div class="highlight-box">
            <b>Automatic 429 Failover:</b> When rate-limited (HTTP 429) or quota is exhausted, ApexPilot seamlessly rotates to the next enabled API in your pool without failing your answer.
        </div>

        <h2>5. Intelligent Q&A Cache & Local PDF Archiving</h2>
        <p>ApexPilot AI incorporates a two-tier persistent memory engine:</p>
        <ol>
            <li><b>0ms Instant Retrieval:</b> Incoming questions are normalized and matched against previously solved problems using Jaccard token similarity. Recurring or rephrased questions return instantly with 0ms latency and 0 API cost.</li>
            <li><b>Automatic Vector PDF Generation:</b> Every solved problem is saved as a styled vector PDF in <code>saved_interviews/</code>. Click the <b>📁 Saved PDFs</b> button on the toolbar to open the archive folder.</li>
        </ol>

        <h2>6. Custom Instructions & Persona Engine</h2>
        <p>Under <b>Settings &rarr; Custom Instructions</b>, you can enter custom behavioral directives:</p>
        <ul>
            <li><i>"Always write modern C++20 with vector and unordered_map."</i></li>
            <li><i>"Keep all explanations under 3 concise speakable bullet points."</i></li>
            <li><i>"Adopt the persona of a Principal Infrastructure Architect."</i></li>
        </ul>
        <p>When configured, the AI strictly enforces your custom rules. If left blank, it behaves normally like standard programs.</p>

        <h2>7. Rapid Interruption & Dynamic Window Resizing</h2>
        <ul>
            <li><b>Interruption Handling:</b> If an interviewer asks a follow-up or changes topic mid-stream, submitting a new question instantly aborts the active stream and begins answering the new query with zero queuing lag.</li>
            <li><b>Frameless Resizing:</b> Drag any border or corner (Left, Right, Top, Bottom, Corners) to resize the HUD freely. Resized dimensions are automatically remembered.</li>
        </ul>

        <div class="footer">
            ApexPilot AI &bull; Confidential Interview & Meeting Copilot &bull; Generated locally on Windows
        </div>
    </body>
    </html>
    """


def generate_pdf():
    app = QApplication.instance() or QApplication(sys.argv)
    html_content = build_documentation_html()

    doc = QTextDocument()
    doc.setHtml(html_content)

    writer = QPdfWriter(str(OUTPUT_PDF))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

    layout = QPageLayout()
    layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    layout.setOrientation(QPageLayout.Orientation.Portrait)
    layout.setMargins(QMarginsF(12, 12, 12, 12))
    writer.setPageLayout(layout)

    doc.print_(writer)
    print(f"Documentation PDF generated successfully at: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
