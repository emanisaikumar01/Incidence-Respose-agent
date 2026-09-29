
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path(
        "incidents/new/",
        views.new_incident,
        name="new_incident",
    ),

    # Keep History BEFORE the dynamic incident-detail route.
    path(
        "incidents/history/",
        views.incident_history,
        name="incident_history",
    ),

    path(
        "incidents/<str:incident_id>/",
        views.incident_detail,
        name="incident_detail",
    ),

    path(
        "incidents/<str:incident_id>/analyze/",
        views.analyze_incident,
        name="analyze_incident",
    ),

    path(
        "incidents/<str:incident_id>/resolve/",
        views.resolve_incident,
        name="resolve_incident",
    ),

    path(
        "memory/",
        views.memory_explorer,
        name="memory_explorer",
    ),

    path(
        "memory/search/",
        views.memory_search,
        name="memory_search",
    ),
]
