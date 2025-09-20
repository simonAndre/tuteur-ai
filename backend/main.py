from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import os
import re

from guardrails import sanitize_and_demote_solutions
from adapters.openai_adapter import llm_answer

app = FastAPI(title="Tuteur IA — API")

# CORS (à adapter au domaine du front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mémoire in‑memory très simple pour quotas (à remplacer par Redis ou postgre en prod)
WINDOW = timedelta(hours=2)
QUOTA_PER_USER = int(os.getenv("QUOTA_PER_USER", "12"))  # requêtes max par fenêtre
USAGE = {}  # dict[user_id] = list[datetime]

SYSTEM_PROMPT = (
    "Tu es un tuteur pédagogique. Tu ne donnes JAMAIS la solution complète. "
    "Tu poses des questions de relance, fournis des indices progressifs et des pistes de méthode. "
    "Style: concis, 3 à 5 phrases max puis 1 question. "
    "Si l'élève insiste pour la solution, rappelle le cadre."
)

LEVEL_PROMPTS = {
    1: "Niveau d'aide 1 (très léger) : reformule l'énoncé, propose une piste très générale.",
    2: "Niveau d'aide 2 (méthode) : propose une démarche, cite une notion à revoir.",
    3: "Niveau d'aide 3 (diagnostic) : pointe une erreur prob. ou un test à faire, sans donner de code final.",
}

class Message(BaseModel):
    role: str
    content: str

class AskPayload(BaseModel):
    user_id: str = Field(..., description="Identifiant élève (anonyme ou compte ENT)")
    level: int = Field(2, ge=1, le=3, description="Palier d'indice 1..3")
    messages: List[Message] = Field(..., description="Historique court: alternance user/assistant")

class AskResponse(BaseModel):
    answer: str
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    model: Optional[str] = None


def check_quota(user_id: str):
    now = datetime.utcnow()
    window_start = now - WINDOW
    if user_id not in USAGE:
        USAGE[user_id] = []
    USAGE[user_id] = [t for t in USAGE[user_id] if t >= window_start]
    if len(USAGE[user_id]) >= QUOTA_PER_USER:
        raise HTTPException(status_code=429, detail="Quota atteint. Demande un nouvel indice au prof.")
    USAGE[user_id].append(now)

@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskPayload, request: Request):
    # Quota par élève
    check_quota(payload.user_id)

    # Tronquer l'historique au dernier échange user (on évite que le modèle recompose la solution)
    short_history = payload.messages[-4:]

    # Construire le système + consigne de niveau
    system = SYSTEM_PROMPT + "\n" + LEVEL_PROMPTS.get(payload.level, LEVEL_PROMPTS[2])

    # Limiter la verbosité avec une instruction claire
    behavior = (
        "Réponds en 3–5 phrases maximum, puis ajoute 1 question de relance. "
        "N'inclus PAS de blocs de code complets (>6 lignes)."
    )

    # Appel LLM via l'adapter (OpenAI par défaut)
    raw_answer, usage, model = await llm_answer(system=system, messages=short_history, behavior=behavior)

    # Garde‑fous anti-solution trop directe
    safe_answer = sanitize_and_demote_solutions(raw_answer, level=payload.level)

    return AskResponse(
        answer=safe_answer,
        tokens_in=usage.get("input", None),
        tokens_out=usage.get("output", None),
        model=model,
    )

@app.get("/health")
async def health():
    return {"ok": True}