import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io"
)

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

BANK_ID = "nexora-incidents"

if not HINDSIGHT_API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is not set in .env")

client = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY
)


def initialize_memory():
    """Create the incident memory bank if it does not already exist."""
    try:
        client.create_bank(
            bank_id=BANK_ID,
            name="Nexora Incident Memory"
        )
        return True
    except Exception as e:
        # Bank may already exist.
        if "already exists" in str(e).lower():
            return True
        raise


def retain_incident(incident):
    """
    Store a completed incident in Hindsight.

    Expected incident fields:
    incident_id, service, symptom, logs,
    root_cause, fix_tried, outcome
    """

    content = f"""
Incident ID: {incident.get("incident_id")}

Service: {incident.get("service")}

Symptom:
{incident.get("symptom")}

Logs:
{incident.get("logs")}

Root Cause:
{incident.get("root_cause")}

Fix Tried:
{incident.get("fix_tried")}

Outcome:
{incident.get("outcome")}
"""

    return client.retain(
        bank_id=BANK_ID,
        content=content,
        context="production incident response"
    )


def recall_similar(incident_text):
    """
    Recall relevant past incidents from Hindsight.

    Returns a list of PastCase dictionaries.
    """

    result = client.recall(
        bank_id=BANK_ID,
        query=f"""
Find previous production incidents relevant to this incident.

Current incident:
{incident_text}

Return only genuinely relevant past incidents.
Do not invent incidents.
"""
    )

    past_cases = []

    for memory in result.results:
        past_cases.append({
            "memory_id": getattr(memory, "id", None),
            "text": memory.text
        })

    return past_cases


def record_outcome(incident_id, fix, worked, incident=None):
    """
    Record the engineer-confirmed outcome of an incident.

    If the incident dict is provided, its title/service/description/logs are
    stored together with the outcome. Without that context the memory would
    only say "INC-123: fix X, resolved" and could never match a future
    incident by symptom.
    """

    outcome = "resolved" if worked else "unresolved"
    incident = incident or {}

    content = f"""
Incident outcome record

Incident ID: {incident_id}

Title: {incident.get("title", "")}

Service: {incident.get("service", "")}

Severity: {incident.get("severity", "")}

Symptom:
{incident.get("description", "")}

Logs:
{incident.get("logs") or ""}

Fix tried:
{fix}

Engineer-confirmed outcome:
{outcome}
"""

    return client.retain(
        bank_id=BANK_ID,
        content=content,
        context="engineer-confirmed incident outcome"
    )
