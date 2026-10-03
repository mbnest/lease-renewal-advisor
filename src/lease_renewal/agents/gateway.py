"""OpenRouter client for the spike.

One gateway (ADR-017). The model slug and the upstream provider are pinned and
fallback routing is off, so a run is attributable to one model on one provider.
"""

import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-5-nano"
PROVIDER = "openai"


@dataclass(frozen=True)
class Call:
    """One completed model call."""

    content: str
    prompt_tokens: int
    completion_tokens: int
    model: str
    provider: str


def _api_key() -> str:
    load_dotenv()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Copy .env.example to .env.")
    return key


def call_json(system: str, user: str, schema: dict, seed: int = 7) -> Call:
    """Send one request and return the structured JSON string it produced."""
    body = {
        "model": MODEL,
        "provider": {"order": [PROVIDER], "allow_fallbacks": False},
        "seed": seed,
        "max_tokens": 16000,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "baseline_output", "strict": True, "schema": schema},
        },
    }
    response = httpx.post(
        URL,
        headers={"Authorization": f"Bearer {_api_key()}"},
        json=body,
        timeout=120.0,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"Gateway error: {payload['error']}")
    choice = payload["choices"][0]
    content = choice["message"].get("content")
    if not content:
        raise RuntimeError(
            f"Gateway returned no content. finish_reason={choice.get('finish_reason')!r} "
            f"usage={payload.get('usage')}"
        )
    usage = payload.get("usage", {})
    return Call(
        content=content,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        model=payload.get("model", MODEL),
        provider=payload.get("provider", PROVIDER),
    )


async def call_json_async(
    client: httpx.AsyncClient, system: str, user: str, schema: dict, seed: int = 7
) -> Call:
    """Async form of call_json, for running specialists in parallel."""
    body = {
        "model": MODEL,
        "provider": {"order": [PROVIDER], "allow_fallbacks": False},
        "seed": seed,
        "max_tokens": 16000,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "agent_output", "strict": True, "schema": schema},
        },
    }
    response = await client.post(
        URL, headers={"Authorization": f"Bearer {_api_key()}"}, json=body, timeout=180.0
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"Gateway error: {payload['error']}")
    choice = payload["choices"][0]
    content = choice["message"].get("content")
    if not content:
        raise RuntimeError(
            f"Gateway returned no content. finish_reason={choice.get('finish_reason')!r} "
            f"usage={payload.get('usage')}"
        )
    usage = payload.get("usage", {})
    return Call(
        content=content,
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        model=payload.get("model", MODEL),
        provider=payload.get("provider", PROVIDER),
    )
