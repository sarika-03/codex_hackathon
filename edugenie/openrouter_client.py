"""OpenRouter integration via OpenAI-compatible API."""

from __future__ import annotations

from typing import Dict, List

from openai import APIStatusError, OpenAI

Message = Dict[str, str]


def get_chat_completion(
    api_key: str,
    model: str,
    messages: List[Message],
    temperature: float = 0.2,
) -> str:
    """
    Generate an assistant response from OpenRouter.

    Uses the OpenAI-compatible endpoint with a free model by default.
    """
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
        )
    except APIStatusError as exc:
        if exc.status_code in {402, 429}:
            return (
                "OpenRouter free quota/rate limit reached. "
                "Please try again later or choose another free model."
            )
        raise

    content = response.choices[0].message.content
    return content or "I could not generate a response. Please try again."

