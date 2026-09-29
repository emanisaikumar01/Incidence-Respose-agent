from django.shortcuts import render, redirect

from .services import (
    BackendError,
    get_dashboard_summary,
    get_incidents,
    get_incident,
    create_incident,
    analyze_incident as backend_analyze_incident,
    resolve_incident as backend_resolve_incident,
    search_memory,
)



def _normalize_analysis(result):
    """
    Flatten the backend /analyze response into what the templates expect.

    Backend success shape:
        {incident_id, incident, recalled_cases: [...], recommendation: {...}}
    Backend failure shape (HTTP 200!):
        {incident_id, status: "memory_error" | "llm_error", error: "..."}
    """
    status = result.get("status")
    if status in ("memory_error", "llm_error") or result.get("error"):
        return None, result.get("error") or "Analysis failed."

    rec = result.get("recommendation") or {}
    if not rec:
        return None, "Backend returned no recommendation."

    recalled = result.get("recalled_cases") or []

    analysis = {
        "summary": rec.get("summary", ""),
        "possible_cause": rec.get("possible_cause") or rec.get("root_cause", ""),
        "evidence": rec.get("evidence") or [],
        "similar_incidents": rec.get("similar_incidents", ""),
        "recommended_action": rec.get("recommended_action", ""),
        "recommended_steps": rec.get("recommended_steps") or [],
        "prevention": rec.get("prevention", ""),
        "confidence": rec.get("confidence", ""),
        "memory_status": "found" if recalled else "no_matches",
        "memory_used": bool(recalled),
    }
    return analysis, None


def dashboard(request):
    try:
        incidents = get_incidents()

        if not isinstance(incidents, list):
            incidents = []

        statuses = [
            str(incident.get("status", "")).lower()
            for incident in incidents
        ]

        summary = {
            "total": len(incidents),
            # "open" = anything not yet resolved or marked unresolved.
            "open": sum(
                status not in ("resolved", "unresolved")
                for status in statuses
            ),
            "analyzing": statuses.count("analyzing"),
            "resolved": statuses.count("resolved"),
        }

        return render(
            request,
            "dashboard/index.html",
            {
                "summary": summary,
                "incidents": incidents,
            },
        )

    except BackendError as exc:
        return render(
            request,
            "dashboard/index.html",
            {
                "summary": {
                    "total": 0,
                    "open": 0,
                    "analyzing": 0,
                    "resolved": 0,
                },
                "incidents": [],
                "error": str(exc),
            },
        )



def new_incident(request):
    if request.method == "GET":
        return render(
            request,
            "incidents/new.html",
        )

    payload = {
        "title": request.POST.get("title", "").strip(),
        "service": request.POST.get("service", "").strip(),
        # Backend and templates expect these as free-form text.
        "environment": request.POST.get(
            "environment",
            "production",
        ).strip() or "production",
        "severity": request.POST.get(
            "severity",
            "medium",
        ),
        "deployment": request.POST.get(
            "deployment",
            "",
        ).strip(),
        "logs": request.POST.get(
            "logs",
            "",
        ).strip(),
        "description": request.POST.get("logs", "").strip(),
    }

    if not payload["title"]:
        return render(
            request,
            "incidents/partials/incident_result.html",
            {
                "error": "Incident title is required."
            },
        )

    if not payload["logs"]:
        return render(
            request,
            "incidents/partials/incident_result.html",
            {
                "error": "Please provide incident logs or details."
            },
        )

    try:
        result = create_incident(payload)
    except BackendError as exc:
        return render(
            request,
            "incidents/partials/incident_result.html",
            {
                "error": str(exc)
            },
        )

    if request.headers.get("HX-Request"):
        return render(
            request,
            "incidents/partials/incident_result.html",
            {
                "incident": result,
            },
        )

    incident_id = result.get("incident_id")

    return redirect(
        "incident_detail",
        incident_id=incident_id,
    )


def incident_detail(request, incident_id):
    try:
        incident = get_incident(incident_id)
    except BackendError as exc:
        return render(
            request,
            "incidents/detail.html",
            {
                "error": str(exc),
                "incident_id": incident_id,
            },
        )

    return render(
        request,
        "incidents/detail.html",
        {
            "incident": incident,
        },
    )


def analyze_incident(request, incident_id):
    if request.method != "POST":
        return redirect("incident_detail", incident_id=incident_id)

    try:
        result = backend_analyze_incident(incident_id)
    except BackendError as exc:
        return render(
            request,
            "incidents/partials/analysis_result.html",
            {"error": str(exc)},
        )
    except Exception as exc:
        return render(
            request,
            "incidents/partials/analysis_result.html",
            {"error": f"Unexpected frontend error: {exc}"},
        )

    if not isinstance(result, dict):
        return render(
            request,
            "incidents/partials/analysis_result.html",
            {"error": "Backend returned an invalid analysis response."},
        )

    analysis, error = _normalize_analysis(result)

    if error:
        return render(
            request,
            "incidents/partials/analysis_result.html",
            {"error": error, "memory_failed": result.get("status") == "memory_error"},
        )

    return render(
        request,
        "incidents/partials/analysis_result.html",
        {
            "analysis": analysis,
            "memories": result.get("recalled_cases") or [],
        },
    )


def resolve_incident(request, incident_id):
    if request.method != "POST":
        return redirect(
            "incident_detail",
            incident_id=incident_id,
        )

    fix = request.POST.get(
        "fix",
        "",
    ).strip()

    worked = request.POST.get(
        "worked",
        "",
    )

    if not fix:
        return render(
            request,
            "incidents/partials/resolution_card.html",
            {
                "error": "Please describe the fix you attempted."
            },
        )

    worked_bool = worked == "true"

    try:
        result = backend_resolve_incident(
            incident_id,
            fix,
            worked_bool,
        )
    except BackendError as exc:
        return render(
            request,
            "incidents/partials/resolution_card.html",
            {
                "error": str(exc),
            },
        )

    return render(
        request,
        "incidents/partials/resolution_card.html",
        {
            "resolution": result,
        },
    )


def incident_history(request):
    try:
        incidents = get_incidents()
    except BackendError as exc:
        return render(
            request,
            "incidents/history.html",
            {
                "incidents": [],
                "error": str(exc),
            },
        )

    return render(
        request,
        "incidents/history.html",
        {
            "incidents": incidents,
        },
    )


def memory_explorer(request):
    return render(
        request,
        "memory/explorer.html",
    )


def memory_search(request):
    query = request.GET.get(
        "q",
        "",
    ).strip()

    if not query:
        return render(
            request,
            "memory/partials/memory_results.html",
            {
                "memories": [],
            },
        )

    try:
        result = search_memory(query)
    except BackendError as exc:
        return render(
            request,
            "memory/partials/memory_results.html",
            {
                "error": str(exc),
                "memories": [],
            },
        )

    memories = result.get(
        "memories",
        result.get(
            "results",
            [],
        ),
    )

    return render(
        request,
        "memory/partials/memory_results.html",
        {
            "memories": memories,
            "query": query,
        },
    )