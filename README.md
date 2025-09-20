# Prototype « Tuteur IA » — FastAPI (backend) + React (frontend)

Un prototype clé-en-main qui guide les élèves par **indices** plutôt que de donner la solution. Il s’appuie sur une **surcouche pédagogique** côté serveur : paliers d’aide, limite de verbosité, garde-fous anti-solution, quotas par élève.

### 1) Backend
```bash
cd backend && uv run uvicorn main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

## notes pédagogiques
- **Historique tronqué** et **max tokens** courts → l’IA évite de « dérouler » la solution.
- **Paliers d’aide** exposés dans l’UI + consignes système dédiées.
- **Guardrails** post‑traitement qui transforment les gros blocs de code en pseudo‑code/étapes.
- **Quota par élève** configurable (remplacer la mémoire in‑memory par Redis en production).

