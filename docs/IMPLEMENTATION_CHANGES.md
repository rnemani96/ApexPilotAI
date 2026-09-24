# ApexPilot AI Implementation Changes

## Document purpose

This document records the code changes made while aligning ApexPilot AI with the
features and operating behavior described in `README.md`.

The changes focus on reliable question answering, provider routing, offline
behavior, configuration persistence, audio capture foundations, cache integrity,
and verification coverage. Existing unrelated worktree changes were not
reverted or included as part of this implementation.

## Executive summary

The application now:

- Sends real Bearer authentication tokens to OpenAI-compatible providers.
- Builds provider endpoints correctly when URLs already include `/v1` or a
  provider-specific API path.
- Falls back instead of silently returning an empty answer when speculative
  race mode receives an empty provider stream.
- Avoids presenting unrelated canned coding answers for arbitrary questions.
- Avoids storing outage notices and offline fallback messages as valid answers.
- Preserves missing nested defaults when loading partial configuration files.
- Starts microphone capture and attempts Windows WASAPI loopback capture when
  supported.
- Performs lightweight RMS-based voice activity detection.
- Provides a transcript submission API that triggers existing interviewer
  question detection.
- Uses atomic configuration writes so an interrupted save cannot leave a
  truncated `config.json`.
- Captures system output only by default for meeting questions, avoiding
  candidate microphone audio in the interviewer-question pipeline.
- Routes screen snips through Windows.Media.Ocr first and prevents an OCR
  failure placeholder from being submitted as a coding question.
- Writes console and rotating file logs to `logs/apexpilot.log`, including
  audio RMS levels, queued segments, transcription attempts, and recognizer
  results.
- Reapplies verified display-affinity protection after Qt native styles are
  finalized and checks that DWM composition is available before reporting
  protection as active.
- Uses a concise coding prompt that prioritizes simple, efficient, readable
  solutions.
- Ships with a sanitized local-first configuration: no API credentials are
  stored in the repository working tree, online providers are disabled until
  explicitly configured, and speculative racing is opt-in.
- Documents the actual 17-test verification suite in `README.md`.

## Final audit and reliability hardening

The final repository audit verified compilation, the complete regression suite,
audio-device selection, transcription dependency loading, UI behavior, and
configuration parsing. The test suite completed with **23 passing tests**.

`config.json` was also sanitized during the audit. Any provider credentials
must now be entered locally through the settings UI or an untracked
configuration file. This prevents accidental credential exposure while keeping
all provider integrations available when deliberately configured.

Configuration persistence now writes to a temporary file and replaces the
active file only after serialization succeeds. This protects user settings
from partial writes caused by process termination or disk errors.

## Files changed

### `core/llm_client.py`

#### Bearer authentication

Online OpenAI-compatible requests now use:

```python
headers["Authorization"] = f"Bearer {api_key}"
```

Previously, the request used a masked placeholder instead of the configured
key. That caused otherwise valid online provider requests to be rejected as
unauthenticated.

#### Endpoint construction

Added `_chat_completions_endpoint()` to normalize OpenAI-compatible endpoint
URLs. It prevents malformed paths such as:

```text
/v1/v1/chat/completions
```

It supports:

- OpenAI-compatible URLs ending in `/v1`
- Custom paths such as `/v1/openai`
- OpenRouter and other custom endpoints
- Perplexity's endpoint layout
- Local servers such as llama.cpp and LM Studio

#### Speculative race reliability

Fastest-first race mode now tracks whether the winning provider actually
completed. If both candidates terminate without producing a usable completed
stream, the client invokes normal failover instead of ending with no answer.

#### Offline fallback correctness

The mock engine no longer returns a hard-coded Two Sum solution for every
coding question. The Two Sum sample is only used when the submitted question
actually contains “Two Sum”.

For other coding questions, the fallback:

- Preserves the submitted question.
- Clearly identifies that configured providers are unavailable.
- Does not claim to have generated an exact solution.

Mode-specific fallback output was also added for:

- STAR behavioral answers
- System design questions
- HuddleMate meeting exchanges
- Teleprompter talking points

## `core/context_store.py`

### Deep configuration merge

Configuration loading now recursively merges nested dictionaries with the
default configuration. A partial `config.json` no longer removes unrelated
default values from sections such as:

- `llm`
- `online_providers`
- `routing`
- `preferences`
- `profile`
- `hotkeys`

