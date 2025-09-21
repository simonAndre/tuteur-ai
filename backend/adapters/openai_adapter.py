import os
import httpx
from dotenv import load_dotenv

# Implémentation asynchrone minimaliste s’appuyant sur la **Responses API** d’OpenAI 
# Renseigner `OPENAI_API_KEY` dans `.env`.

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}

async def llm_answer(system: str, messages, behavior: str):
    if not OPENAI_API_KEY:
        # Fallback pour dev hors‑ligne
        dummy = (
            "Indice: relis l'énoncé et isole les entrées/sorties. "
            "Propose une structure en 2–3 fonctions. Quels tests écrirais‑tu ?"
        )
        return dummy, {"input": 0, "output": len(dummy.split())}, "dummy"

    # Construire le format messages (system + history + instruction comportement)
    chat = [{"role": "system", "content": system + "\n" + behavior}] + [m.dict() for m in messages]

    payload = {
        "model": OPENAI_MODEL,
        "input": chat,  # Responses API accepte "input" messages
        "max_output_tokens": int(os.getenv("MAX_OUTPUT_TOKENS", "220")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{OPENAI_BASE_URL}/responses", headers=HEADERS, json=payload)
        r.raise_for_status()
        data = r.json()

    # Extraire le texte (compat Responses API)
    # data["output"][0]["content"][0]["text"] selon le schéma courant
    try:
        segments = data.get("output", [])
        first = segments[0]
        content = first.get("content", [])
        text = "".join([c.get("text", "") for c in content if c.get("type") == "output_text"])
        usage = data.get("usage", {}).get("total_tokens", {})
        model = data.get("model", OPENAI_MODEL)
    except Exception:
        # Fallback plus compat avec Chat Completions si proxy
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "(réponse vide)")
        usage = data.get("usage", {})
        model = data.get("model", OPENAI_MODEL)

    # Normaliser la forme d'usage
    if isinstance(usage, dict):
        usage_norm = {
            "input": usage.get("input_tokens") or usage.get("prompt_tokens") or 0,
            "output": usage.get("output_tokens") or usage.get("completion_tokens") or 0,
        }
    else:
        usage_norm = {"input": 0, "output": 0}

    return text, usage_norm, model