"""Lightweight topic extraction and in-session tracking utilities."""

from __future__ import annotations

import re
from collections import Counter

import streamlit as st

# Small stopword set to keep extraction lightweight and dependency-free.
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "should",
    "tell",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with",
    "you",
}


def extract_topic(user_message: str) -> str:
    """
    Extract one short topic keyword from a user message.

    Uses simple token cleanup + frequency scoring with no external NLP libs.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", user_message.lower())
    tokens = [
        token
        for token in cleaned.split()
        if token not in STOPWORDS and len(token) > 2 and not token.isdigit()
    ]
    if not tokens:
        return "general"

    counts = Counter(tokens)
    # Prefer higher frequency tokens, then longer tokens as a tiebreaker.
    best_topic = max(counts.items(), key=lambda item: (item[1], len(item[0])))[0]
    return best_topic


def initialize_topic_counter() -> None:
    """Ensure topic frequency tracker exists in session state."""
    if "topic_counter" not in st.session_state:
        st.session_state.topic_counter = {}


def increment_topic_count(topic: str) -> None:
    """Increment frequency for the extracted topic in session memory."""
    current = st.session_state.topic_counter.get(topic, 0)
    st.session_state.topic_counter[topic] = current + 1


def top_topics(limit: int = 3) -> list[tuple[str, int]]:
    """Return top topics sorted by frequency descending."""
    items = st.session_state.topic_counter.items()
    return sorted(items, key=lambda item: item[1], reverse=True)[:limit]

