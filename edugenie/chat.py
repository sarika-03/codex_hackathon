"""Chat state and message helpers."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st

Message = Dict[str, str]


def initialize_chat_state() -> None:
    """Ensure session-level chat history exists."""
    if "messages" not in st.session_state:
        st.session_state.messages: List[Message] = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I am EduGenie. Ask me anything about your studies, "
                    "topics, or exam preparation."
                ),
            }
        ]


def add_message(role: str, content: str) -> None:
    """Append one message to session history."""
    st.session_state.messages.append({"role": role, "content": content})


def clear_chat() -> None:
    """Reset chat history to initial assistant greeting."""
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I am EduGenie. Ask me anything about your studies, "
                "topics, or exam preparation."
            ),
        }
    ]

