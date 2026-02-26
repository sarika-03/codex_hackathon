"""EduGenie Streamlit application entrypoint."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from edugenie.chat import add_message, clear_chat, initialize_chat_state
from edugenie.config import get_settings
from edugenie.features import generate_quiz, study_plan_generator, summarize_topic
from edugenie.openrouter_client import get_chat_completion
from edugenie.topic_tracker import (
    extract_topic,
    increment_topic_count,
    initialize_topic_counter,
    top_topics,
)


def inject_custom_styles() -> None:
    """Inject lightweight UI styling without altering app logic."""
    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at 0% 0%, #1e293b 0%, #0f172a 48%, #020617 100%);
                font-family: "Inter", "Segoe UI", sans-serif;
            }
            .main .block-container {
                max-width: 1180px;
                padding-top: 0.6rem;
                padding-bottom: 0.8rem;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
                border-right: 1px solid rgba(148, 163, 184, 0.2);
            }
            [data-testid="stSidebar"] * {
                color: #e2e8f0 !important;
            }
            [data-testid="stSidebar"] .stCaption {
                color: #94a3b8 !important;
            }
            [data-testid="stChatMessage"] {
                border-radius: 14px;
                padding: 0.45rem 0.55rem;
                margin-bottom: 0.45rem;
                box-shadow: 0 3px 12px rgba(2, 6, 23, 0.28);
                background: rgba(15, 23, 42, 0.68);
                border: 1px solid rgba(148, 163, 184, 0.17);
            }
            .edg-hero {
                text-align: center;
                padding: 0.1rem 0 0.2rem 0;
            }
            .edg-title {
                font-size: 2.55rem;
                font-weight: 800;
                margin: 0;
                letter-spacing: 0.2px;
                background: linear-gradient(90deg, #60a5fa, #22d3ee, #2dd4bf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .edg-subtitle {
                color: #93c5fd;
                margin-top: 0.2rem;
                font-size: 0.98rem;
            }
            .edg-chat-shell {
                border-radius: 20px;
                padding: 1rem 1rem 0.35rem 1rem;
                background: linear-gradient(
                    180deg,
                    rgba(15, 23, 42, 0.76) 0%,
                    rgba(15, 23, 42, 0.58) 100%
                );
                border: 1px solid rgba(148, 163, 184, 0.2);
                box-shadow: 0 12px 36px rgba(2, 6, 23, 0.4);
                backdrop-filter: blur(8px);
                margin-top: 0.25rem;
            }
            [data-testid="stChatInput"] textarea {
                background: rgba(15, 23, 42, 0.86) !important;
                border: 1px solid rgba(56, 189, 248, 0.45) !important;
                border-radius: 16px !important;
                color: #e2e8f0 !important;
            }
            [data-testid="stChatInput"] textarea::placeholder {
                color: #94a3b8 !important;
            }
            .stButton > button {
                border-radius: 12px !important;
                border: 1px solid rgba(125, 211, 252, 0.42) !important;
                background: rgba(30, 41, 59, 0.9) !important;
                color: #e2e8f0 !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            }
            .stButton > button:hover {
                transform: translateY(-1px) scale(1.015);
                border-color: rgba(34, 211, 238, 0.88) !important;
                box-shadow: 0 8px 20px rgba(14, 165, 233, 0.22);
            }
            .stDivider {
                margin-top: 0.6rem !important;
                margin-bottom: 0.7rem !important;
            }
            .edg-footer {
                text-align: center;
                color: #94a3b8;
                font-size: 0.82rem;
                padding-bottom: 0.2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render top hero section."""
    st.markdown(
        """
        <div class="edg-hero">
            <h1 class="edg-title">EduGenie</h1>
            <p class="edg-subtitle">
                AI-powered academic assistant for smarter study, clearer concepts, and faster preparation
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


def render_footer() -> None:
    """Render footer content."""
    st.divider()
    st.markdown(
        '<div class="edg-footer">Built with ❤️ for smarter learning | EduGenie 2026</div>',
        unsafe_allow_html=True,
    )


def start_chat_shell() -> None:
    """Start styled wrapper for chat region."""
    st.markdown('<div class="edg-chat-shell">', unsafe_allow_html=True)


def end_chat_shell() -> None:
    """Close styled wrapper for chat region."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> Optional[str]:
    """Render sidebar controls and return selected smart-tool action."""
    st.sidebar.markdown("### 🎓 EduGenie")
    st.sidebar.caption("AI Academic Assistant")
    st.sidebar.markdown("---")

    st.sidebar.markdown("#### ⚙️ Settings")

    # Adaptive explanation mode persisted in session state via Streamlit key.
    st.sidebar.checkbox(
        "Explain Like I'm 10",
        key="explain_like_10",
        help="Use simple language, analogies, and real-life examples.",
    )

    if st.sidebar.button("Clear Chat"):
        clear_chat()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 🛠️ Smart Tools")
    st.sidebar.caption("Uses your latest message as the topic.")

    if st.sidebar.button("Generate Quiz 📝", use_container_width=True):
        return "quiz"
    if st.sidebar.button("Summarize Topic 📚", use_container_width=True):
        return "summary"
    if st.sidebar.button("Study Plan 📅", use_container_width=True):
        return "study_plan"

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📈 Learning Insights")
    st.sidebar.markdown("##### Your Weak Topics")
    weak_topics = top_topics(limit=3)
    if not weak_topics:
        st.sidebar.caption("No topics tracked yet. Start chatting to see insights.")
    else:
        for topic, count in weak_topics:
            st.sidebar.write(f"- {topic} ({count})")

    # Lightweight analytics view for most discussed topics.
    if st.session_state.topic_counter:
        chart_df = (
            pd.DataFrame(
                [
                    {"topic": topic, "frequency": count}
                    for topic, count in st.session_state.topic_counter.items()
                ]
            )
            .sort_values(by="frequency", ascending=False)
            .head(5)
            .set_index("topic")
        )
        st.sidebar.markdown("##### Topic Frequency (Top 5)")
        st.sidebar.caption("Most discussed topics in this learning session.")
        with st.sidebar:
            st.bar_chart(chart_df)
    return None


def get_last_user_message() -> Optional[str]:
    """Return the most recent user message from session history."""
    for message in reversed(st.session_state.messages):
        if message.get("role") == "user":
            content = message.get("content", "").strip()
            if content:
                return content
    return None


def run_smart_tool(tool_name: str, topic: str, api_key: str, model: str) -> str:
    """Dispatch selected smart tool to the corresponding feature function."""
    if tool_name == "quiz":
        return generate_quiz(topic=topic, api_key=api_key, model=model)
    if tool_name == "summary":
        return summarize_topic(topic=topic, api_key=api_key, model=model)
    if tool_name == "study_plan":
        return study_plan_generator(topic=topic, api_key=api_key, model=model)
    return "Unsupported smart tool requested."


def build_chat_messages() -> list[dict[str, str]]:
    """Build model input with adaptive system instruction + session history."""
    explain_like_10 = st.session_state.get("explain_like_10", False)
    if explain_like_10:
        system_instruction = (
            "Explain concepts in very simple language, using analogies and "
            "real-life examples suitable for a 10-year-old."
        )
    else:
        system_instruction = (
            "Provide clear, student-friendly academic explanations with "
            "accurate and structured reasoning."
        )

    return [{"role": "system", "content": system_instruction}, *st.session_state.messages]


def main() -> None:
    """Run Streamlit UI and chat workflow."""
    st.set_page_config(
        page_title="EduGenie – AI Academic Assistant",
        page_icon="🎓",
        layout="wide",
    )
    inject_custom_styles()

    settings = get_settings()
    initialize_chat_state()
    initialize_topic_counter()
    selected_tool = render_sidebar()

    # UI layout: centered content area to reduce excess whitespace.
    _, center_col, _ = st.columns([1, 6.5, 1])
    with center_col:
        render_hero()
        start_chat_shell()

        # Display prior conversation (session-based memory).
        for message in st.session_state.messages:
            avatar = "👩‍🎓" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Tool actions behave like assistant messages and remain in memory.
        if selected_tool:
            topic = get_last_user_message()
            with st.chat_message("assistant", avatar="🤖"):
                if not topic:
                    tool_output = (
                        "Please send at least one message first. "
                        "Smart Tools use your latest question/topic."
                    )
                else:
                    with st.spinner("Running smart tool..."):
                        try:
                            tool_output = run_smart_tool(
                                tool_name=selected_tool,
                                topic=topic,
                                api_key=settings.openrouter_api_key,
                                model=settings.openrouter_model,
                            )
                        except ValueError as exc:
                            tool_output = f"Configuration error: {exc}"
                        except Exception as exc:  # noqa: BLE001
                            tool_output = (
                                "Smart tool request failed. "
                                f"Details: {exc}"
                            )
                st.markdown(tool_output)
            add_message("assistant", tool_output)

        prompt = st.chat_input("Ask a question about any topic...")
        if not prompt:
            end_chat_shell()
            render_footer()
            return

        # Track user topic frequency to identify weak areas from repeated queries.
        topic = extract_topic(prompt)
        increment_topic_count(topic)

        add_message("user", prompt)
        with st.chat_message("user", avatar="👩‍🎓"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    answer = get_chat_completion(
                        api_key=settings.openrouter_api_key,
                        model=settings.openrouter_model,
                        messages=build_chat_messages(),
                    )
                except ValueError as exc:
                    answer = f"Configuration error: {exc}"
                except Exception as exc:  # noqa: BLE001
                    answer = (
                        "Something went wrong while contacting the AI service. "
                        f"Details: {exc}"
                    )
                st.markdown(answer)

        add_message("assistant", answer)
        end_chat_shell()
        render_footer()


if __name__ == "__main__":
    main()
