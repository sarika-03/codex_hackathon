"""Gemini integration layer exposed through a chat-completion style interface."""

from __future__ import annotations

from typing import Dict, List

from google import genai
from google.genai import errors as genai_errors

Message = Dict[str, str]


def get_chat_completion(
    api_key: str,
    model: str,
    messages: List[Message],
    temperature: float = 0.2,
) -> str:
    """
    Generate an assistant response from Gemini.

    Raises:
        ValueError: If API key is missing.
        Exception: Propagates SDK exceptions for caller-level handling.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    # Convert role-based chat messages into a single Gemini prompt while
    # preserving session context and system instructions.
    prompt = _build_gemini_prompt(messages)
    client = genai.Client(api_key=api_key)
    selected_model = _resolve_model(client=client, requested_model=model)

    try:
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
            config={"temperature": temperature},
        )
    except genai_errors.ClientError as exc:
        status_code = getattr(exc, "status_code", None)
        if status_code == 429 or "RESOURCE_EXHAUSTED" in str(exc):
            return _local_fallback_response(messages)
        if status_code == 404 or "NOT_FOUND" in str(exc):
            return _local_fallback_response(messages)
        raise
    content = _extract_response_text(response)
    return content or _local_fallback_response(messages)


def _build_gemini_prompt(messages: List[Message]) -> str:
    """Build a structured prompt from role-based message history."""
    system_instructions: list[str] = []
    transcript: list[str] = []

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "").strip()
        if not content:
            continue
        if role == "system":
            system_instructions.append(content)
        elif role == "assistant":
            transcript.append(f"Assistant: {content}")
        else:
            transcript.append(f"User: {content}")

    prompt_sections: list[str] = []
    if system_instructions:
        prompt_sections.append("System Instructions:\n" + "\n".join(system_instructions))
    if transcript:
        prompt_sections.append("Conversation:\n" + "\n".join(transcript))
    prompt_sections.append("Assistant:")
    return "\n\n".join(prompt_sections)


def _extract_response_text(response: object) -> str:
    """Extract response text safely across Gemini response shapes."""
    text = getattr(response, "text", None)
    if text:
        return text.strip()
    return ""


def _resolve_model(client: genai.Client, requested_model: str) -> str:
    """Pick a working generateContent model if requested model is unavailable."""
    try:
        available: set[str] = set()
        for model_obj in client.models.list():
            name = getattr(model_obj, "name", "")
            actions = getattr(model_obj, "supported_actions", []) or []
            if name and "generateContent" in actions:
                available.add(name.removeprefix("models/"))

        if requested_model in available:
            return requested_model

        preferred = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-pro-latest",
        ]
        for candidate in preferred:
            if candidate in available:
                return candidate
    except Exception:  # noqa: BLE001
        pass
    return requested_model


def _local_fallback_response(messages: List[Message]) -> str:
    """Return a lightweight offline response when API is unavailable."""
    user_query = ""
    simple_mode = False
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        if role == "system" and "10-year-old" in content:
            simple_mode = True
        if role == "user" and content.strip():
            user_query = content.strip()

    if not user_query:
        user_query = "your topic"

    if simple_mode:
        return (
            "AI service abhi unavailable hai, lekin main simple explain karta hoon.\n\n"
            f"Topic: **{user_query}**\n"
            "- Is topic ko ek chhote step se start karo.\n"
            "- Real life example socho.\n"
            "- 3 short points likho jo tumhe yaad rakhne hain.\n"
            "- End me khud ko 2 questions pucho.\n\n"
            "Tip: thodi der baad phir se try karo, API restore hone par detailed answer milega."
        )

    return (
        "AI API currently unavailable, so here is a quick fallback study guide.\n\n"
        f"Topic: **{user_query}**\n"
        "1. Define the core concept in 2-3 lines.\n"
        "2. List key terms and formulas/points.\n"
        "3. Solve one basic and one medium example.\n"
        "4. Write a short revision note.\n\n"
        "Retry shortly for full AI-generated response."
    )
