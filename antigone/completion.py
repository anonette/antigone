"""Route each request to OpenAI direct or OpenRouter — no cross-provider fallback."""

from __future__ import annotations

from typing import Any

from antigone.openai_direct import complete_openai
from antigone.openrouter import complete_openrouter, uses_openai_direct


def complete(
    *,
    openrouter_api_key: str | None,
    openai_api_key: str | None,
    model_config: dict[str, Any],
    prompt_text: str,
    seed: int,
    timeout_s: float = 180.0,
    temperature: float = 0.0,
) -> dict[str, Any]:
    model_id = model_config["id"]
    thinking = bool(model_config.get("thinking"))
    reasoning_effort = model_config.get("reasoning_effort")

    if uses_openai_direct(model_config):
        if not openai_api_key:
            return {
                "status": "error",
                "http_status": None,
                "error": f"OPENAI_API_KEY required for {model_id} (OpenAI direct)",
                "api_backend": "openai",
                "model_requested": model_id,
            }
        return complete_openai(
            api_key=openai_api_key,
            model_id=model_id,
            model_config=model_config,
            prompt_text=prompt_text,
            seed=seed,
            thinking=thinking,
            reasoning_effort=reasoning_effort,
            timeout_s=timeout_s,
            temperature=temperature,
        )

    if not openrouter_api_key:
        return {
            "status": "error",
            "http_status": None,
            "error": f"OPENROUTER_API_KEY required for {model_id}",
            "api_backend": "openrouter",
            "model_requested": model_id,
        }
    return complete_openrouter(
        api_key=openrouter_api_key,
        model_id=model_id,
        prompt_text=prompt_text,
        seed=seed,
        thinking=thinking,
        reasoning_effort=reasoning_effort,
        timeout_s=timeout_s,
        temperature=temperature,
    )
