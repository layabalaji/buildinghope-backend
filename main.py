"""
Building Hope San Diego — backend entry point.

Run locally with:
    uvicorn main:app --reload --port 8000
"""

from dotenv import load_dotenv
load_dotenv()  # must run before any app.* imports — app/auth.py reads
               # ADMIN_USERNAME/ADMIN_PASSWORD_HASH from the environment
               # the moment it's imported, not when it's actually used

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import chat, auth, contact, messages

app = FastAPI(title="Building Hope San Diego API")

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(contact.router)
app.include_router(messages.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "building-hope-sd-backend"}