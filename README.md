# 🦅 ApexPilot

> **The Ultimate Ultra-Low-Latency Stealth Interview & Meeting Copilot for Windows**  
> Uniting the most powerful features of **GhostPilot AI**, **StealthCoder**, **Parakeet AI**, **HuddleMate**, and **Final Round AI** into a single, high-performance local AI engine.

---

## 🌟 Feature Breakdown vs Competing Apps

| Feature | Inspired By | ApexPilot Superpower |
| :--- | :--- | :--- |
| **Screen-share Protection** | **GhostPilot AI** | Uses `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` when Windows accepts it. The application verifies the result and reports when the OS or capture method cannot support exclusion. |
| **Discreet Teleprompter HUD** | **GhostPilot AI** | Sleek floating HUD placed directly beneath the webcam so you maintain eye contact with interviewers while reading talking points. |
| **Instant Screen Snip & OCR** | **StealthCoder** | Press `Ctrl + Alt + S` to draw a box over any LeetCode / HackerRank problem. Native Windows Media OCR extracts problem text in <25ms. |
| **Algorithmic Code Solver** | **StealthCoder** | Generates optimal solution, Big-O Time & Space complexity, speakable line-by-line explanation, and edge case dry runs. |
| **Live Dual-Channel Audio & VAD** | **Parakeet AI** | Captures system-output and microphone audio concurrently with real-time Voice Activity Detection. Uses WASAPI speaker loopback when available, then Stereo Mix. Candidate speech is transcribed and displayed, while only interviewer/system speech can trigger an answer. |
| **Instant Question Detection** | **Parakeet AI** | NLP heuristic engine detects questions ("How would you scale...", "Can you explain...") and triggers 1-click or automated answers. |
| **Executive Meeting Intelligence** | **HuddleMate** | Live meeting summary, agenda tracking, action items extractor, and strategic talking point suggestions. |
| **Resume & Experience Personalization** | **Final Round AI** | Ingests candidate's real resume and target Job Description (JD) so all answers reference your authentic past projects, metrics, and tech stack. |
| **STAR Method Behavioral Coach** | **Final Round AI** | Automatically formats behavioral responses into Situation, Task, Action, and Result bullets. |
| **Local LLM Streaming (Sub-Second Latency)**| **Local-First Core** | Direct streaming connector for **Ollama**, **llama.cpp**, **LM Studio**, and **vLLM** + built-in zero-setup smart mock engine. |

---

## ⌨️ Global Hotkeys (Work System-Wide)

| Shortcut | Action | Description |
| :--- | :--- | :--- |
| **`Ctrl + Alt + H`** | **Panic / Boss Key** | Instantly hides or unhides the overlay HUD. |
| **`Ctrl + Alt + S`** | **LeetCode Snip Tool** | Freezes screen with crosshairs to drag-select coding problems for instant OCR. |
| **`Ctrl + Alt + T`** | **Webcam Teleprompter** | Toggles ultra-compact top-bezel teleprompter mode. |
| **`Ctrl + Alt + C`** | **Silent Code Copy** | Strips comments/markdown and copies clean solution directly to clipboard. |

The red `✕` button exits ApexPilot AI completely, including its global hotkey
listener and audio capture service. Use `Ctrl + Alt + H` when you only want to
hide or show the HUD.

---

## 📦 Installation & Executables

