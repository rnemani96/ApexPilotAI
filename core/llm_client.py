"""
ApexPilot AI - Ultra-Low-Latency Multi-Provider LLM Streaming Client
====================================================================
Features:
1. Local LLMs: Ollama, llama.cpp, LM Studio, Built-in Mock Engine.
2. Online LLMs: OpenAI (ChatGPT), xAI (Grok), Groq (300+ tok/s), Claude (Anthropic), DeepSeek, Gemini.
3. Automatic 429 Rate-Limit Failover: Automatically rotates to next API key/provider on 429 or quota errors.
4. Fastest-First Race Engine ("Speculative Duel"): Races Local LLM vs Online LLM in parallel; fastest token wins.
5. Instant Interruption / Abort: Cancels active streams instantly when a new question arrives.
"""

import json
import time
import threading
import queue
from typing import Generator, Optional
from urllib.parse import urlparse
import httpx
import logging
from core.context_store import context_store
from core.prompts import build_prompt

logger = logging.getLogger("ApexPilot.LLM")


class LocalLLMClient:
    """Multi-provider streaming client with rate-limit failover and speculative racing."""

    def __init__(self):
        self._http_client = None
        self._current_abort_event = threading.Event()
        self._abort_lock = threading.Lock()

    def get_client(self) -> httpx.Client:
        if self._http_client is None or self._http_client.is_closed:
            limits = httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=60.0)
            self._http_client = httpx.Client(limits=limits, timeout=httpx.Timeout(25.0, connect=3.5))
        return self._http_client

    @staticmethod
    def _chat_completions_endpoint(base_url: str) -> str:
        """Build an OpenAI-compatible endpoint without duplicating or omitting /v1."""
        base_url = base_url.rstrip("/")
        parsed = urlparse(base_url)
        path = parsed.path.rstrip("/")
        if path.endswith("/v1") or "/v1/" in f"{path}/" or parsed.hostname == "api.perplexity.ai":
            return f"{base_url}/chat/completions"
        return f"{base_url}/v1/chat/completions"

    def abort_active_streams(self):
        """Signals any currently running streaming requests to terminate immediately."""
        with self._abort_lock:
            self._current_abort_event.set()
            # Prepare new event for subsequent requests
            self._current_abort_event = threading.Event()

    def check_health(self) -> tuple[bool, str, list[str]]:
        """Checks if the configured primary LLM is reachable."""
        config = context_store.get_llm_config()
        provider = config.get("provider", "ollama")
        base_url = config.get("base_url", "http://127.0.0.1:11434").rstrip("/")

        if provider == "mock":
            return True, "Mock Local Engine (Zero-setup Offline Mode)", ["mock-instant-qwen-coder", "mock-star-coach"]

        client = self.get_client()

        try:
            if provider == "ollama":
                resp = client.get(f"{base_url}/api/tags", timeout=2.5)
                if resp.status_code == 200:
                    models = [m.get("name", "") for m in resp.json().get("models", [])]
                    configured_model = config.get("model", "").strip()
                    if not models:
                        return False, "Ollama is reachable but no models are installed.", []
                    if configured_model and configured_model not in models:
                        fallback = self._choose_ollama_fallback(
                            models,
                            context_store.get_routing_config().get("ollama_fallback_models"),
                        )
                        return (
                            True,
                            (
                                f"Ollama online; configured model '{configured_model}' is "
                                f"missing, using local fallback '{fallback}'."
                            ),
                            models,
                        )
                    return True, f"Ollama Online ({len(models)} models available)", models
                return False, f"Ollama responded with status {resp.status_code}", []

            elif provider in ("llama_cpp", "lm_studio"):
                resp = client.get(f"{base_url}/v1/models", timeout=2.5)
                if resp.status_code == 200:
                    models = [m.get("id", "") for m in resp.json().get("data", [])]
                    return True, f"{provider.upper()} Online ({len(models)} models)", models
                return False, f"Server responded with status {resp.status_code}", []

            elif provider in ("openai", "grok", "groq", "deepseek", "gemini", "claude"):
                online_providers = context_store.get_online_providers()
                p_cfg = online_providers.get(provider, {})
                api_key = p_cfg.get("api_key", "").strip()
                if not api_key:
                    return False, f"{provider.upper()} API Key not configured.", []
                return True, f"{provider.upper()} Configured & Ready", [p_cfg.get("model", "default")]

        except httpx.ConnectError:
            return False, f"Cannot connect to {provider} at {base_url}.", []
        except Exception as e:
            return False, f"Health check failed: {str(e)}", []

        return False, "Unknown provider or server unreachable", []

    @staticmethod
    def _choose_ollama_fallback(models: list[str], preferred: Optional[list[str]] = None) -> str:
        """Choose a small, free local model from the models already installed."""
        candidates = preferred or (
            "qwen2.5:3b",
            "phi4-mini",
            "phi4-mini:latest",
            "gemma3:4b",
            "llama3.2:3b",
            "phi3:mini",
            "gemma2:2b",
            "qwen2.5-coder:7b",
        )
        for candidate in candidates:
            if candidate in models:
                return candidate
        return models[0] if models else "qwen2.5:3b"

    def stream_response(self, mode: str, query: str) -> Generator[str, None, None]:
        """
        Main streaming entry point.
        Checks for Fastest-First Race Mode; otherwise dispatches with automatic 429 failover.
        """
        routing = context_store.get_routing_config()
        if routing.get("fastest_first_race", False):
            yield from self._stream_speculative_race(mode, query)
        else:
            yield from self._stream_with_failover(mode, query)

    def _stream_speculative_race(self, mode: str, query: str) -> Generator[str, None, None]:
        """
        'Speculative Duel' Engine:
        Races Local LLM vs primary Online LLM in parallel threads.
        The first model to yield tokens wins; the slower model is instantly cancelled.
        """
        local_cfg = context_store.get_llm_config()
        online_providers = context_store.get_online_providers()

        # Find first enabled online provider
        best_online = None
        for name, p_data in online_providers.items():
            if p_data.get("enabled", False) and p_data.get("api_key", "").strip():
                best_online = name
                break

        # If no online provider is configured, run normal stream
        if not best_online:
            yield from self._stream_with_failover(mode, query)
            return

        result_queue = queue.Queue()
        cancel_local = threading.Event()
        cancel_online = threading.Event()
        winner_announced = threading.Event()

        def run_candidate(provider_type: str, cancel_ev: threading.Event):
            try:
                if provider_type == "local":
                    stream = self._execute_provider_stream(local_cfg.get("provider", "ollama"), mode, query, cancel_ev)
                else:
                    stream = self._execute_provider_stream(best_online, mode, query, cancel_ev)

                first_chunk = True
                for token in stream:
                    if cancel_ev.is_set():
                        break
                    if first_chunk:
                        first_chunk = False
                        if not winner_announced.is_set():
                            winner_announced.set()
                            result_queue.put(("WINNER", provider_type))
                    result_queue.put(("TOKEN", token))
                result_queue.put(("DONE", provider_type))
            except Exception as e:
                result_queue.put(("ERROR", f"{provider_type}: {str(e)}"))

        t_local = threading.Thread(target=run_candidate, args=("local", cancel_local), daemon=True)
        t_online = threading.Thread(target=run_candidate, args=(best_online, cancel_online), daemon=True)

        t_local.start()
        t_online.start()

        winner_name = None
        winner_completed = False
        while True:
            # Check external abort
            if self._current_abort_event.is_set():
                cancel_local.set()
                cancel_online.set()
                break

            try:
                event_type, data = result_queue.get(timeout=0.05)
                if event_type == "WINNER":
                    winner_name = data
                    if winner_name == "local":
                        cancel_online.set()
                        yield f"⚡ *[Duel Winner: Local LLM ({local_cfg.get('provider', 'ollama')})]*\n\n"
                    else:
                        cancel_local.set()
                        yield f"⚡ *[Duel Winner: {winner_name.upper()} ({online_providers[winner_name].get('model')})]*\n\n"
                elif event_type == "TOKEN":
                    yield data
                elif event_type == "DONE":
                    if data == winner_name:
                        winner_completed = True
                        break
                elif event_type == "ERROR":
                    logger.warning(f"Duel candidate error: {data}")
            except queue.Empty:
                if not t_local.is_alive() and not t_online.is_alive() and result_queue.empty():
                    break

        # A provider can terminate without yielding a token (for example, an
        # empty or malformed stream). Do not silently finish with no answer.
        if not winner_completed:
            cancel_local.set()
            cancel_online.set()
            yield from self._stream_with_failover(mode, query)

    def _stream_with_failover(self, mode: str, query: str) -> Generator[str, None, None]:
        """
        Executes streaming with automatic 429 rate-limit and quota failover.
        Pool order: Primary Provider -> Enabled Online Providers -> Local LLM -> Built-in Mock.
        """
        config = context_store.get_llm_config()
        primary_provider = config.get("provider", "ollama")
        online_providers = context_store.get_online_providers()
        routing = context_store.get_routing_config()
        auto_failover = routing.get("auto_failover_on_rate_limit", True)

        # Build candidate providers list
        candidates = [primary_provider]
        if auto_failover:
            for p_name, p_data in online_providers.items():
                if p_data.get("enabled", False) and p_data.get("api_key", "").strip():
                    if p_name not in candidates:
                        candidates.append(p_name)

            # Include unlimited custom endpoints
            for c_endpoint in context_store.get_custom_endpoints():
                if c_endpoint.get("enabled", False) and c_endpoint.get("base_url"):
                    c_id = c_endpoint.get("id")
                    if c_id not in candidates:
                        candidates.append(c_id)

            if "ollama" not in candidates:
                candidates.append("ollama")
            if "mock" not in candidates:
                candidates.append("mock")

        for provider in candidates:
            # Check external abort
            if self._current_abort_event.is_set():
                break

            try:
                success = False
                for token in self._execute_provider_stream(provider, mode, query, self._current_abort_event):
                    if self._current_abort_event.is_set():
                        return
                    yield token
                    success = True

                if success:
                    return  # Completed successfully

            except RateLimitError as e:
                logger.warning(f"Rate limit hit on {provider}: {e}. Failing over to next provider in pool...")
                yield f"\n⚠️ *[Rate limit reached on {provider.upper()}. Automatically failing over...]*\n\n"
                continue
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}. Trying fallback...")
                continue

        # If everything fails, run mock engine
        yield "\n⚠️ *[All configured endpoints offline or rate-limited. Serving instant built-in response:]*\n\n"
        prefs = context_store.config.get("preferences", {})
        yield from self._stream_mock_response(mode, query, prefs.get("coding_language", "Python"))

    def _execute_provider_stream(self, provider: str, mode: str, query: str, abort_event: threading.Event) -> Generator[str, None, None]:
        """Dispatches streaming request to the specified provider."""
        profile = context_store.get_profile()
        prefs = context_store.config.get("preferences", {})
        coding_lang = prefs.get("coding_language", "Python")
        custom_instructions = context_store.get_custom_instructions()

        context_dict = {
            "resume": profile.get("resume", ""),
            "job_description": profile.get("job_description", ""),
            "language": coding_lang,
            "language_ext": coding_lang.lower(),
            "custom_instructions": custom_instructions
        }
        sys_prompt, user_prompt = build_prompt(mode, query, context_dict)

        if provider == "mock":
            yield from self._stream_mock_response(mode, query, coding_lang)
            return

        client = self.get_client()

        # 1. Local Ollama
        if provider == "ollama":
            llm_cfg = context_store.get_llm_config()
            base_url = llm_cfg.get("base_url", "http://127.0.0.1:11434").rstrip("/")
            model = llm_cfg.get("model", "qwen2.5:3b")
            try:
                tags = client.get(f"{base_url}/api/tags", timeout=3.0)
                if tags.status_code == 200:
                    installed = [
                        item.get("name", "")
                        for item in tags.json().get("models", [])
                        if item.get("name")
                    ]
                    if installed and model not in installed:
                        fallback = self._choose_ollama_fallback(
                            installed,
                            context_store.get_routing_config().get("ollama_fallback_models"),
                        )
                        logger.warning(
                            "Configured Ollama model '%s' is unavailable; using local fallback '%s'.",
                            model,
                            fallback,
                        )
                        model = fallback
            except Exception as exc:
                logger.debug("Unable to inspect Ollama models before streaming: %s", exc)
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "options": {"temperature": llm_cfg.get("temperature", 0.2), "num_predict": llm_cfg.get("max_tokens", 1500)},
                "stream": True
            }
            # Qwen 3 can spend the whole short interview budget in hidden
            # reasoning. Keep teleprompter responses direct and low-latency.
            if model.startswith("qwen3"):
                payload["think"] = False
            # Keep local generation responsive; fail over instead of blocking
            # the teleprompter for a long model-load or stalled stream.
            with client.stream(
                "POST",
                f"{base_url}/api/chat",
                json=payload,
                timeout=httpx.Timeout(20.0, connect=3.0, read=20.0, write=10.0, pool=3.0),
            ) as resp:
                if resp.status_code == 429:
                    raise RateLimitError("Ollama 429")
                if resp.status_code == 404:
                    model = payload["model"]
                    raise RuntimeError(
                        f"Ollama model '{model}' was not found. Run: ollama pull {model}"
                    )
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {resp.status_code}")
                for line in resp.iter_lines():
                    if abort_event.is_set():
                        break
                    if line:
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue

        # 2. Online OpenAI / Grok / Groq / DeepSeek / Gemini / llama_cpp / lm_studio / Custom Endpoints
        elif provider in ("openai", "grok", "groq", "deepseek", "gemini", "llama_cpp", "lm_studio") or str(provider).startswith("custom_"):
            online_providers = context_store.get_online_providers()
            custom_endpoints = {e.get("id"): e for e in context_store.get_custom_endpoints()}

            if provider in online_providers:
                p_cfg = online_providers[provider]
                base_url = p_cfg.get("base_url", "").rstrip("/")
                model = p_cfg.get("model", "gpt-4o")
                api_key = p_cfg.get("api_key", "").strip()
            elif provider in custom_endpoints:
                p_cfg = custom_endpoints[provider]
                base_url = p_cfg.get("base_url", "").rstrip("/")
                model = p_cfg.get("model", "default")
                api_key = p_cfg.get("api_key", "").strip()
            else:
                llm_cfg = context_store.get_llm_config()
                base_url = llm_cfg.get("base_url", "http://127.0.0.1:8080").rstrip("/")
                model = llm_cfg.get("model", "default")
                api_key = ""

            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            endpoint = self._chat_completions_endpoint(base_url)

            payload = {
                "model": model,
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.2,
                "stream": True
            }

            with client.stream("POST", endpoint, json=payload, headers=headers, timeout=35.0) as resp:
                if resp.status_code == 429:
                    raise RateLimitError(f"{provider} 429 Rate Limit")
                if resp.status_code == 402:
                    raise RateLimitError(f"{provider} 402 Quota Exceeded")
                if resp.status_code != 200:
                    raise RuntimeError(f"{provider} HTTP {resp.status_code}")

                for line in resp.iter_lines():
                    if abort_event.is_set():
                        break
                    if line.startswith("data: "):
                        raw_data = line[6:].strip()
                        if raw_data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw_data)
                            choices = chunk.get("choices", [])
                            if choices:
                                content = choices[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                        except Exception:
                            continue

        # 3. Anthropic Claude (native API)
        elif provider == "claude":
            online_providers = context_store.get_online_providers()
            p_cfg = online_providers.get("claude", {})
            api_key = p_cfg.get("api_key", "").strip()
            model = p_cfg.get("model", "claude-3-5-sonnet-20241022")
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": model,
                "system": sys_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
                "max_tokens": 1500,
                "stream": True
            }
            with client.stream("POST", "https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=35.0) as resp:
                if resp.status_code == 429:
                    raise RateLimitError("Claude 429 Rate Limit")
                if resp.status_code != 200:
                    raise RuntimeError(f"Claude HTTP {resp.status_code}")

                for line in resp.iter_lines():
                    if abort_event.is_set():
                        break
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[6:].strip())
                            if chunk.get("type") == "content_block_delta":
                                text = chunk.get("delta", {}).get("text", "")
                                if text:
                                    yield text
                        except Exception:
                            continue

    def _stream_mock_response(self, mode: str, query: str, language: str) -> Generator[str, None, None]:
        """Realistic simulated response for offline instant testing."""
        custom_instructions = context_store.get_custom_instructions()
        custom_note = f"\n*(Applied Custom Instructions: '{custom_instructions}')*\n\n" if custom_instructions else ""
        question = " ".join(query.split())
        question_preview = question[:500] if question else "the submitted question"

        if mode == "stealth_coder":
            if "two sum" in question.lower():
                content = f"""{custom_note}### 1. Intuition & Approach
- Use a hash map from value to index while scanning the array once.
- For each value, check whether its complement already exists.
- **Time Complexity:** O(N). **Space Complexity:** O(N).

### 2. Optimal Code ({language})
```{language.lower()}
def solve_problem(nums: list[int], target: int) -> list[int]:
    seen = {{}}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### 3. Step-by-Step Explanation (Speakable)
- *"I store each value and its index as I scan."*
- *"For every value, I calculate the complement needed to reach the target."*
- *"If that complement is already stored, I return both indices."*

### 4. Edge Cases & Dry Run
- Handles duplicates, negative values, an empty input, and a missing pair.
"""
            else:
                content = f"""{custom_note}### Offline fallback
The configured LLM endpoints were unavailable, so I did not invent a solution for this question:

> {question_preview}

Connect Ollama, llama.cpp, LM Studio, or an enabled online provider in Settings to generate the exact algorithm, code, complexity analysis, and edge cases for this problem.
"""
        elif mode == "star_behavioral":
            content = f"""{custom_note}- **Question**: {question_preview}
- **Situation**: Describe the specific project, incident, or challenge that best answers the question.
- **Task**: I owned the mission to stabilize write throughput and eliminate deadlocks within 48 hours.
- **Action**: I introduced an asynchronous Redis buffer and Kafka decoupled worker queue, batching commits in 50ms windows.
- **Result**: P99 latency dropped by 68% to 134ms, saving $45,000 monthly in infrastructure costs.
- **Key Takeaway**: Decouple synchronous write paths from relational locks.
"""
        elif mode == "system_design":
            content = f"""{custom_note}### Offline fallback
The system-design question was received:

> {question_preview}

Use this discussion structure when answering: clarify requirements, estimate scale, define the API and data model, draw the high-level architecture, then cover partitioning, caching, consistency, failure handling, and observability. Connect a configured LLM for a concrete design.
"""
        elif mode == "huddle_mate":
            content = f"""{custom_note}### Meeting exchange received
> {question_preview}

### Suggested response
- Confirm the decision or unresolved issue in one sentence.
- State the next action, owner, and expected deadline.
- Ask one clarifying question before committing to scope.
"""
        elif mode == "teleprompter":
            content = f"""{custom_note}- Address the question directly: {question_preview}
- Lead with the outcome, then give one supporting example.
- Mention a measurable result or trade-off.
- Close by checking whether the interviewer wants more detail.
"""
        else:
            content = f"""{custom_note}- Question received: {question_preview}
- Be direct, confident, and highlight measurable technical impact.
- Structure explanations with high-level intuition before deep technical dives.
"""

        words = content.split(" ")
        for i, word in enumerate(words):
            if self._current_abort_event.is_set():
                break
            yield word + (" " if i < len(words) - 1 else "")
            time.sleep(0.011)


class RateLimitError(Exception):
    """Raised when an LLM provider returns HTTP 429 or quota exceeded."""
    pass


# Singleton instance
llm_client = LocalLLMClient()
