"""Shared response parsing for OpenAI and OpenRouter APIs."""

from __future__ import annotations

import hashlib
from typing import Any


def deterministic_seed(stimulus_id: str, model_id: str, replicate: int) -> int:
    raw = f"{stimulus_id}:{model_id}:{replicate}".encode()
    return int(hashlib.sha256(raw).hexdigest()[:8], 16) % (2**31 - 1)


def extract_response_payload(data: dict[str, Any]) -> dict[str, Any]:
    choices = data.get("choices") or []
    if not choices:
        return {
            "response_text": None,
            "reasoning_text": None,
            "finish_reason": None,
        }
    choice = choices[0]
    msg = choice.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        parts = [
            p.get("text", "")
            for p in content
            if isinstance(p, dict) and p.get("type") == "text"
        ]
        content = "\n".join(p for p in parts if p)
    if not content:
        # OpenRouter prompt API returns completion in choices[].text
        content = choice.get("text")
    reasoning = msg.get("reasoning")
    if reasoning is None:
        reasoning = msg.get("reasoning_content")
    if reasoning is None:
        reasoning = choice.get("reasoning")
    return {
        "response_text": content,
        "reasoning_text": reasoning,
        "finish_reason": choice.get("finish_reason"),
    }
