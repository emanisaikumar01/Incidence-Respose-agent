
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from Backend.services.memory_service import (
    recall_similar,
    record_outcome,
)

from Backend.services.recommendation_service import (
    generate_recommendation,
)


# Persist incidents in a JSON file at the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INCIDENTS_FILE = PROJECT_ROOT / "data" / "incidents.json"

# Ensure the data directory exists.
INCIDENTS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_incidents() -> dict[str, dict[str, Any]]:
    """Load saved incidents from disk."""
    if not INCIDENTS_FILE.exists():
        return {}

    try:
        with INCIDENTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        # Don't silently overwrite a damaged file.
        raise RuntimeError(
            f"Could not read incident data from {INCIDENTS_FILE}"
        )


def _save_incidents() -> None:
    """Save all incidents to disk."""
    temporary_file = INCIDENTS_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(_incidents, file, indent=2, ensure_ascii=False)

    temporary_file.replace(INCIDENTS_FILE)


_incidents: dict[str, dict[str, Any]] = _load_incidents()


def create_incident(data: dict[str, Any]) -> dict[str, Any]:
    """Create and persist a new incident."""
    incident_id = f"INC-{uuid4().hex[:8].upper()}"

    incident = {
        "incident_id": incident_id,
        "title": data["title"],
        "description": data["description"],
        "service": data["service"],
        "severity": data["severity"],
        "logs": data.get("logs"),
        "environment": data.get("environment"),
        "deployment": data.get("deployment"),
        "status": "investigating",
    }

    _incidents[incident_id] = incident
    _save_incidents()

    return incident


def get_incident(incident_id: str) -> dict[str, Any] | None:
    """Get one incident by ID."""
    return _incidents.get(incident_id)


def list_incidents() -> list[dict[str, Any]]:
    """Return all saved incidents."""
    return list(_incidents.values())


def analyze_incident(incident_id: str) -> dict[str, Any]:
    """Recall historical cases and generate an AI recommendation."""
    incident = get_incident(incident_id)

    if incident is None:
        raise ValueError("Incident not found")

    # Show an "analyzing" badge while the AI call is in flight.
    incident["status"] = "analyzing"
    _save_incidents()

    def _restore_status() -> None:
        """Analysis is done (or failed) — the incident is back in the engineer's hands."""
        if incident.get("status") == "analyzing":
            incident["status"] = "investigating"
            _save_incidents()

    incident_text = (
        f"Title: {incident['title']}\n"
        f"Description: {incident['description']}\n"
        f"Service: {incident['service']}\n"
        f"Severity: {incident['severity']}\n"
        f"Logs: {incident.get('logs') or 'No logs provided'}"
    )

    try:
        recalled_cases = recall_similar(incident_text)
    except Exception as exc:
        _restore_status()
        return {
            "incident_id": incident_id,
            "status": "memory_error",
            "memory_status": "unavailable",
            "error": f"Hindsight retrieval failed: {exc}",
        }

    try:
        recommendation = generate_recommendation(
            incident=incident,
            recalled_cases=recalled_cases,
        )
    except Exception as exc:
        _restore_status()
        return {
            "incident_id": incident_id,
            "status": "llm_error",
            "memory_status": "found" if recalled_cases else "no_matches",
            "error": f"AI recommendation failed: {exc}",
        }

    _restore_status()

    return {
        "incident_id": incident_id,
        "incident": incident,
        "recalled_cases": recalled_cases,
        "recommendation": recommendation,
        # Flattened fields so the frontend template can render the
        # analysis result directly without digging into `recommendation`.
        **recommendation,
        "memory_status": (
            "found" if recalled_cases else "no_matches"
        ),
        "memory_used": bool(recalled_cases),
    }


def record_incident_outcome(
    incident_id: str,
    fix: str,
    worked: bool,
) -> dict[str, Any]:
    """Persist the engineer's verified outcome and record it in Hindsight."""
    incident = get_incident(incident_id)

    if incident is None:
        raise ValueError("Incident not found")

    incident["status"] = "resolved" if worked else "unresolved"
    incident["fix"] = fix
    incident["worked"] = worked

    # Save the incident outcome locally first.
    _save_incidents()

    try:
        memory_result = record_outcome(
            incident_id=incident_id,
            fix=fix,
            worked=worked,
            incident=incident,
        )
    except Exception as exc:
        return {
            "incident_id": incident_id,
            "status": "memory_error",
            "error": f"Outcome recording failed: {exc}",
        }

    return {
        "incident_id": incident_id,
        "status": incident["status"],
        "fix": fix,
        "worked": worked,
        "memory": memory_result,
    }
