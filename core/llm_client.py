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
                        break
                elif event_type == "ERROR":
                    logger.warning(f"Duel candidate error: {data}")
            except queue.Empty:
                if not t_local.is_alive() and not t_online.is_alive() and result_queue.empty():
                    break

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
            payload = {
                "model": llm_cfg.get("model", "qwen2.5-coder:7b"),
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "options": {"temperature": llm_cfg.get("temperature", 0.2), "num_predict": llm_cfg.get("max_tokens", 1500)},
                "stream": True
            }
            with client.stream("POST", f"{base_url}/api/chat", json=payload, timeout=35.0) as resp:
                if resp.status_code == 429:
                    raise RateLimitError("Ollama 429")
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

            endpoint = f"{base_url}/chat/completions" if base_url.endswith("/v1") else f"{base_url}/v1/chat/completions"

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

        if mode == "stealth_coder":
            content = f"""{custom_note}### 1. Intuition & Approach
- We use a **HashMap (Hash Table)** to store previously seen numbers and their indices in a single pass.
- For each element `x`, we check if the complement `target - x` exists in our map. This transforms an `O(N^2)` brute-force search into an optimal **O(N)** solution.
- **Time Complexity:** O(N) single pass.
- **Space Complexity:** O(N) auxiliary space.

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
- *"First, I maintain a hash map of visited items."*
- *"For every item, I compute the required complement needed to hit the target."*
- *"If the complement is present, we return the pair immediately in O(1) time."*

### 4. Edge Cases & Dry Run
- **Negative values:** Subtraction arithmetic preserves exact target.
- **Duplicates:** Handled correctly since lookup precedes map insertion.
"""
        elif mode == "star_behavioral":
            content = f"""{custom_note}- **Situation**: During a peak traffic event, lock contention in our relational database caused P99 latency spikes of 420ms.
- **Task**: I owned the mission to stabilize write throughput and eliminate deadlocks within 48 hours.
- **Action**: I introduced an asynchronous Redis buffer and Kafka decoupled worker queue, batching commits in 50ms windows.
- **Result**: P99 latency dropped by 68% to 134ms, saving $45,000 monthly in infrastructure costs.
- **Key Takeaway**: Decouple synchronous write paths from relational locks.
"""
        else:
            content = f"""{custom_note}- Be direct, confident, and highlight measurable technical impact.
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
