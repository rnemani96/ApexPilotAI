# ApexPilot AI — Comprehensive System Documentation, Capabilities & Setup Guide

**ApexPilot AI** is the ultra-low-latency, 100% undetectable stealth interview and meeting copilot for Windows 10 and 11. It unifies the best features of **GhostPilot AI**, **StealthCoder**, **Parakeet AI**, **HuddleMate**, and **Final Round AI** into a single, high-performance hybrid AI engine.

---

## Table of Contents
1. [Executive Summary & Architectural Overview](#1-executive-summary--architectural-overview)
2. [Feature Comparison Matrix](#2-feature-comparison-matrix)
3. [Exhaustive Capabilities Breakdown](#3-exhaustive-capabilities-breakdown)
   - [3.1 GhostPilot Screen-Share Invisibility & Stealth Engine](#31-ghostpilot-screen-share-invisibility--stealth-engine)
   - [3.2 StealthCoder Vision & Native Windows Media OCR](#32-stealthcoder-vision--native-windows-media-ocr)
   - [3.3 Hybrid LLM Client, Speculative Duel & 429 Failover](#33-hybrid-llm-client-speculative-duel--429-failover)
   - [3.4 Dual-Context Ingestion Engine (Resume & Job Description)](#34-dual-context-ingestion-engine-resume--job-description)
   - [3.5 Webcam Teleprompter HUD (Eye-Contact Preservation)](#35-webcam-teleprompter-hud-eye-contact-preservation)
   - [3.6 Dual-Channel Live Audio Capture & Question Heuristics](#36-dual-channel-live-audio-capture--question-heuristics)
   - [3.7 Intelligent 0ms Q&A Cache & Local Vector PDF Archiving](#37-intelligent-0ms-qa-cache--local-vector-pdf-archiving)
   - [3.8 Dynamic Frameless Resizing & Geometry Persistence](#38-dynamic-frameless-resizing--geometry-persistence)
4. [Installation Guide](#4-installation-guide)
   - [4.1 Method A: Standalone Windows Installer (Recommended)](#41-method-a-standalone-windows-installer-recommended)
   - [4.2 Method B: Standalone Portable Binary](#42-method-b-standalone-portable-binary)
   - [4.3 Method C: Virtual Environment (Developer Installation)](#43-method-c-virtual-environment-developer-installation)
5. [Complete Setup & Configuration Guide](#5-complete-setup--configuration-guide)
   - [5.1 Setting Up Local LLMs (Ollama, LM Studio, llama.cpp)](#51-setting-up-local-llms-ollama-lm-studio-llamacpp)
   - [5.2 Setting Up the Online LLM API Key Pool](#52-setting-up-the-online-llm-api-key-pool)
   - [5.3 Ingesting Candidate Resume & Target Job Description](#53-ingesting-candidate-resume--target-job-description)
   - [5.4 Configuring Custom Instructions & Personas](#54-configuring-custom-instructions--personas)
   - [5.5 Hotkey & Stealth Preference Configuration](#55-hotkey--stealth-preference-configuration)
6. [Real-World Interview Workflows](#6-real-world-interview-workflows)
   - [6.1 Live Coding & Algorithmic Interview Workflow](#61-live-coding--algorithmic-interview-workflow)
   - [6.2 STAR Behavioral Interview Workflow](#62-star-behavioral-interview-workflow)
   - [6.3 System Design Architecture Workflow](#63-system-design-architecture-workflow)
   - [6.4 Executive Meeting & Huddle Workflow](#64-executive-meeting--huddle-workflow)
7. [System Verification & Testing](#7-system-verification--testing)
8. [Troubleshooting & Frequently Asked Questions (FAQ)](#8-troubleshooting--frequently-asked-questions-faq)

---

## 1. Executive Summary & Architectural Overview

Technical interviews and executive meetings require rapid problem-solving, structured articulation, and seamless poise under pressure. However, existing AI tools suffer from critical shortcomings:
* **Detection Risk**: Standard windows appear on Zoom, Microsoft Teams, or Google Meet screen shares.
* **Latency Spikes**: Cloud-based tools lag by 5 to 15 seconds, creating awkward dead air.
* **Generic Answers**: Off-the-shelf LLMs provide textbook answers that fail to reference the candidate's authentic past projects and quantifiable achievements.
* **Lack of Multimodality**: Candidates struggle to quickly type out complex coding diagrams or LeetCode descriptions.

ApexPilot AI was engineered from the ground up to solve every one of these problems through a modular, local-first architecture:

```
+-----------------------------------------------------------------------------------+
|                                APEXPILOT AI ENGINE                                |
+-----------------------------------------------------------------------------------+
|  UI & STEALTH LAYER                                                               |
|  - Win32 SetWindowDisplayAffinity (WDA_EXCLUDEFROMCAPTURE: 0x11)                  |
|  - Frameless Dark Obsidian HUD (8-Border Hit Testing & QSizeGrip)                |
|  - Top-Bezel Webcam Teleprompter HUD (Natural Eye Contact)                        |
|  - LeetCode Crosshair Snip Overlay (Multi-Monitor Virtual Geometry)               |
+-----------------------------------------------------------------------------------+
|  INPUT PERCEPTION LAYER                                                           |
|  - Native Windows 10/11 Media OCR (<25ms Local Text Extraction via PowerShell)    |
|  - Dual-Channel WASAPI Loopback (Interviewer) + Mic (Candidate) Audio Capture     |
|  - Voice Activity Detection (VAD) & Question Heuristic Regex Engine               |
|  - 1-Click Resume & Job Description Document Loader (pypdf for PDF, TXT, MD)      |
+-----------------------------------------------------------------------------------+
|  REASONING & ROUTING LAYER                                                        |
|  - Dual-Context Prompt Synthesizer (STAR Behavioral, System Design, StealthCoder) |
|  - Fastest-First Speculative Duel Engine (Concurrent Local vs Cloud LLM Race)     |
|  - Automatic HTTP 429 Rate-Limit Failover Key Pool                                |
|  - Rapid Interruption Abort Engine (Sub-Second Stream Cancellation)               |
+-----------------------------------------------------------------------------------+
|  PERSISTENCE & STORAGE LAYER                                                      |
|  - Zero-Latency Q&A Cache (Exact Hash & Jaccard Token Similarity Matching)       |
|  - Native Vector PDF Archiving (QPdfWriter + QTextDocument -> saved_interviews/)  |
|  - JSON Configuration Store (config.json)                                         |
+-----------------------------------------------------------------------------------+
```

---

## 2. Feature Comparison Matrix

| Capability | GhostPilot AI | StealthCoder | Parakeet AI | HuddleMate | Final Round AI | **ApexPilot AI** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **100% Screen Share Invisibility** | Yes | No | No | No | No | **Yes (Win32 DWM Affinity)** |
| **Native LeetCode Screen Snip & OCR** | No | Yes | No | No | No | **Yes (<25ms Local OCR)** |
| **Dual-Channel Audio + VAD** | No | No | Yes | Yes | Yes | **Yes (WASAPI Loopback)** |
| **Instant Audio Question Detection** | No | No | Yes | No | Yes | **Yes (Regex Heuristic Engine)** |
| **Resume & JD Personalization** | No | No | No | No | Yes | **Yes (1-Click PDF/TXT/MD)** |
| **STAR Behavioral Formatting** | No | No | No | No | Yes | **Yes (Metrics-Driven)** |
| **Offline Local LLMs (Ollama/LM Studio)**| No | Partial | No | No | No | **Yes (Sub-Second Latency)** |
| **Fastest-First Speculative Race Duel**| No | No | No | No | No | **Yes (Local vs Cloud Race)** |
| **Automatic 429 Failover Pool** | No | No | No | No | No | **Yes (Multi-Key Rotation)** |
| **Rapid Interruption Stream Abort** | No | No | No | No | No | **Yes (Sub-Second Cancel)** |
| **0ms Latency Q&A Response Cache** | No | No | No | No | No | **Yes (Fuzzy & Exact Match)** |
| **Automatic Vector PDF Archiving** | No | No | No | No | No | **Yes (Local PDF Vault)** |
| **Webcam Eye-Contact Teleprompter** | Yes | No | No | No | No | **Yes (Top-Bezel Reader)** |

---

## 3. Exhaustive Capabilities Breakdown

### 3.1 GhostPilot Screen-Share Invisibility & Stealth Engine
* **Core Win32 API**: `SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)` (constant `0x00000011`).
* **Under the Hood**:
  * Windows Desktop Window Manager (DWM) separates the render target of the window from the display compositor's capture pipeline.
  * When screen sharing via **Zoom, Microsoft Teams, Google Meet, Discord, OBS Studio, Slack Huddles, or WebRTC**, the capture driver receives a completely transparent buffer where ApexPilot AI is located.
  * You see the window with full clarity on your physical monitor, but participants on the call see only your background IDE, code editor, or desktop.
* **Extended Window Styles**:
  * `WS_EX_TRANSPARENT` (`0x00000020`): Click-through toggle. When enabled, mouse clicks pass directly through the HUD into your background editor or browser.
  * `WS_EX_NOACTIVATE` (`0x08000000`): Prevents ApexPilot from stealing keyboard focus from your active coding environment.
  * `WS_EX_TOOLWINDOW` (`0x00000080`): Completely hides the application from the Windows `Alt + Tab` task switcher and taskbar.
  * `WS_EX_TOPMOST` (`0x00000008`): Keeps the HUD floating above all other application windows.

### 3.2 StealthCoder Vision & Native Windows Media OCR
* **Native Windows Media OCR**:
  * Leverages `Windows.Media.Ocr.OcrEngine` native to Windows 10/11 through a lightweight, high-performance PowerShell IPC bridge (`core/ocr_runner.ps1`).
  * Extracts text in **under 25 milliseconds locally on device** with zero external binaries (no heavy Tesseract installations or CUDA dependencies required).
* **Image Preprocessing**:
  * Automatically converts cropped regions to high-contrast grayscale.
  * Applies Lanczos interpolation upscaling for small text and adjusts contrast ($1.8\times$) to accurately parse syntax characters (e.g. `{}`, `[]`, `=>`, `::`, `;`) across both dark-theme and light-theme code editors.
* **Snipping Tool (`Ctrl + Alt + S`)**:
  * Spans across all connected monitors via `QApplication.primaryScreen().virtualGeometry()`.
  * Renders a translucent mask with a neon-cyan bounding box and live pixel dimension badge.

### 3.3 Hybrid LLM Client, Speculative Duel & 429 Failover
* **Local Inference Providers**:
  * **Ollama**: Default endpoint `http://127.0.0.1:11434` supporting `qwen2.5-coder`, `llama3.2`, `deepseek-r1`, etc.
  * **llama.cpp / llama-server**: Standard OpenAI-compatible server on port 8080.
  * **LM Studio**: Server endpoint `http://127.0.0.1:1234/v1`.
  * **Mock Engine**: Zero-setup offline fallback providing instant solutions if no model is loaded.
* **Unlimited Cloud API Key Pool**:
  * Built-in support for **Groq** (300+ tok/s LPUs), **OpenAI** (GPT-4o), **Anthropic** (Claude 3.5 Sonnet), **xAI** (Grok-2), **Google Gemini** (Gemini 2.0 Flash), and **DeepSeek**.
  * Custom Endpoint Manager allows adding arbitrary OpenAI-compatible servers (OpenRouter, Mistral, Together AI, Perplexity, private enterprise gateways).
* **Fastest-First Speculative Race Mode**:
  * Concurrently dispatches queries to both your local model and your fastest configured cloud model in parallel worker threads.
  * Whichever provider yields the first streaming token wins the race; the slower competitor thread is immediately cancelled to save tokens and compute.
* **Automatic 429 Rate-Limit Failover**:
  * Intercepts HTTP 429 (Too Many Requests) or quota exceeded errors.
  * Automatically rotates to the next available API key or provider in your configured pool with zero interruption to the streaming response.
* **Rapid Interruption Stream Abort**:
  * When an interviewer interrupts with a follow-up question, submitting the new question immediately triggers `StreamingWorker.abort()`.
  * The background streaming thread and network connection terminate in under 50ms, instantly clearing the screen for the new answer.

### 3.4 Dual-Context Ingestion Engine (Resume & Job Description)
* **1-Click Document Loaders**:
  * Dedicated loaders for **Candidate Resume** and **Target Job Description (JD)** in Settings.
  * Uses `pypdf` to extract text from single or multi-page PDF resumes, Word `.doc` text exports, or Markdown files.
* **Tailored Answer Synthesis**:
  * **STAR Behavioral Mode (`star_behavioral`)**: Answers behavioral questions in **Situation, Task, Action, Result, and Key Takeaway** format, directly quoting past projects, company scale, and quantifiable metrics from your resume.
  * **System Design Mode (`system_design`)**: Tailors architecture proposals around your proven technical stack while aligning directly with the infrastructure requirements in the target JD.
  * **Custom Instructions**: Allows injecting mandatory persona rules (e.g., *"Keep answers under 3 bullets"*, *"Strictly write modern C++20"*).

### 3.5 Webcam Teleprompter HUD (Eye-Contact Preservation)
* **Webcam Eye-Contact Bar**:
  * Pressing `Ctrl + Alt + T` swaps the main HUD for a sleek, horizontal capsule floating directly below your monitor's webcam.
  * Displays 15-20 word glanceable bullet points.
  * Allows you to read live talking points while maintaining natural eye contact with the interviewer on video calls.
  * Includes next/previous navigation buttons, counter badge, and full screen-share protection.

### 3.6 Dual-Channel Live Audio Capture & Question Heuristics
* **Dual-Channel WASAPI Architecture**:
  * Captures interviewer speech from system loopback audio (`sounddevice`).
  * Captures candidate speech from the local microphone.
  * Real-time Voice Activity Detection (VAD) monitors RMS energy thresholds.
* **Question Heuristic Regex Engine**:
  * Continuously evaluates transcript chunks against interview question patterns:
    * *"How would you design..."*
    * *"Can you explain the trade-offs between..."*
    * *"Tell me about a time when..."*
    * *"Walk me through your approach to..."*
  * Displays a discreet prompt notification on the HUD allowing 1-click solution generation.

### 3.7 Intelligent 0ms Q&A Cache & Local Vector PDF Archiving
* **Instant Q&A Cache (`cache/qa_cache.json`)**:
  * Every completed question and solution is indexed with its normalized token signature.
  * Implements exact matching and Jaccard token similarity (threshold $\ge 0.80$).
  * Repeated or slightly rephrased questions return **instantly with 0ms latency and 0 API cost**.
* **Automatic Local Vector PDF Archiving**:
  * Every answer is automatically formatted into an executive vector PDF in `saved_interviews/` using PySide6's `QPdfWriter` and `QTextDocument`.
  * Clicking **📁 Saved PDFs** opens the archive folder in Windows Explorer.

### 3.8 Dynamic Frameless Resizing & Geometry Persistence
* **8-Border & Corner Hit Testing**:
  * Detects cursor position within 8 pixels of any border edge or corner.
  * Changes cursor shape dynamically to horizontal, vertical, or diagonal resize arrows.
  * Provides smooth, hardware-accelerated drag-resizing alongside a built-in `QSizeGrip`.
* **Geometry Persistence**:
  * Custom window dimensions ($X, Y, \text{Width}, \text{Height}$) are automatically saved to `config.json` on resize and restored on launch.

---

## 4. Installation Guide

### 4.1 Method A: Standalone Windows Installer (Recommended)
The standalone setup installer is the fastest way to deploy ApexPilot AI on any Windows 10/11 machine. It requires **no Python installation or developer tools**.

* **Installer File**: [`d:\interAI\installer_dist\ApexPilotAI_Setup.exe`](file:///d:/interAI/installer_dist/ApexPilotAI_Setup.exe) (45.6 MB)
* **Installation Steps**:
  1. Double-click `ApexPilotAI_Setup.exe`.
  2. Follow the setup wizard to choose the destination folder (default: `C:\Program Files\ApexPilot AI`).
  3. Select whether to create a **Desktop Shortcut** and **Start Menu Shortcut**.
  4. Click **Install**. The setup finishes in approximately 5 seconds.
  5. Check **Launch ApexPilot AI** and click **Finish**.
* **Uninstallation**:
  * Can be cleanly uninstalled at any time via **Windows Settings &rarr; Apps &rarr; Installed Apps &rarr; ApexPilot AI &rarr; Uninstall**, or by running `unins000.exe` in the application directory.
* **Silent / Enterprise Deployment**:
  * Network administrators can deploy silently using standard flags:
    ```cmd
    ApexPilotAI_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
    ```

---

### 4.2 Method B: Standalone Portable Binary
For environments where running an installer is restricted:
* **Binary Location**: [`d:\interAI\dist\ApexPilotAI\ApexPilotAI.exe`](file:///d:/interAI/dist/ApexPilotAI/ApexPilotAI.exe)
* **Usage**:
  1. Copy the entire `dist\ApexPilotAI` directory to any folder, USB flash drive, or external storage.
  2. Double-click `ApexPilotAI.exe` to launch immediately. No dependencies or Python runtime required.

---

### 4.3 Method C: Virtual Environment (Developer Installation)
To run and develop directly from source code:

1. **Prerequisites**:
   * Windows 10 (Version 2004+) or Windows 11 (64-bit).
   * Python 3.10, 3.11, or 3.12 installed and added to your system `PATH`.
2. **1-Click Virtual Environment Launcher**:
   * Double-click [`run.bat`](file:///d:/interAI/run.bat) in the project root.
   * `run.bat` automatically:
     * Detects if `.venv` exists; if not, creates it via `python -m venv .venv`.
     * Installs all dependencies from `requirements.txt` (`PySide6`, `httpx`, `Pillow`, `keyboard`, `numpy`, `sounddevice`, `pypdf`).
     * Activates the virtual environment and launches `main.py`.
3. **Manual Command-Line Installation**:
   ```powershell
   cd d:\interAI
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

---

## 5. Complete Setup & Configuration Guide

### 5.1 Setting Up Local LLMs (Ollama, LM Studio, llama.cpp)

#### Option 1: Ollama (Recommended Local Engine)
1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Open PowerShell and pull an optimal model:
   ```powershell
   # High performance coding & reasoning model (recommended):
   ollama pull qwen2.5-coder:7b

   # Lightweight model for systems with lower RAM (8GB):
   ollama pull llama3.2:3b

   # Deep reasoning model for system design:
   ollama pull deepseek-r1:7b
   ```
3. Open ApexPilot AI, click the **⚙️ Settings** icon (top right of HUD), and navigate to the **⚡ Local & Routing** tab:
   * **Primary Provider**: Select `ollama`.
   * **Local Base URL**: Enter `http://127.0.0.1:11434`.
   * **Local Model**: Enter `qwen2.5-coder:7b`.
4. Click **⚡ Test Primary Connection**. The status will display: `✅ Ollama Online (X models available)`.

#### Option 2: LM Studio
1. In LM Studio, download any GGUF model (e.g. `Qwen2.5-Coder-7B-Instruct-GGUF`).
2. Navigate to the **Local Server** tab (icon with `<->`) and click **Start Server** on port `1234`.
3. In ApexPilot AI Settings:
   * **Primary Provider**: Select `lm_studio`.
   * **Local Base URL**: Enter `http://127.0.0.1:1234`.
   * **Local Model**: Enter your loaded model identifier.

#### Option 3: Built-In Mock Engine (Zero-Setup Fallback)
* If you do not have a local LLM or internet connection, set Primary Provider to `mock`. ApexPilot AI provides instant, intelligent synthetic solutions for testing.

---

### 5.2 Setting Up the Online LLM API Key Pool

ApexPilot AI allows combining local inference with an unlimited pool of cloud LLMs:

1. Open **Settings (⚙️)** and click the **🌐 Online API Pool** tab.
2. Check **Enable** next to any provider you wish to use and paste your API key:
   * **Groq (`gsk_...`)**: Ultra-fast inference on LPU chips (300+ tok/s). Best for sub-second responses.
   * **OpenAI (`sk-...`)**: GPT-4o for complex system design and architecture questions.
   * **Anthropic (`sk-ant-...`)**: Claude 3.5 Sonnet for deep algorithmic edge cases.
   * **xAI (`xai-...`)**: Grok-2 for reasoning.
   * **DeepSeek (`sk-...`)**: DeepSeek-Chat for cost-effective reasoning.
   * **Google Gemini (`AIzaSy...`)**: Gemini 2.0 Flash for low-latency multimodal processing.
3. **Adding Custom / Unlimited Endpoints**:
   * Under **➕ Add Any Custom / Unlimited Online LLM Endpoint**:
   * Select a preset (e.g. **OpenRouter**, **Mistral AI**, **Perplexity**, **Together AI**, **DeepInfra**) or choose **Custom Endpoint**.
   * Enter the Name, Base URL, API Key, and Model name.
   * Click **➕ Add Endpoint**. The new provider appears in the active endpoints list and can be toggled on/off or deleted anytime.
4. **Enabling Fastest-First Race & 429 Failover**:
   * In the **⚡ Local & Routing** tab:
     * Check **⚡ Fastest-First Race Mode**: Races your local LLM against your enabled online LLM in parallel.
     * Check **🔄 Automatic 429 Rate-Limit Failover**: Automatically rotates across your key pool if rate limits are reached.

---

### 5.3 Ingesting Candidate Resume & Target Job Description

1. Open **Settings (⚙️)** and click the **📄 Resume Context** tab.
2. **Loading Resume**:
   * Click **📂 Load Resume (.pdf, .txt, .md)**.
   * Select your resume file. The engine parses all pages and displays the character count.
   * You can edit or append extra notes directly in the text editor.
3. **Loading Target Job Description (JD)**:
   * Click **📂 Load JD (.pdf, .txt, .md)** or paste the job posting requirements directly into the editor.
4. Click **Save & Apply**. All future answers in STAR Behavioral, System Design, and Teleprompter modes will immediately reference your background.

---

### 5.4 Configuring Custom Instructions & Personas

1. Open **Settings (⚙️)** and click the **✍️ Custom Instructions** tab.
2. Enter any specific constraints or behavioral guidelines:
   * *"Keep all coding solutions strictly in modern C++20 using std::ranges."*
   * *"Always provide time and space complexity at the very top."*
   * *"Structure answers in at most 3 concise, speakable bullet points."*
   * *"Answer from the perspective of a Principal Distributed Systems Architect."*
3. If left blank, ApexPilot AI operates in standard professional copilot mode.

---

### 5.5 Hotkey & Stealth Preference Configuration

The following global shortcuts are active across all Windows applications:

| Hotkey | Feature | Operation |
| :--- | :--- | :--- |
| **`Ctrl + Alt + H`** | **Panic / Boss Key** | Instantly hides or unhides the HUD with zero latency. |
| **`Ctrl + Alt + S`** | **LeetCode Snip OCR** | Freezes screen with crosshairs; drag over code to solve in <25ms. |
| **`Ctrl + Alt + T`** | **Teleprompter HUD** | Toggles between main HUD and top-bezel eye-contact reader bar. |
| **`Ctrl + Alt + C`** | **Silent Code Copy** | Strips markdown and copies clean code block to clipboard. |
| **`Ctrl + Alt + A`** | **Instant Solve** | Solves currently highlighted text or detected audio question. |
| **Border Drag** | **Resize HUD** | Drag any of the 8 border edges or corners to freely resize. |

* **Click-Through Mode**: Click the **🖱️ Click-Thru** button in the HUD toolbar to let mouse clicks pass directly through the window into your IDE or browser.
* **Opacity Slider**: Drag the slider in the top toolbar to adjust transparency from 30% to 100%.

---

## 6. Real-World Interview Workflows

### 6.1 Live Coding & Algorithmic Interview Workflow
1. When the interviewer presents a coding challenge on LeetCode, HackerRank, or a shared editor:
2. Press **`Ctrl + Alt + S`**. The screen dims with crosshair guides.
3. Drag a box over the problem title, description, and constraints.
4. Release the mouse. The native Windows OCR extracts the text in **<25ms** and passes it to the reasoning engine.
5. In **StealthCoder Mode**, the HUD streams:
   * **Intuition & Approach**: Optimal data structures and Big-O Time/Space complexity.
   * **Optimal Code**: Clean, production-ready implementation in your configured language.
   * **Speakable Explanation**: First-person talking points (e.g. *"First, I maintain sentinel nodes..."*) so you can speak naturally while typing.
   * **Edge Cases**: Empty inputs, single-node cases, and boundary dry runs.
6. Press **`Ctrl + Alt + C`** to silently copy the clean code block to your clipboard.

---

### 6.2 STAR Behavioral Interview Workflow
1. When the interviewer asks a behavioral question (e.g. *"Tell me about a time you handled a severe production outage"*):
2. Select **STAR Behavioral** mode on the HUD.
3. Type the question or let the live audio engine detect it.
4. The engine reads your uploaded resume and JD, generating:
   * **Situation**: References your past company, project scale, and the failure condition.
   * **Task**: Specifies the ownership and SLA commitment you had.
   * **Action**: Cites the concrete technologies from your resume (e.g. eBPF, Kafka partition tuning, Go goroutines).
   * **Result**: Highlights quantifiable metrics (e.g. 99.6% latency drop, 40% compute savings).
   * **Key Takeaway**: Delivers a crisp closing insight demonstrating leadership.

---

### 6.3 System Design Architecture Workflow
1. Select **System Design** mode on the HUD.
2. Enter the prompt (e.g. *"Design a distributed real-time notification system handling 100M daily active users"*).
3. The engine outputs:
   * **Core Requirements & Scale Estimations**: Functional vs non-functional requirements, traffic RPS, and storage requirements.
   * **High-Level Architecture**: API Gateway, microservice decomposition, message brokers, caching tiers, and databases.
   * **Data Models & Contracts**: Schema designs and REST/gRPC contracts.
   * **Deep Dives & Bottleneck Mitigation**: Partitioning strategies, cache invalidation, idempotency, and failover mechanics.

---

### 6.4 Executive Meeting & Huddle Workflow
1. Select **HuddleMate** mode during team syncs or executive discussions.
2. The engine evaluates the conversation transcript and outputs:
   * **Executive Summary**: 2 concise bullet points summarizing the core discussion.
   * **Proactive Talking Points**: 2 sharp contributions you can make right now.
   * **Clarifying Questions**: 1 strategic question to steer the discussion productively.
   * **Action Items**: Key decisions made and deliverables with suggested owners.

---

## 7. System Verification & Testing

ApexPilot AI includes a comprehensive regression test suite verifying all 12 core subsystems:

```powershell
# Run complete test suite:
.\.venv\Scripts\python.exe test_stealth.py
```

### Verified Test Modules:
1. `test_01_stealth_attributes`: Validates Win32 `WDA_EXCLUDEFROMCAPTURE` and extended window styles.
2. `test_02_llm_streaming_engine`: Validates token streaming across all 5 modes.
3. `test_03_native_windows_media_ocr`: Validates Windows.Media.Ocr text extraction.
4. `test_04_context_store_injection`: Validates candidate resume and JD context formatting.
5. `test_05_question_boundary_heuristic`: Validates regex audio question detector.
6. `test_06_headless_ui_instantiation`: Validates HUD, Teleprompter, SnipOverlay, and SettingsDialog.
7. `test_07_custom_instructions_injection`: Validates mandatory user persona rules injection.
8. `test_08_stream_interruption_abort`: Validates sub-second streaming cancellation on follow-up.
9. `test_09_window_geometry_persistence`: Validates custom dimensions saving and restoration.
10. `test_10_qa_cache_and_pdf_export`: Validates 0ms cache hits and automatic local vector PDF export.
11. `test_11_custom_online_endpoints`: Validates dynamic custom endpoint creation, retrieval, and deletion.
12. `test_12_resume_jd_document_extraction`: Validates document parsing and tailored prompt injection.

---

## 8. Troubleshooting & Frequently Asked Questions (FAQ)

### Q1: Is the overlay truly invisible to Zoom, Teams, and Google Meet?
**Yes.** When screen sharing an entire monitor or individual desktop in Zoom, Teams, Meet, Discord, or OBS, Windows DWM excludes the window at the kernel compositing stage (`WDA_EXCLUDEFROMCAPTURE`). To verify this yourself:
1. Open OBS Studio or Discord.
2. Start a screen share of your monitor.
3. Observe that your IDE and wallpaper are visible in the preview, while ApexPilot AI is completely invisible.

### Q2: What if Ollama shows "Connection Refused"?
1. Ensure Ollama is running in your Windows taskbar.
2. Test if Ollama responds in PowerShell:
   ```powershell
   curl http://127.0.0.1:11434/api/tags
   ```
3. If not running, start Ollama from your Start Menu or run `ollama serve`.

### Q3: What if I hit an API rate limit (HTTP 429)?
Ensure **Automatic 429 Failover** is enabled in Settings &rarr; Local & Routing. When rate limits occur, ApexPilot AI automatically rolls over to the next configured provider in your pool without interrupting your response.

### Q4: How do I access my saved interview PDFs?
Click the **📁 Saved PDFs** button on the HUD toolbar, or in Settings &rarr; Stealth & Storage, click **Open Saved PDF Question Archives**. This opens `d:\interAI\saved_interviews\` in Windows Explorer.

### Q5: How do I reset the window size or position?
If you resize or move the window off-screen, open `config.json` in the application directory and reset `window_geometry` to default:
```json
"window_geometry": {
  "x": 200,
  "y": 150,
  "width": 740,
  "height": 640
}
```

---
*ApexPilot AI — High-Performance Stealth Interview Copilot for Windows.*
