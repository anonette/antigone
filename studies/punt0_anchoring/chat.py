"""Multi-turn chat completion for the PUNT0 anchoring study (standalone).

The main Antigone engine (antigone/completion.py) is deliberately single-turn
and prompt-only. This study needs three scripted turns with an optional system
message, so the chat call lives here, study-local, and mirrors the main
engine's routing conventions (OpenAI direct for openai/* when OPENAI_API_KEY
is set, OpenRouter otherwise, no cross-provider fallback). Transient failures
(429, 5xx, network errors) retry with backoff; a long run must survive them.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from antigone.openai_direct import is_reasoning_openai_model, openai_model_name  # noqa: E402
from antigone.openrouter import uses_openai_direct  # noqa: E402
from antigone.response_utils import extract_response_payload  # noqa: E402

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

MAX_ATTEMPTS = 5
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def complete_chat(
    *,
    openrouter_api_key: str | None,
    openai_api_key: str | None,
    model_config: dict[str, Any],
    messages: list[dict[str, str]],
    seed: int,
    timeout_s: float = 180.0,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """One chat completion over an explicit messages list (system/user/assistant)."""
    model_id = model_config["id"]
    thinking = bool(model_config.get("thinking"))
    reasoning_effort = model_config.get("reasoning_effort")
    # Reasoning models burn tokens on the hidden chain; give them headroom.
    max_tokens = 8192 if thinking else 4096

    if uses_openai_direct(model_config):
        if not openai_api_key:
            return _error(f"OPENAI_API_KEY required for {model_id} (OpenAI direct)", "openai", model_id)
        openai_name = openai_model_name(model_id, model_config)
        body: dict[str, Any] = {"model": openai_name, "messages": messages, "stream": False}
        params_sent: dict[str, Any] = {}
        if (thinking or is_reasoning_openai_model(openai_name)) and reasoning_effort:
            body["reasoning_effort"] = reasoning_effort
            params_sent["reasoning_effort"] = reasoning_effort
        else:
            body["temperature"] = temperature
            body["seed"] = seed
            params_sent.update({"temperature": temperature, "seed": seed})
        return _post(
            OPENAI_CHAT_URL, openai_api_key, body,
            backend="openai", model_id=model_id, extra_headers={},
            timeout_s=timeout_s, params_sent=params_sent,
        )

    if not openrouter_api_key:
        return _error(f"OPENROUTER_API_KEY required for {model_id}", "openrouter", model_id)
    body = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "provider": {"allow_fallbacks": False},
        "stream": False,
    }
    params_sent = {"temperature": temperature, "seed": seed, "max_tokens": max_tokens}
    if thinking and reasoning_effort:
        body["reasoning"] = {"effort": reasoning_effort}
        params_sent["reasoning_effort"] = reasoning_effort
    extra = {
        "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://github.com/antigone-study"),
        "X-OpenRouter-Title": os.environ.get("OPENROUTER_TITLE", "punt0-anchoring"),
    }
    return _post(
        OPENROUTER_CHAT_URL, openrouter_api_key, body,
        backend="openrouter", model_id=model_id, extra_headers=extra,
        timeout_s=timeout_s, params_sent=params_sent,
    )


def _error(msg: str, backend: str, model_id: str) -> dict[str, Any]:
    return {
        "status": "error",
        "http_status": None,
        "error": msg,
        "api_backend": backend,
        "model_requested": model_id,
        "request_mode": "chat_messages",
    }


def _post(
    url: str,
    api_key: str,
    body: dict[str, Any],
    *,
    backend: str,
    model_id: str,
    extra_headers: dict[str, str],
    timeout_s: float = 180.0,
    params_sent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", **extra_headers}
    started = time.perf_counter()
    last_error: dict[str, Any] = _error("no attempt made", backend, model_id)

    for attempt in range(MAX_ATTEMPTS):
        try:
            with httpx.Client(timeout=timeout_s) as client:
                resp = client.post(url, headers=headers, json=body)
        except httpx.HTTPError as exc:
            last_error = _error(f"{type(exc).__name__}: {exc}", backend, model_id)
            time.sleep(2 ** attempt)
            continue

        latency_ms = int((time.perf_counter() - started) * 1000)
        if resp.status_code in RETRYABLE_STATUSES:
            last_error = {
                "status": "error",
                "http_status": resp.status_code,
                "error": resp.text[:2000],
                "latency_ms": latency_ms,
                "api_backend": backend,
                "model_requested": model_id,
                "request_mode": "chat_messages",
            }
            try:
                wait = float(resp.headers.get("retry-after", 2 ** attempt))
            except ValueError:
                wait = float(2 ** attempt)
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            return {
                "status": "error",
                "http_status": resp.status_code,
                "error": resp.text[:2000],
                "latency_ms": latency_ms,
                "api_backend": backend,
                "model_requested": model_id,
                "request_mode": "chat_messages",
            }

        try:
            data = resp.json()
        except ValueError as exc:
            return {
                "status": "error",
                "http_status": resp.status_code,
                "error": f"unparseable JSON response: {exc}",
                "latency_ms": latency_ms,
                "api_backend": backend,
                "model_requested": model_id,
                "request_mode": "chat_messages",
            }

        extracted = extract_response_payload(data)
        return {
            "status": "ok",
            "http_status": 200,
            "latency_ms": latency_ms,
            "api_backend": backend,
            "request_mode": "chat_messages",
            "model_requested": model_id,
            "model_actual": data.get("model"),
            "params_sent": params_sent or {},
            "usage": data.get("usage"),
            **extracted,
            "raw_response": data,
        }

    return last_error
