# ApexPilot AI Model Setup

This guide explains what to install, which models to download, how to configure
ApexPilot AI, and how to verify that the local interview pipeline is working.
The instructions target Windows PowerShell and the repository virtual
environment at `D:\interAI\.venv`.

## 1. Recommended architecture

ApexPilot uses separate models for separate jobs:

```text
Microphone / meeting audio
        |
        v
Speech recognition (Google regional recognition -> local Whisper -> PocketSphinx)
        |
        v
Question detection and interview-mode routing
        |
        v
Ollama text-generation model
        |
        v
Streaming answer in the teleprompter
```

Laya is not part of the answer-generation path. Laya is a typed-decision
classifier (`choice`, `score`, and `noul`), while ApexPilot needs a
text-generation model that can stream natural-language answers. Ollama models
are therefore the supported local answer models.

## 2. Install Ollama

1. Download and install Ollama from [ollama.com/download](https://ollama.com/download).
2. Start Ollama. The default local API must be available at:

   ```text
   http://127.0.0.1:11434
   ```

3. Confirm that the command is available:

   ```powershell
   ollama --version
   ollama list
   ```

If `ollama list` cannot connect, start the Ollama desktop application and
repeat the command. Do not configure ApexPilot until the Ollama API responds.

## 3. Download the recommended models

Run these commands in PowerShell:

```powershell
ollama pull qwen2.5:3b
ollama pull phi4-mini
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull qwen2.5-coder:7b
```

The models have different roles:

| Model | Role | Recommendation |
| --- | --- | --- |
| `qwen2.5:3b` | General interview answers | Primary model; fastest tested option |
| `phi4-mini` | Coding and reasoning answers | Preferred coding fallback |
| `gemma3:4b` | Behavioral and multilingual answers | Preferred behavioral/multilingual fallback |
| `llama3.2:3b` | General-purpose fallback | Reliable backup |
| `qwen2.5-coder:7b` | Detailed coding answers | Quality fallback; slower |

The downloads require several gigabytes of disk space. The models are stored
and managed by Ollama; they are not copied into this repository.

Verify that all models are installed:

```powershell
ollama list
```

The model names must match the names in the `NAME` column. A suffix such as
`:latest` is normal for models such as `phi4-mini`.

## 4. Optional model

`qwen3:4b` can be downloaded for manual testing:

```powershell
ollama pull qwen3:4b
```

It is not in ApexPilot's automatic fallback order because the current Ollama
output can expose internal reasoning text in the answer stream. That text is
not appropriate for a live teleprompter. Use it manually only after checking
the output yourself.

## 5. Install the ApexPilot Python dependencies

From the repository root:

```powershell
Set-Location D:\interAI
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The relevant local-audio and transcription packages are:

- `SoundCard`: Windows speaker/WASAPI loopback capture.
- `SpeechRecognition`: Google regional recognition interface.
- `pocketsphinx`: lightweight final speech-recognition fallback.
- `faster-whisper`: local accent/noise-resilient transcription fallback.

The first local Whisper transcription may download the configured Whisper
checkpoint. This is separate from the Ollama models and may take additional
time and disk space.

## 6. Configure ApexPilot in the application

Open ApexPilot settings and configure **Local & Routing**:

| Setting | Value |
| --- | --- |
| Provider | `ollama` |
| Base URL | `http://127.0.0.1:11434` |
| Model | `qwen2.5:3b` |
| Temperature | `0.2` |
| Maximum tokens | `1500` |
| Automatic failover | Enabled |

Then click **Test Primary Connection** or **Test Local LLM Connection**.
The connection test should report Ollama online and list the installed models.

The checked-in `config.json` already contains the intended local defaults:

```json
{
  "llm": {
    "provider": "ollama",
    "base_url": "http://127.0.0.1:11434",
    "model": "qwen2.5:3b",
    "temperature": 0.2,
    "max_tokens": 1500,
    "timeout_seconds": 15
  },
  "routing": {
    "auto_failover_on_rate_limit": true,
    "fastest_first_race": false,
    "ollama_fallback_models": [
      "qwen2.5:3b",
      "phi4-mini",
      "phi4-mini:latest",
      "gemma3:4b",
      "llama3.2:3b",
      "qwen2.5-coder:7b"
    ]
  }
}
```

The fallback list is ordered. When the configured primary model is missing,
ApexPilot selects the first installed model in that list. Keep
`qwen2.5:3b` first for low latency. Do not add API keys to this file.

## 7. Configure speech recognition and audio

The default speech settings are:

```json
{
  "preferences": {
    "system_audio_only": false,
    "speech_languages": ["en-US", "en-IN", "en-GB"],
    "whisper_model": "small.en"
  }
}
```

`system_audio_only: false` enables both candidate microphone capture and
interviewer/system-audio capture. Only interviewer/system-audio questions
automatically start answer generation.

For meeting audio, confirm that the startup log contains both:

```text
Microphone capture started
WASAPI loopback capture started
```

If the meeting application is not exposed through PortAudio, ApexPilot tries
the SoundCard WASAPI speaker loopback backend and then Stereo Mix. Play audio
through the selected Windows speakers while testing loopback capture.

For accented or noisy speech, ApexPilot tries the configured regional Google
recognizers, then local Whisper, then PocketSphinx. The first Whisper fallback
may be slower because its model is loaded lazily.

## 8. Verify each Ollama model directly

Before testing ApexPilot, verify that each downloaded model can answer:

```powershell
$prompt = 'Answer in under 80 words: What is the difference between a process and a thread?'
ollama run qwen2.5:3b $prompt
ollama run phi4-mini $prompt
ollama run gemma3:4b $prompt
ollama run llama3.2:3b $prompt
ollama run qwen2.5-coder:7b $prompt
```

If a model is slow, allow its first request to finish before judging it. Ollama
loads a model into memory on first use. Later requests are normally faster.

## 9. Run the ApexPilot verification suite

Run the project tests with the same Python interpreter used by the application:

```powershell
Set-Location D:\interAI
.\.venv\Scripts\python.exe -m unittest test_stealth
```

The expected result is currently:

```text
Ran 23 tests
OK
```

This suite validates model fallback selection, configuration defaults,
question routing, prompt generation, audio heuristics, and offline response
paths. It does not download or load every multi-gigabyte Ollama model.

## 10. Run the application and perform an end-to-end test

Start the application:

```powershell
.\run.bat
```

Then:

1. Open **Settings** and test the Ollama connection.
2. Confirm the selected model is `qwen2.5:3b`.
3. Ask a conceptual question using **Generate Answer**.
4. Ask a coding question and confirm the response contains suitable code.
5. Test a behavioral question and confirm STAR-style content.
6. Play interviewer audio and confirm that it appears in the transcript.
7. Confirm that candidate microphone speech does not automatically trigger an answer.
8. Watch `logs\apexpilot.log` for transcription, question detection, model
   selection, and answer-stream events.

## 11. Troubleshooting

### Ollama is not reachable

```powershell
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Start Ollama if either command fails. Keep the Base URL exactly
`http://127.0.0.1:11434` unless Ollama is intentionally configured on another
port.

### A model is missing

```powershell
ollama pull qwen2.5:3b
ollama pull phi4-mini
```

Then restart ApexPilot or run the connection test again. ApexPilot will use the
first available configured fallback if the selected model is not installed.

### Answers are too slow

Use `qwen2.5:3b` as the primary model. Avoid using
`qwen2.5-coder:7b` as the default on machines with limited memory. Close other
GPU/CPU-heavy applications and allow the model to remain loaded in Ollama.

### Answers contain reasoning or planning text

Use `qwen2.5:3b`, `phi4-mini`, or `gemma3:4b`. Do not place `qwen3:4b` in the
automatic fallback list unless its output has been verified with the installed
Ollama version.

### Interviewer audio is missing

Check Windows microphone and speaker permissions, confirm the correct output
device is selected, and verify that SoundCard is installed:

```powershell
.\.venv\Scripts\python.exe -c "import soundcard; print(soundcard.all_speakers())"
```

During a test, play actual meeting audio. A silent speaker produces a valid
loopback stream with no transcript.

### Accent recognition is poor

Confirm that `faster-whisper` is installed and leave
`"whisper_model": "small.en"` configured. The first fallback can take longer
while the model is downloaded. For non-English interviews, add the appropriate
regional recognition language to `speech_languages` and test the local Whisper
fallback.

## 12. Updating or removing models

List installed models:

```powershell
ollama list
```

Remove a model only when it is no longer needed:

```powershell
ollama rm qwen2.5-coder:7b
```

Removing a model that appears in the fallback list is safe; ApexPilot skips
missing models and uses the next installed model. Keep at least
`qwen2.5:3b` installed for the documented default behavior.

