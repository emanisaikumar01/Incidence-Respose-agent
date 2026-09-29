from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    service: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    logs: str | None = None
    environment: str | None = None
    deployment: str | None = None


class IncidentResponse(BaseModel):
    incident_id: str
    title: str
    description: str
    service: str
    severity: str
    logs: str | None = None
    environment: str | None = None
    deployment: str | None = None
    status: str