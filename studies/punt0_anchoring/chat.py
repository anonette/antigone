"""Multi-turn chat completion for the PUNT0 anchoring study (standalone).

The main Antigone engine (antigone/completion.py) is deliberately single-turn
and prompt-only. This study needs three scripted turns with an optional system
message, so the chat call lives here, study-local, and mirrors the main
engine's routing conventions (OpenAI direct for openai/* when OPENAI_API_KEY
is set, OpenRouter otherwise, no cross-provider fallback).
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

    if uses_openai_direct(model_config):
        if not openai_api_key:
            return _error(f"OPENAI_API_KEY required for {model_id} (OpenAI direct)", "openai", model_id)
        openai_name = openai_model_name(model_id, model_config)
        body: dict[str, Any] = {"model": openai_name, "messages": messages, "stream": False}
        if (thinking or is_reasoning_openai_model(openai_name)) and reasoning_effort:
            body["reasoning_effort"] = reasoning_effort
        else:
            body["temperature"] = temperature
            body["seed"] = seed
        return _post(OPENAI_CHAT_URL, openai_api_key, body, backend="openai", model_id=model_id, extra_headers={})

    if not openrouter_api_key:
        return _error(f"OPENROUTER_API_KEY required for {model_id}", "openrouter", model_id)
    body = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "seed": seed,
        "max_tokens": 4096,
        "provider": {"allow_fallbacks": False},
        "stream": False,
    }
    if thinking and reasoning_effort:
        body["reasoning"] = {"effort": reasoning_effort}
    extra = {
        "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://github.com/antigone-study"),
        "X-OpenRouter-Title": os.environ.get("OPENROUTER_TITLE", "punt0-anchoring"),
    }
    return _post(OPENROUTER_CHAT_URL, openrouter_api_key, body, backend="openrouter", model_id=model_id, extra_headers=extra)


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
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", **extra_headers}
    started = time.perf_counter()
    with httpx.Client(timeout=body.pop("_timeout", 180.0) if "_timeout" in body else 180.0) as client:
        resp = client.post(url, headers=headers, json=body)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if resp.status_code != 200:
        return {
            "status": "error",
            "http_status": resp.status_code,
            "error": resp.text,
            "latency_ms": latency_ms,
            "api_backend": backend,
            "model_requested": model_id,
            "request_mode": "chat_messages",
        }

    data = resp.json()
    extracted = extract_response_payload(data)
    return {
        "status": "ok",
        "http_status": 200,
        "latency_ms": latency_ms,
        "api_backend": backend,
        "request_mode": "chat_messages",
        "model_requested": model_id,
        "model_actual": data.get("model"),
        "usage": data.get("usage"),
        **extracted,
        "raw_response": data,
    }
