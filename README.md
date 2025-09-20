# Tuteur IA

guide les élèves par **indices** plutôt qu'en donnant la solution. 
le système s’appuie sur une **surcouche pédagogique** côté serveur : paliers d’aide, limite de verbosité, garde-fous anti-solution, quotas par élève.

techno: FastAPI (backend) + React (frontend)

**en phase de prototype**



### 1) Backend
```bash
cd backend
# installe les dépendances
uv sync
# lance le backend
uv run uvicorn main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
# installe les dépendances
npm install
# lance le frontend
npm run dev
```

## notes pédagogiques
- **Historique tronqué** et **max tokens** courts → l’IA évite de « dérouler » la solution.
- **Paliers d’aide** exposés dans l’UI + consignes système dédiées.
- **Guardrails** post‑traitement qui transforment les gros blocs de code en pseudo‑code/étapes.
- **Quota par élève** configurable (remplacer la mémoire in‑memory par Redis en production).


