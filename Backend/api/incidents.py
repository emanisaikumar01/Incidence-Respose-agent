from fastapi import APIRouter, HTTPException

from Backend.models.incident import IncidentCreate
from Backend.models.outcome import OutcomeCreate

from Backend.services.incident_service import (
    create_incident,
    get_incident,
    list_incidents,
    analyze_incident,
    record_incident_outcome,
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


@router.post("/")
def create_new_incident(
    incident: IncidentCreate,
):
    return create_incident(
        incident.model_dump()
    )


@router.get("/")
def get_all_incidents():
    return list_incidents()


@router.get("/{incident_id}")
def get_single_incident(
    incident_id: str,
):
    incident = get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.post("/{incident_id}/analyze")
def analyze_existing_incident(
    incident_id: str,
):
    try:
        return analyze_incident(
            incident_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/{incident_id}/outcome")
def submit_incident_outcome(
    incident_id: str,
    outcome: OutcomeCreate,
):
    try:
        return record_incident_outcome(
            incident_id=incident_id,
            fix=outcome.fix,
            worked=outcome.worked,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )