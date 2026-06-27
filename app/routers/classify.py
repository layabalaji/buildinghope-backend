"""
Intent classifier.

TEMPORARY: this is a simple keyword-based stand-in so the rest of the
pipeline (chat.py, the frontend widget) has something real to talk to
while you build and train the actual neural network.

WHEN YOUR MODEL IS READY:
Replace the body of `classify_intent` with something like:

    import joblib
    _model = joblib.load("models/intent_classifier.joblib")
    _embedder = ...  # whatever you used to turn text into features

    def classify_intent(text: str) -> dict:
        features = _embedder.encode([text])
        intent = _model.predict(features)[0]
        ...

Keep the same return shape so chat.py doesn't need to change:
    {"intent": "navigation" | "informational" | "crisis" | "off_topic",
     "page": "home" | "about" | "issue" | "events" | "involved" | "contact" | None}
"""

from __future__ import annotations

NAV_KEYWORDS = {
    "home": ["home", "homepage", "main page"],
    "about": ["about", "who are you", "your team", "your story"],
    "issue": ["the issue", "research", "statistics", "why hygiene", "background"],
    "events": ["event", "events", "schedule", "when is", "upcoming"],
    "involved": ["volunteer", "donate", "get involved", "sign up", "help out"],
    "contact": ["contact", "email you", "reach you", "get in touch"],
}

# Deliberately conservative and narrow — false negatives here (missing a
# real disclosure) are worse than false positives (occasionally routing a
# borderline message here when it wasn't strictly necessary).
CRISIS_KEYWORDS = [
    "i'm homeless", "i am homeless", "i have nowhere to stay", "nowhere to sleep",
    "i ran away", "running away", "i need a place to stay tonight",
    "kicked me out", "i'm scared to go home", "thinking about suicide",
    "want to hurt myself", "self harm",
]


def classify_intent(text: str) -> dict:
    lowered = text.lower()

    for phrase in CRISIS_KEYWORDS:
        if phrase in lowered:
            return {"intent": "crisis", "page": None}

    for page, keywords in NAV_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return {"intent": "navigation", "page": page}

    # Anything that looks like a real question gets treated as informational
    # and routed to retrieval + the AI API. Everything else falls back to
    # off_topic. This split is intentionally crude — your trained classifier
    # should replace it with something far better.
    question_markers = ["what", "why", "how", "who", "when", "is youth", "are youth", "?"]
    if any(marker in lowered for marker in question_markers):
        return {"intent": "informational", "page": None}

    return {"intent": "off_topic", "page": None}