This makes upgrades and hand-edited configuration files safer.

### Endpoint ID generation

Endpoint ID creation now imports and uses `time` directly rather than importing
the module dynamically at the call site. The resulting behavior is unchanged,
but the implementation is clearer and easier to validate.

## `core/audio_capture.py`

### Microphone capture

The audio worker now attempts to open a `sounddevice.InputStream` for the
default microphone using the configured sample rate and chunk size.

### Windows WASAPI loopback

On Windows, the engine attempts a second input stream using
`sd.WasapiSettings(loopback=True)` and the default output device. This captures
system audio, which is intended for interviewer audio in the README workflow.

Loopback initialization is optional. If the device or host API does not
support it, microphone capture can continue and a warning is logged.

### Stream lifecycle

Audio streams are tracked and closed during `stop_capture()` so the process
does not leave active input devices behind.

### Voice activity detection

Audio callbacks now calculate RMS energy and update the last speech timestamp
when the configured threshold is exceeded. This is intentionally lightweight
and avoids blocking the sounddevice callback.

### Transcript adapter boundary

Added:

```python
audio_engine.submit_transcript(speaker, text)
```

This routes text from any speech-to-text adapter through the existing
`simulate_speech_input()` path. It triggers transcript storage and interviewer
question detection.

The engine now includes an optional SpeechRecognition transcription worker.
Completed speech segments are converted to PCM audio off the sounddevice
callback and sent to the recognizer. The resulting text is passed through
`submit_transcript()` and the existing question detector.

The current adapter uses SpeechRecognition's Google recognizer, so it requires
network access and sends audio to that service. A local recognizer such as
Vosk or Whisper can replace `_transcribe()` when offline/private transcription
is required.

## `core/qa_cache.py`

Cache lookup now ignores entries whose answer begins with an outage or offline
fallback marker. This prevents a temporary provider failure from becoming a
permanent “instant answer” for the same question.

## `ui/overlay_window.py`

Automatic Q&A archival now skips outage and offline fallback responses. Valid
answers continue to be:

- Stored in the local QA cache.
- Exported to the local PDF archive.
- Available through the Saved PDFs control.

This preserves retry behavior when a provider becomes available later.

## `README.md`

The verification section was corrected to the current suite count of 23 tests.
It now also lists:

- Resume/JD document extraction and prompt personalization.
- Click-through and opacity controls.

## Behavior by README feature

| README feature | Current implementation status |
|---|---|
| Local LLM streaming | Implemented for Ollama, llama.cpp-compatible, LM Studio-compatible, and mock routing |
| Online provider routing | Implemented for configured providers and custom OpenAI-compatible endpoints |
| Bearer API authentication | Fixed and implemented |
| Rate-limit/quota failover | Implemented for HTTP 429 and HTTP 402 responses |
| Fastest-first race mode | Implemented with empty-stream fallback protection |
| Question-specific offline behavior | Implemented without unrelated canned answers |
| QA cache and PDF archive | Implemented; failure notices are excluded |
| Resume/JD personalization | Implemented through prompt context injection |
| OCR screen snipping | Implemented through Windows OCR with pytesseract fallback |
| Global hotkeys | Implemented through the keyboard package |
| Screen-share display affinity | Implemented through the Win32 stealth layer |
| Microphone capture | Optional; disabled by default for automatic question detection |
| WASAPI loopback capture | Preferred system-output source when supported |
| Stereo Mix capture | Fallback system-output source with native-rate probing |
| Automatic speech transcription | Implemented through optional SpeechRecognition adapter; requires network access to its recognizer |

## Validation performed

The following checks passed after the changes:

### Python compilation

```powershell
.\.venv\Scripts\python.exe -m compileall -q main.py core ui
```

Result: passed.

### Automated verification suite

```powershell
.\.venv\Scripts\python.exe test_stealth.py
```

Result: all 23 tests passed.

The suite covers:

1. Win32 stealth constants and bindings.
2. LLM streaming across five modes.
3. OCR extraction.
4. Audio question heuristics.
5. Resume/profile persistence.
6. Qt UI initialization.
7. Custom prompt instructions.
8. Stream interruption.
9. Window geometry persistence.
10. QA cache and PDF generation.
11. Custom online endpoint management.
12. Resume/JD document extraction and prompt tailoring.
13. Click-through and opacity controls.