### 1. Windows Setup Installer (Recommended)
You can install ApexPilot AI directly using the generated Windows Setup wizard:
- **Installer Path**: [`\\installer_dist\ApexPilotAI_Setup.exe`](//installer_dist/ApexPilotAI_Setup.exe) (45.5 MB)
- Features:
  - Guided installation wizard
  - Creates **Desktop Shortcut**
  - Creates **Start Menu** entry
  - Registers Windows **Uninstaller** in Control Panel / Apps & Features
  - Single-file zero-dependency installation (no Python or virtual environment needed!)

### 2. Standalone Portable Executable
- Simply run `ApexPilotAI.exe` directly from the `dist\ApexPilotAI` folder.

### 3. Developer Mode (Virtual Environment)
Run directly from source with live reloading:
```powershell
d:\interAI\run.bat
```

---

## 🧠 Connecting to Local LLMs

ApexPilot AI works out-of-the-box with a built-in offline engine, but is built to harness local models for private, zero-latency inference:

### Option A: Ollama (Recommended)
1. Install Ollama and pull your favorite coding or reasoning model:
   ```powershell
   ollama run qwen2.5-coder:7b
   # or
   ollama run qwen2.5:3b
   # or
   ollama run llama3.2:3b
   # or
   ollama run deepseek-r1:7b
   ```
2. In ApexPilot AI, click the **⚙️ Settings** icon:
   - **Provider**: `ollama`
   - **Base URL**: `http://127.0.0.1:11434`
   - **Model**: `qwen2.5-coder:7b`
   - Click **⚡ Test Local LLM Connection**.

`qwen2.5:3b` is the recommended free fallback for machines with limited
memory. `llama3.2:3b` and `phi3:mini` are also good lightweight choices.
If the configured Ollama model is unavailable, ApexPilot automatically selects
one of these installed local models.

### Meeting audio troubleshooting

Install the optional WASAPI loopback backend so interviewer audio can be
captured even when Windows does not expose a loopback device through
PortAudio:

```powershell
.\.venv\Scripts\pip.exe install SoundCard
```

At startup, verify the log contains both `Microphone capture started` and
`WASAPI loopback` (or `Stereo Mix`). If interviewer RMS remains near zero,
select the meeting playback device as the Windows default output and confirm
the meeting application is actually playing audio through that device.

### Accent and recognition fallback

Recognition tries `en-US`, `en-IN`, and `en-GB` by default. If Google
recognition cannot understand the accent or is unavailable, ApexPilot uses a
local Whisper `small.en` model, then PocketSphinx as a final lightweight
fallback. The first Whisper use downloads its model and may take longer; later
segments stay local and do not require Google.

### Option B: llama.cpp / llama-server
```powershell
llama-server.exe -m your_model.gguf --port 8080 -ngl 99
```
- In ApexPilot Settings: Provider `llama_cpp`, Base URL `http://127.0.0.1:8080`.

### Option C: LM Studio / vLLM / LocalAI
- Enable local server at `http://127.0.0.1:1234/v1`.
- In ApexPilot Settings: Provider `lm_studio`, Base URL `http://127.0.0.1:1234`.

---

---

## ⚡ Intelligent Q&A Cache & Local PDF Archiving

ApexPilot AI automatically archives your interview interactions:
1. **0ms Latency QA Cache**:
   - Every question and solution is stored in local persistent storage.
   - When faced with the same (or rephrased) question, ApexPilot performs **exact and fuzzy token matching** to pull up the answer **instantly with 0ms latency and zero API cost**.
   - A distinct badge informs you: `⚡ [INSTANT CACHE HIT — 0ms Latency | Saved Local PDF]`.
2. **Automatic Vector PDF Export**:
   - Each interview answer is automatically rendered and saved as a high-quality PDF in `d:\interAI\saved_interviews\`.
   - Click the **📁 Saved PDFs** button in the HUD toolbar or Settings to open the directory directly in Windows Explorer.

---

## 🌐 Unlimited Online LLM Endpoints & Rate-Limit Failover

Do not limit yourself to standard APIs. ApexPilot AI supports:
- **Built-in Presets**: OpenAI (ChatGPT), xAI (Grok), Groq (300+ tok/s), Anthropic (Claude), DeepSeek, Google Gemini.
- **Custom / Unlimited Endpoints**: In Settings, add any OpenAI-compatible endpoint with custom URL, API key, and model (e.g. **OpenRouter**, **Mistral AI**, **Perplexity**, **Together AI**, **DeepInfra**, or private enterprise/LAN vLLM servers).
- **Automatic 429 Rate-Limit Failover**: When any provider hits rate limits or quota errors, the engine seamlessly rotates to the next available provider in your pool without interrupting your response.
- **Fastest-First Race Mode ("Speculative Duel")**: Competitively races Local LLM vs Online LLM in parallel; the fastest responder streams to your screen while the slower is aborted.

---

## 🛡️ How Screen Share Invisibility Works

ApexPilot AI calls the Windows Desktop Window Manager (DWM) kernel API:
```python
SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE) # 0x00000011
```
Introduced in Windows 10 (version 2004+) and Windows 11:
- The window is rendered by the GPU directly to your physical display output.
- Any capture layer (Windows Graphics Capture, DirectX Desktop Duplication API, GDI BitBlt, Zoom, Microsoft Teams, Google Meet, Discord, OBS, WebRTC) receives a transparent render buffer excluding ApexPilot completely.
- You can code, browse, and use supported screen-share protection with confidence.

---

## 🧪 Running the Verification Test Suite

To verify all system subsystems, display affinity hooks, OCR engines, cache, PDF export, and LLM streaming:
```powershell
.\.venv\Scripts\python.exe test_stealth.py
```
The verification suite currently contains 23 tests covering:
- Win32 Stealth Layer (`WDA_EXCLUDEFROMCAPTURE`)
- Real-time LLM Streaming Generator across 5 modes
- Windows.Media.Ocr Native Text Recognition
- Audio Question Detection Heuristics
- Context Store & Resume Injection
- Qt6 UI Headless Initialization
- Custom Instructions Injection (rules vs normal mode)
- Stream Interruption & Rapid Cancellation Abort
- Window Geometry & Resizing Persistence
- QA Cache Exact & Fuzzy Lookup + Vector PDF Generation
- Dynamic Custom Online LLM Endpoints Management
- Resume/JD document extraction and prompt personalization
- Click-through and opacity controls
- Screen OCR preprocessing and coding-problem extraction
- Persistent rotating application logs in `logs/apexpilot.log`

Screen-share protection is best-effort and OS-enforced. ApexPilot applies and
verifies Windows display-affinity protection to each overlay after its native
window styles are created. Windows may still reject the request, and capture
methods that do not honor display affinity cannot be controlled by ApexPilot.
