# app/routes/events.py

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, HTTPException, Query, status

from app.services.events_service import get_history, get_latest, get_n_records

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get(
    "/latest",
    summary="Get latest event",
    description="Retrieve the most recent event.",
    status_code=status.HTTP_200_OK,
)
def events_latest():
    try:
        item = get_latest()
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve event data from AWS",
        )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No events found",
        )

    return item


@router.get(
    "/history",
    summary="Get event history",
    description="Retrieve events within the specified time range.",
    status_code=status.HTTP_200_OK,
)
def events_history(
    from_ms: int = Query(ge=0),
    to_ms: int = Query(ge=0),
):
    if from_ms > to_ms:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_ms must be less than or equal to to_ms",
        )

    try:
        return get_history(from_ms, to_ms)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve event history from AWS",
        )


@router.get(
    "/history/recent",
    summary="Get latest N events",
    description="Retrieve the specified number of most recent events.",
    status_code=status.HTTP_200_OK,
)
def events_n_history(
    n_events: int = Query(ge=1),
):
    try:
        return get_n_records(n_events)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve events history from AWS",
        )
