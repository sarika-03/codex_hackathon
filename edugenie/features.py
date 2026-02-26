"""Academic feature helpers powered by OpenRouter."""

from __future__ import annotations

from edugenie.openrouter_client import get_chat_completion


def generate_quiz(topic: str, api_key: str, model: str) -> str:
    """Generate a 5-question MCQ quiz for the provided topic."""
    prompt = f"""
Create a student-friendly quiz on: "{topic}".

Requirements:
- Exactly 5 multiple-choice questions.
- Each question must have 4 options (A, B, C, D).
- Keep difficulty moderate for students.
- After all questions, add a separate "Answer Key" section.
- The answer key must list only question number and correct option letter.
"""
    return _run_feature_prompt(prompt=prompt, api_key=api_key, model=model)


def summarize_topic(topic: str, api_key: str, model: str) -> str:
    """Summarize a topic with clear, structured bullet points."""
    prompt = f"""
Summarize this topic for a student audience: "{topic}".

Requirements:
- Use concise bullet points.
- Include key concepts and definitions.
- Add a short "Why this matters" section.
- Keep language simple and exam-oriented.
"""
    return _run_feature_prompt(prompt=prompt, api_key=api_key, model=model)


def study_plan_generator(topic: str, api_key: str, model: str) -> str:
    """Generate a structured 7-day study plan with revision strategy."""
    prompt = f"""
Create a 7-day study plan for: "{topic}".

Requirements:
- Provide Day 1 to Day 7 clearly.
- Include daily goals and suggested practice tasks.
- Include one revision strategy section for retention.
- Keep it realistic for students with limited time.
"""
    return _run_feature_prompt(prompt=prompt, api_key=api_key, model=model)


def _run_feature_prompt(prompt: str, api_key: str, model: str) -> str:
    """Run feature-specific prompt through the shared OpenRouter chat client."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are EduGenie, an academic AI assistant. "
                "Provide well-structured, accurate, student-friendly responses."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    return get_chat_completion(
        api_key=api_key,
        model=model,
        messages=messages,
        temperature=0.3,
    )
