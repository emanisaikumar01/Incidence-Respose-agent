import os
import httpx

from django.conf import settings


BASE_URL = getattr(
    settings,
    "FASTAPI_BASE_URL",
    os.getenv(
        "FASTAPI_BASE_URL",
        "http://127.0.0.1:8001",
    ),
)


class BackendError(Exception):
    pass


def _request(method, path, **kwargs):
    url = f"{BASE_URL}{path}"

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.request(
                method,
                url,
                **kwargs,
            )

        if response.status_code >= 400:
            try:
                data = response.json()
                message = data.get(
                    "detail",
                    "Backend request failed."
                )
            except Exception:
                message = response.text

            raise BackendError(str(message))

        return response.json()

    except httpx.RequestError as exc:
        raise BackendError(
            f"Backend unavailable at {BASE_URL}: {type(exc).__name__} {exc}"
        ) from exc


def get_dashboard_summary():
    return _request(
        "GET",
        "/api/dashboard/summary",
    )


def get_incidents():
    return _request(
        "GET",
        "/api/incidents/",
    )


def get_incident(incident_id):
    return _request(
        "GET",
        f"/api/incidents/{incident_id}",
    )


def create_incident(payload):
    return _request(
        "POST",
        "/api/incidents/",
        json=payload,
    )


def analyze_incident(incident_id):
    return _request(
        "POST",
        f"/api/incidents/{incident_id}/analyze",
    )


def resolve_incident(
    incident_id,
    fix,
    worked,
):
    return _request(
        "POST",
        f"/api/incidents/{incident_id}/outcome",
        json={
            "fix": fix,
            "worked": worked,
        },
    )


def search_memory(query):
    return _request(
        "GET",
        "/api/memory/search",
        params={
            "q": query,
        },
    )