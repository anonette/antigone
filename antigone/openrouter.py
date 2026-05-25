"""OpenRouter API — non-OpenAI models (and openai/* only if no OPENAI_API_KEY)."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from antigone.response_utils import extract_response_payload

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def uses_openai_direct(model_config: dict[str, Any]) -> bool:
    """True when this entry should call api.openai.com, not OpenRouter."""
    api = model_config.get("api")
    if api == "openai":
        return True
    if api == "openrouter":
        return False
    return str(model_config.get("id", "")).startswith("openai/")


def complete_openrouter(
    *,
    api_key: str,
    model_id: str,
    prompt_text: str,
    seed: int,
    thinking: bool = False,
    reasoning_effort: str | None = "medium",
    timeout_s: float = 180.0,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Single stateless completion via OpenRouter.

    Uses ``prompt`` field only (no messages / roles / history).
    ``provider.allow_fallbacks`` is false.
    """
    body: dict[str, Any] = {
        "model": model_id,
        "prompt": prompt_text,
        "temperature": temperature,
        "seed": seed,
        "max_tokens": 4096,
        "provider": {"allow_fallbacks": False},
        "stream": False,
    }
    if thinking and reasoning_effort:
        body["reasoning"] = {"effort": reasoning_effort}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://github.com/antigone-study"),
        "X-OpenRouter-Title": os.environ.get("OPENROUTER_TITLE", "antigone-burial-dilemma"),
    }

    started = time.perf_counter()
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(OPENROUTER_URL, headers=headers, json=body)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if resp.status_code != 200:
        return {
            "status": "error",
            "http_status": resp.status_code,
            "error": resp.text,
            "latency_ms": latency_ms,
            "api_backend": "openrouter",
            "request_mode": "prompt_only",
        }

    data = resp.json()
    extracted = extract_response_payload(data)
    return {
        "status": "ok",
        "http_status": 200,
        "latency_ms": latency_ms,
        "api_backend": "openrouter",
        "request_mode": "prompt_only",
        "model_requested": model_id,
        "model_actual": data.get("model"),
        "openrouter_id": data.get("id"),
        "usage": data.get("usage"),
        **extracted,
        "raw_response": data,
    }
