# EduGenie

AI-Powered Chatbot for Student Queries built with Streamlit and OpenRouter API.

## Tech Stack
- Frontend: Streamlit
- Backend Logic: Python
- AI Integration: OpenRouter API (`openai` SDK, OpenAI-compatible endpoint)
- Config: Environment variables (`python-dotenv`)

## Project Structure
```text
EduGenie/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── edugenie/
    ├── __init__.py
    ├── chat.py
    ├── config.py
    ├── features.py
    ├── openai_client.py
    └── openrouter_client.py
```

## Setup
1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
cp .env.example .env
```
Then edit `.env` and set:
- `OPENROUTER_API_KEY=...`
- Optional: `OPENROUTER_MODEL=openrouter/free`

## Run
```bash
streamlit run app.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Deploy (Render)
This repo includes `render.yaml` for one-click deployment.

1. Push this project to GitHub.
2. In Render, create a new **Blueprint** and select the repo.
3. Set secret env var:
   - `OPENROUTER_API_KEY=...`
4. Deploy.

Render will run:
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

## Features Implemented
- Chat interface via Streamlit chat components
- Session-based memory (`st.session_state.messages`)
- OpenRouter response integration
- Environment-variable based API key loading
- Basic error handling for missing key/API failures

## Bonus Placeholders Included
- `generate_quiz(topic)`
- `summarize_topic(topic_text)`
- `study_plan_generator(goal, duration_days)`

These are currently placeholders and can be replaced with richer OpenRouter-powered workflows later.
