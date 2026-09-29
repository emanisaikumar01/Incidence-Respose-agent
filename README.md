# Incident Response Agent (RecallOps)

## Problem
Engineers often spend valuable time investigating recurring incidents because the causes and successful fixes from previous incidents are difficult to find.

## Our solution
RecallOps is an AI-assisted incident response tool that uses Hindsight as a memory layer. It recalls relevant past incidents and their outcomes to help suggest troubleshooting steps for a new incident.

## How it works
1. An engineer submits incident details or logs.
2. The agent recalls similar incidents from Hindsight.
3. An LLM uses the current incident and relevant past cases to suggest possible causes and fixes.
4. The engineer reviews and tries the suggested fix.
5. The outcome is recorded so it can inform future incidents.

## Technology
- Python for the agent/backend
- Hindsight for incident memory
- Groq or another supported LLM provider
- A web UI (to be decided by the team)

## Project status
Under development for Hack With Hyderabad 3.0.

## Safety
The agent provides recommendations only. Engineers must review and approve operational changes; the agent does not automatically execute production fixes.

## Setup & run (demo)

```powershell
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 2. Start the FastAPI backend (port 8000)
python -m uvicorn Backend.main:app --host 127.0.0.1 --port 8000

# 3. In a second terminal, start the Django frontend (port 8001)
cd app
..\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001
```

Open http://127.0.0.1:8001 — FastAPI must be up **before** you analyze an incident.
API keys (`GROQ_API_KEY`, `HINDSIGHT_API_KEY`) live in `.env` (never commit it).

**Demo flow:** Dashboard → New Incident → Analyze (recalls Hindsight memories, then Groq drafts the recommendation) → Record Outcome (writes the verified fix back to Hindsight so future recalls get smarter).
