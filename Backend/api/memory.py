from fastapi import APIRouter, HTTPException, Query

from Backend.services.memory_service import recall_similar


router = APIRouter(
    prefix="/api/memory",
    tags=["Memory"],
)


@router.get("/search")
def search_memory(
    q: str = Query(..., min_length=1),
):
    """Search the Hindsight memory bank from the Memory Explorer page."""
    try:
        memories = recall_similar(q)
    except Exception as exc:
        # Hindsight may be briefly unavailable — don't 500 the dashboard.
        raise HTTPException(
            status_code=503,
            detail=f"Memory service unavailable: {exc}",
        )

    return {"memories": memories}
