"""
ApexPilot AI - Comprehensive PDF Documentation Generator
=========================================================
Generates an executive, fully styled multi-page PDF documentation manual
covering all system features, architecture, stealth mechanics, capabilities,
installation methods, local & online LLMs setup, Q&A cache, and usage instructions.
"""

import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument, QPdfWriter, QPageSize, QPageLayout
from PySide6.QtCore import QMarginsF

OUTPUT_PDF = Path(__file__).resolve().parent / "ApexPilot_AI_Comprehensive_Documentation.pdf"


def build_documentation_html() -> str:
    now_str = datetime.now().strftime("%B %d, %Y")
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
                font-size: 11px;
            }}
            h1 {{
                color: #0284c7;
                font-size: 22px;
                border-bottom: 2.5px solid #0284c7;
                padding-bottom: 6px;
                margin-top: 0;
            }}
            h2 {{
                color: #0369a1;
                font-size: 15px;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 4px;
                margin-top: 18px;
            }}
            h3 {{
                color: #0f172a;
                font-size: 12px;
                margin-top: 12px;
                margin-bottom: 4px;
            }}
            p, li {{
                color: #334155;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
                font-size: 11px;
            }}
            th {{
                background-color: #0284c7;
                color: #ffffff;
                text-align: left;
                padding: 6px 8px;
                font-weight: bold;
            }}
            td {{
                border: 1px solid #cbd5e1;
                padding: 5px 8px;
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
                font-size: 10px;
            }}
            .code-block {{
                background-color: #0f172a;
                color: #38bdf8;
                font-family: 'Consolas', monospace;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 11px;
                margin: 8px 0;
            }}
            .highlight-box {{
                background-color: #f0fdf4;
                border-left: 4px solid #10b981;
                padding: 8px 12px;
                margin: 10px 0;
                border-radius: 4px;
            }}
            .footer {{
                margin-top: 25px;
                text-align: center;
                color: #94a3b8;
                font-size: 10px;
                border-top: 1px solid #e2e8f0;
                padding-top: 6px;
            }}
        </style>
    </head>
    <body>
        <h1>ApexPilot AI &mdash; Comprehensive System Manual</h1>
        <p><b>Executive Technical Reference: Architecture, Capabilities, Installation & Setup</b></p>
        <p><i>Generated on {now_str} &bull; Version 2.0.0 &bull; Windows 10/11 64-bit Architecture</i></p>

        <div class="highlight-box">
            <b>System Purpose:</b><br/>
            ApexPilot AI is an ultra-low-latency, 100% undetectable stealth interview and meeting copilot for Windows.
            It unifies the flagship features of <b>GhostPilot AI</b> (100% Zoom/Teams invisibility), <b>StealthCoder</b> (&lt;25ms native OCR coding copilot),
            <b>Parakeet AI</b> (dual-channel WASAPI live audio capture + VAD), <b>HuddleMate</b> (live meeting executive summaries), and
            <b>Final Round AI</b> (resume-powered STAR behavioral and system design answers).
        </div>

        <h2>1. Unified Feature Matrix vs. Market Alternatives</h2>
        <table>
            <tr>
                <th>Feature / Capability</th>
                <th>Inspired By</th>
                <th>ApexPilot AI Superpower & Implementation</th>
            </tr>
            <tr>
                <td><b>Undetectable Screen Protection</b></td>
                <td>GhostPilot AI</td>
                <td>Hardware-level <code>SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE: 0x11)</code>. 100% invisible to Zoom, Teams, Meet, Discord, OBS, WebRTC.</td>
            </tr>
            <tr>
                <td><b>Discreet Webcam Teleprompter</b></td>
                <td>GhostPilot AI</td>
                <td>Horizontal floating HUD placed directly beneath monitor webcam for natural eye contact while reading talking points.</td>
            </tr>
            <tr>
                <td><b>Native LeetCode Screen OCR</b></td>
                <td>StealthCoder</td>
                <td>Sub-25ms native hardware OCR via <code>Windows.Media.Ocr</code>. Zero external heavy dependencies.</td>
            </tr>
            <tr>
                <td><b>Optimal Algorithmic Solver</b></td>
                <td>StealthCoder</td>
                <td>Generates optimal solution, Big-O Time & Space complexity, speakable step-by-step points, and dry-run edge cases.</td>
            </tr>
            <tr>
                <td><b>Dual-Channel Audio & VAD</b></td>
                <td>Parakeet AI</td>
                <td>WASAPI loopback capture (interviewer audio) + candidate microphone streaming with Voice Activity Detection.</td>
            </tr>
            <tr>
                <td><b>Real-Time Question Detection</b></td>
                <td>Parakeet AI</td>
                <td>NLP heuristic engine detects questions in real time (<i>"How would you scale..."</i>, <i>"Can you explain..."</i>) with 1-click solve.</td>
            </tr>
            <tr>
                <td><b>Meeting Executive Notes</b></td>
                <td>HuddleMate</td>
                <td>Auto-generates executive summaries, key decisions, action items, and live proactive talking points.</td>
            </tr>
            <tr>
                <td><b>Resume Context Tailoring</b></td>
                <td>Final Round AI</td>
                <td>1-click PDF/TXT/MD document loaders ingest candidate resume and target JD to ground all answers in authentic past metrics.</td>
            </tr>
            <tr>
                <td><b>STAR Method Engine</b></td>
                <td>Final Round AI</td>
                <td>Structures behavioral interview responses strictly as Situation, Task, Action, Result, and Key Takeaway.</td>
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
                <td>Rotates through unlimited online providers (OpenAI, Grok, Groq, Claude, DeepSeek, Gemini, OpenRouter) upon rate limits.</td>
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
            <tr>
                <td><b>Border Drag</b></td>
                <td>Dynamic Resize</td>
                <td>Drag any of the 8 border edges or corners to freely resize the HUD.</td>
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

        <h2>4. Installation Guide & Packaging Options</h2>
        <h3>Method A: Standalone Windows Installer (Recommended)</h3>
        <p>
            The easiest method for general users. Requires no Python, virtual environments, or command line tools.
        </p>
        <ul>
            <li><b>File:</b> <code>d:\interAI\installer_dist\ApexPilotAI_Setup.exe</code> (45.6 MB)</li>
            <li><b>Features:</b> Full guided setup wizard, desktop icon creation, Start Menu group, and Windows Control Panel uninstaller.</li>
            <li><b>Silent Installation:</b> Run <code>ApexPilotAI_Setup.exe /VERYSILENT /NORESTART</code> for unattended deployment.</li>
        </ul>

        <h3>Method B: Standalone Portable Binary</h3>
        <p>
            Run <code>d:\interAI\dist\ApexPilotAI\ApexPilotAI.exe</code> directly from any folder or USB drive with zero installation.
        </p>

        <h3>Method C: Virtual Environment (Developer Mode)</h3>
        <p>
            Double-click <code>run.bat</code> or run in PowerShell:
        </p>
        <div class="code-block">
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
        </div>

        <h2>5. Setup & Configuration Walkthrough</h2>
        <h3>A. Connecting Local LLMs (Ollama / LM Studio)</h3>
        <ol>
            <li>Install Ollama from <code>ollama.com</code> and run: <code>ollama pull qwen2.5-coder:7b</code>.</li>
            <li>Open ApexPilot AI Settings &rarr; <b>Local & Routing</b>.</li>
            <li>Set Provider: <code>ollama</code>, URL: <code>http://127.0.0.1:11434</code>, Model: <code>qwen2.5-coder:7b</code>.</li>
            <li>Click <b>Test Primary Connection</b> to verify.</li>
        </ol>

        <h3>B. Configuring Online LLMs & Unlimited API Endpoints</h3>
        <ol>
            <li>In Settings &rarr; <b>Online API Pool</b>, enable your preferred cloud provider (Groq 300+ tok/s, OpenAI, Claude, Grok, Gemini, DeepSeek).</li>
            <li>Under <b>Add Custom Endpoint</b>, connect to OpenRouter, Mistral, Perplexity, Together AI, or any OpenAI-compatible server.</li>
            <li>Enable <b>Fastest-First Race Mode</b> to race local vs cloud models, and <b>Automatic 429 Failover</b> for seamless rate-limit handling.</li>
        </ol>

        <h3>C. Ingesting Candidate Resume & Target Job Description</h3>
        <ol>
            <li>In Settings &rarr; <b>Resume Context</b>, click <b>📂 Load Resume (.pdf, .txt, .md)</b>.</li>
            <li>The built-in <code>pypdf</code> parser automatically reads and populates your work experience.</li>
            <li>Click <b>📂 Load JD (.pdf, .txt, .md)</b> or paste target role requirements.</li>
            <li>Click <b>Save & Apply</b>. All future answers in STAR Behavioral and System Design modes will cite your authentic metrics.</li>
        </ol>

        <h2>6. Custom Instructions & Persona Engine</h2>
        <p>Under <b>Settings &rarr; Custom Instructions</b>, enter behavioral directives:</p>
        <ul>
            <li><i>"Always write modern C++20 with std::ranges and unordered_map."</i></li>
            <li><i>"Keep all explanations under 3 concise speakable bullet points."</i></li>
            <li><i>"Adopt the persona of a Principal Infrastructure Architect."</i></li>
        </ul>
        <p>When configured, the AI strictly enforces your custom rules. If left blank, it behaves normally like standard programs.</p>

        <h2>7. Rapid Interruption & Dynamic Window Resizing</h2>
        <ul>
            <li><b>Interruption Handling:</b> Submitting a new question instantly aborts active token streams in &lt;50ms with zero queuing lag.</li>
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
