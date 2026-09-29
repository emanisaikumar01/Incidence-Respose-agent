from memory.hindsight_memory import (
    recall_similar as hindsight_recall_similar,
    record_outcome as hindsight_record_outcome,
)


def recall_similar(incident_text: str) -> list[dict[str, str]]:
    """
    Retrieve relevant historical incidents from Hindsight.

    This keeps the agreed backend function signature:
        recall_similar(incident_text)

    The actual Hindsight implementation is located in:
        memory/hindsight_memory.py
    """
    return hindsight_recall_similar(incident_text)


def record_outcome(
    incident_id: str,
    fix: str,
    worked: bool,
    incident: dict | None = None,
):
    """
    Record the engineer-confirmed outcome in Hindsight.

    This keeps the agreed backend function signature:
        record_outcome(incident_id, fix, worked)

    The actual Hindsight implementation is located in:
        memory/hindsight_memory.py
    """
    return hindsight_record_outcome(
        incident_id,
        fix,
        worked,
        incident,
    )