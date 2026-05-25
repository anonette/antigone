"""Direct OpenAI API — for openai/* models when OPENAI_API_KEY is set."""

from __future__ import annotations

import time
from typing import Any

import httpx

from antigone.response_utils import extract_response_payload

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# Models that use reasoning_effort instead of temperature (OpenAI direct).
REASONING_MODEL_PREFIXES = ("o1", "o3", "o4", "gpt-5")


def openai_model_name(model_id: str, model_config: dict[str, Any]) -> str:
    if model_config.get("openai_model"):
        return str(model_config["openai_model"])
    if model_id.startswith("openai/"):
        return model_id[len("openai/") :]
    return model_id


def is_reasoning_openai_model(openai_name: str) -> bool:
    return openai_name.startswith(REASONING_MODEL_PREFIXES)


def complete_openai(
    *,
    api_key: str,
    model_id: str,
    model_config: dict[str, Any],
    prompt_text: str,
    seed: int,
    thinking: bool = False,
    reasoning_effort: str | None = "medium",
    timeout_s: float = 180.0,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Single stateless call to api.openai.com.

    OpenAI chat completions require at least one message; we send exactly one
    ``user`` message (no system, no history) — minimal role use on this API.
    """
    openai_name = openai_model_name(model_id, model_config)
    use_reasoning = thinking or is_reasoning_openai_model(openai_name)

    body: dict[str, Any] = {
        "model": openai_name,
        "messages": [{"role": "user", "content": prompt_text}],
        "stream": False,
    }
    if use_reasoning and reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    else:
        body["temperature"] = temperature
        body["seed"] = seed

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    started = time.perf_counter()
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(OPENAI_URL, headers=headers, json=body)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if resp.status_code != 200:
        return {
            "status": "error",
            "http_status": resp.status_code,
            "error": resp.text,
            "latency_ms": latency_ms,
            "api_backend": "openai",
            "request_mode": "single_user_message",
            "openai_model": openai_name,
        }

    data = resp.json()
    extracted = extract_response_payload(data)
    return {
        "status": "ok",
        "http_status": 200,
        "latency_ms": latency_ms,
        "api_backend": "openai",
        "request_mode": "single_user_message",
        "model_requested": model_id,
        "openai_model": openai_name,
        "model_actual": data.get("model"),
        "openai_id": data.get("id"),
        "usage": data.get("usage"),
        **extracted,
        "raw_response": data,
    }
