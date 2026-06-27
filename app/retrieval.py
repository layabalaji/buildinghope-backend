"""
Retrieval over your research documents.

This is a small TF-IDF retriever — no API key or GPU needed, good enough
to start with. Drop your research (txt or md files) into data/research/
and this will chunk + search them.

UPGRADE PATH: once you have more documents, swap this for embeddings
(e.g. sentence-transformers) and a cosine-similarity or vector-DB search —
the function signature below can stay the same so chat.py doesn't change.
"""

from __future__ import annotations

import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RESEARCH_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "research")


def _load_chunks() -> list[dict]:
    """Reads every .txt/.md file in data/research and splits into paragraph-sized chunks."""
    chunks = []
    if not os.path.isdir(RESEARCH_DIR):
        return chunks

    for filename in os.listdir(RESEARCH_DIR):
        if not filename.endswith((".txt", ".md")):
            continue
        path = os.path.join(RESEARCH_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        for i, paragraph in enumerate(p.strip() for p in text.split("\n\n")):
            if len(paragraph) > 30:  # skip near-empty fragments
                chunks.append({"source": filename, "chunk_id": i, "text": paragraph})
    return chunks


# Loaded once at startup. Restart the server after adding new research docs.
_CHUNKS = _load_chunks()
_VECTORIZER = TfidfVectorizer(stop_words="english") if _CHUNKS else None
_MATRIX = _VECTORIZER.fit_transform([c["text"] for c in _CHUNKS]) if _CHUNKS else None


def get_relevant_chunks(query: str, top_k: int = 3) -> list[dict]:
    """Returns the top_k most relevant chunks for a query, each with its source filename."""
    if not _CHUNKS or _VECTORIZER is None:
        return []

    query_vec = _VECTORIZER.transform([query])
    scores = cosine_similarity(query_vec, _MATRIX)[0]
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [_CHUNKS[i] for i in ranked[:top_k] if scores[i] > 0]