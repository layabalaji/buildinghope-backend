# Building Hope San Diego — backend

FastAPI app powering the chatbot: intent routing, retrieval over research
docs, and the AI API call. Keeps the API key off the browser entirely.

## Getting started

```bash
git clone https://github.com/<your-username>/buildinghopesd-backend.git
cd buildinghopesd-backend
code .

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then open .env and add your real key
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` — FastAPI's auto-generated test page,
useful for trying `/chat` without the frontend at all.

## Structure
```
main.py                     App entry point, CORS setup
requirements.txt
.env.example                Copy to .env, fill in your real key, never commit .env
app/
  routers/classify.py       Intent classifier (placeholder until your neural net is trained)
  routers/chat.py           /chat endpoint — ties classification + retrieval + AI API together
  retrieval.py              Search over data/research/
data/research/               Drop your research .txt/.md files here
models/                      Drop your trained classifier file here, later
```

## Getting an API key
Create one at console.anthropic.com — free trial credits are enough for a
project like this. It goes in `.env`, never in code, never committed.

Without a key, navigation/off-topic/crisis replies still work (no API call
needed) — only informational Q&A needs it.

## Deploying (no domain needed yet)
Push to GitHub, then deploy on Render or Railway with the start command:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```
Add `ANTHROPIC_API_KEY` as an environment variable in the host's dashboard —
not in a committed file. You'll get a free URL; paste it into the frontend's
`BHSD_CHAT_ENDPOINT` once it's live.