### Additional targeted checks

The following targeted checks also passed:

- Partial configuration files retain default nested settings.
- Transcript submission triggers interviewer question callbacks.
- OpenAI-compatible endpoint paths are generated correctly for custom URL
  layouts.
- Offline fallback output contains the submitted question instead of unrelated
  canned coding content.

## Configuration and operational notes

1. The default provider is Ollama at `http://127.0.0.1:11434`.
2. A real model must be installed and running for exact generated answers.
3. Online providers require a valid API key and model configuration in Settings.
4. API keys should be kept local and must not be committed to source control.
5. If all providers fail, the application now reports the outage and uses a
   clearly labeled contextual fallback rather than pretending it solved the
   question.
6. Audio devices, permissions, and WASAPI support vary by Windows machine.
   Dual-channel capture is enabled by default; candidate microphone speech is
   transcribed for display but cannot trigger interviewer answers.
7. Screen-share exclusion depends on Windows 10 version 2004 or newer and
   supported capture behavior.

## Known limitation

The README describes automatic live question detection from spoken audio.
SpeechRecognition with Google recognition and PocketSphinx local fallback is
included. Recognition quality still depends on the selected device, language,
and audio clarity; a local Whisper/Vosk adapter can improve difficult audio.
Interviewer/system transcripts are debounced and joined before triggering an
answer, while candidate transcripts remain display-only.

## Close behavior and packaging verification

### Close button

The red `X` button in the main HUD now performs a complete application exit
instead of only hiding the overlay. Before quitting, it:

1. Aborts an active LLM streaming worker.
2. Waits briefly for the worker to stop.
3. Closes the snipping and teleprompter overlays.
4. Calls `QApplication.quit()`.

The `Ctrl + Alt + H` panic shortcut remains a hide/show action and does not
terminate the application.

### Portable executable

The README-referenced portable build is located at:

```text
D:\interAI\dist\ApexPilotAI\ApexPilotAI.exe
```

The PyInstaller build was regenerated after the close-button and runtime
changes. The invalid `Pillow` hidden-import entry was removed from
`apexpilot.spec`; the application imports Pillow through its supported `PIL`
package namespace.

### Installer and uninstaller

`installer.iss` contains the expected installation surfaces:

- Copies the complete `dist\ApexPilotAI` directory.
- Creates a Start Menu shortcut.
- Optionally creates a Desktop shortcut.
- Creates an uninstall shortcut using `{uninstallexe}`.
- Uses Inno Setup's generated uninstaller registration for Windows installed
  apps.
- Launches ApexPilot AI after installation when the user accepts the option.

The existing artifacts were checked at:

```text
D:\interAI\installer_dist\ApexPilotAI_Setup.exe
D:\interAI\dist\ApexPilotAI\ApexPilotAI.exe
```

The Inno Setup compiler is not installed in the current environment, so the
portable executable was rebuilt successfully, but the installer executable
could not be regenerated here. To publish the latest source changes through
the installer, compile `installer.iss` on a machine with Inno Setup installed.

### Packaging checks performed

- Portable executable exists after the PyInstaller build.
- Installer executable exists at the README path.
- Installer source points to the portable distribution directory.
- Desktop shortcut entry is present.
- Start Menu shortcut entry is present.
- Uninstaller shortcut entry is present.
- Close-button shutdown was verified through the Qt event loop.

## Runtime log compatibility fixes

The following runtime messages were also addressed:

### Unsupported Qt stylesheet property

Qt Style Sheets do not implement the browser CSS `filter` property. The
unsupported hover rule was replaced with a Qt-compatible background-color rule,
removing:

```text
Unknown property filter
```

### WASAPI constructor compatibility

The installed `sounddevice`/PortAudio binding does not accept
`WasapiSettings(loopback=True)`. The audio engine now searches for a
PortAudio-exposed loopback input device and creates `WasapiSettings()` only
when such a device exists. If none exists, it logs an informational message
and continues microphone capture without treating the optional loopback path
as a startup failure.

### Display-affinity failure handling

`SetWindowDisplayAffinity` can be rejected by Windows depending on the window
type, DWM state, Windows version, or capture-policy support. The application
now applies stealth window styles before requesting display affinity, attempts
the documented fallback, and reports an unsupported display-affinity result as
a single warning rather than repeated error logs. The rest of the HUD remains
functional when the OS cannot provide capture exclusion.
