# Venkata Portfolio

This repository contains multiple end-to-end projects, system design notes, and demos focused on backend engineering, cloud-native platforms, and AI integrations.

Key directories:

- `Projects/` — Complete projects and demos (each project has its own README). Examples:
  - `Projects/llm-dispute-resolution` — Dispute resolution MVP and extended system design.
  - `Projects/llm-fraud-detection` — Fraud detection demos.
  - `Projects/multi-agent-customer-support` — Multi-agent orchestration demo.
- `SYSTEM_DESIGNS/` — Architecture documents and case studies.
- `BLOG/` — Notes and blog drafts.

Quick links:

- Root README for each project lives under `Projects/<project-name>/README.md`.
- License: [LICENSE](LICENSE)

---

## Quick Start — Local Backend Demo (llm-dispute-resolution)

This repository includes a lightweight MVP for dispute classification under `Projects/llm-dispute-resolution`.

1. Open a terminal in the project folder:

```powershell
cd e:\Desktop\GitHub\VenkataPortfolio\Projects\llm-dispute-resolution
```

2. Create and activate a virtual environment (Windows example):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run the backend locally:

```powershell
uvicorn app.main:app --reload
```

5. Open the API docs in your browser:

http://127.0.0.1:8000/docs

Use header `x-api-key: changeme` when calling protected endpoints in this demo.

---

## Example API calls (llm-dispute-resolution)

Create and classify a dispute (example using curl):

```powershell
curl -X POST "http://127.0.0.1:8000/disputes/classify" \
  -H "Content-Type: application/json" \
  -H "x-api-key: changeme" \
  -d '{"narrative": "I did not authorize this transaction."}'
```

Batch classify:

```powershell
curl -X POST "http://127.0.0.1:8000/disputes/classify/batch" \
  -H "Content-Type: application/json" \
  -H "x-api-key: changeme" \
  -d '{"narratives": ["Unauthorized charge", "Legitimate purchase"]}'
```

Retrain model (small example):

```powershell
curl -X POST "http://127.0.0.1:8000/disputes/retrain" \
  -H "Content-Type: application/json" \
  -H "x-api-key: changeme" \
  -d '{"texts": ["fraudulent purchase", "normal purchase"], "labels": [1,0]}'
```

Model health:

```powershell
curl "http://127.0.0.1:8000/disputes/model/health" -H "x-api-key: changeme"
```

---

## Developer checklist (recommended)

- Create a Python virtualenv and activate it.
- Install dependencies from the project `requirements.txt` file.
- Run the backend via `uvicorn app.main:app --reload` and test endpoints via `/docs`.
- To add a frontend, create a `frontend/` folder and scaffold a Vite + React app; point API calls to `http://127.0.0.1:8000`.

---

---

## Projects Index (high level)

- `Projects/llm-dispute-resolution` — Dispute classification MVP and extended design docs.
- `Projects/llm-fraud-detection` — Fraud detection experiments.
- `Projects/llm-predictive-maintenance` — Predictive maintenance examples.
- `Projects/multi-agent-customer-support` — Chat / agent coordination demos.
- `Projects/rag-knowledge-retrieval` — Retrieval-augmented generation examples.

---

## Recommendations

- Each project folder contains a dedicated `README.md` — open it for project-specific setup, architecture notes, and run instructions.
- For demos, prefer local runs using the included `requirements.txt` and the FastAPI Swagger UI (`/docs`).

---

## License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
