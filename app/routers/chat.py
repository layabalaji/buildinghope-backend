"""
The /chat endpoint — this is where intent classification, retrieval, and
the AI API call all come together.

Flow:
  1. classify_intent() — your trained neural net (currently a placeholder,
     see classify.py) decides what kind of message this is.
  2. Branch on the intent:
       - navigation  -> canned reply, no API call
       - informational -> retrieve relevant research chunks, then call
         the AI API with that context so the answer is grounded
       - crisis      -> fixed, pre-written resources. No generation here
         on purpose — a sensitive moment is not the place for an
         improvised model response.
       - off_topic   -> polite redirect
"""

from __future__ import annotations

import os
from fastapi import APIRouter
from pydantic import BaseModel
import anthropic

from app.routers.classify import classify_intent
from app.retrieval import get_relevant_chunks

router = APIRouter()

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Check docs.claude.com for the latest model name if this one has aged out.
MODEL_NAME = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

SYSTEM_PROMPT = (
    "You are the help assistant on the Building Hope San Diego website, a "
    "student-led nonprofit supporting underserved youth in San Diego. Answer "
    "only using the provided research context. If the context doesn't cover "
    "the question, say so honestly rather than guessing. Keep answers concise "
    "(3-5 sentences) and cite which source you drew from when relevant. Stay "
    "strictly on topic: Building Hope San Diego and the youth-focused work it does."
)

# Verified as of this writing — recheck periodically, hotline details can change.
CRISIS_REPLY = (
    "It sounds like this might be about something happening to you right now, "
    "not just a general question — and I want to make sure you get real help, "
    "not just a chatbot reply.\n\n"
    "• Call or text 988 (Suicide & Crisis Lifeline) if you're in crisis or thinking about suicide.\n"
    "• Call or text 1-800-RUNAWAY (1-800-786-2929) — National Runaway Safeline, "
    "free and confidential, 24/7, specifically for youth who are homeless, "
    "thinking about running away, or in an unsafe home situation.\n\n"
    "If you're in San Diego, your school counselor or 211 San Diego can also "
    "connect you with local shelters and resources. You deserve support — please reach out."
)

OFF_TOPIC_REPLY = (
    "I'm set up to help with questions about Building Hope San Diego and the "
    "youth-focused work we do, or to help you find your way around the site — "
    "I'm not able to help much beyond that. Is there something in that space "
    "I can help with?"
)

NAV_REPLIES = {
    "home": "Here's our homepage.",
    "about": "Here's our About page — our story and our team.",
    "issue": "Here's our page on the issue we're focused on, with our sourced research.",
    "events": "Here's our Events page — upcoming and past events.",
    "involved": "Here's our Get Involved page — volunteering, donating, and partnering.",
    "contact": "Here's our Contact page.",
}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    intent: str
    reply: str
    page: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    classification = classify_intent(req.message)
    intent = classification["intent"]
    page = classification.get("page")

    if intent == "crisis":
        return ChatResponse(intent=intent, reply=CRISIS_REPLY, page=None)

    if intent == "navigation":
        reply = NAV_REPLIES.get(page, "Here you go.")
        return ChatResponse(intent=intent, reply=reply, page=page)

    if intent == "off_topic":
        return ChatResponse(intent=intent, reply=OFF_TOPIC_REPLY, page=None)

    # informational -> retrieval-augmented generation
    chunks = get_relevant_chunks(req.message)
    if chunks:
        context = "\n\n".join(f"[Source: {c['source']}]\n{c['text']}" for c in chunks)
    else:
        context = "(No matching research found in the knowledge base.)"

    response = _client.messages.create(
        model=MODEL_NAME,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Research context:\n{context}\n\nQuestion: {req.message}",
            }
        ],
    )
    reply_text = "".join(block.text for block in response.content if block.type == "text")
    return ChatResponse(intent=intent, reply=reply_text or "I'm not sure how to answer that yet.", page=None)