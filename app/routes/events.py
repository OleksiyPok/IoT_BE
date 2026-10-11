# app/routes/events.py
import time

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, HTTPException, Query, status

from app.services.events_service import (
    get_event_history,
    get_latest_event,
    get_recent_events,
)

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get(
    "/latest",
    summary="Get the latest event",
    description="Retrieve the single most recent event.",
    status_code=status.HTTP_200_OK,
)
def get_latest_event_route():
    try:
        item = get_latest_event()
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve event data from AWS",
        )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No event found",
        )

    return item


@router.get(
    "/last-hours",
    summary="Get events from the last hours",
    description="Retrieve events from the specified number of past hours.",
    status_code=status.HTTP_200_OK,
)
def get_events_last_hours(
    hours: int = Query(gt=0, le=24),
):
    now_ms = int(time.time() * 1000)
    from_ms = now_ms - hours * 60 * 60 * 1000

    try:
        return get_event_history(from_ms, now_ms)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve event history from AWS",
        )


@router.get(
    "/last-count",
    summary="Get the last events",
    description="Retrieve the specified number of most recent events.",
    status_code=status.HTTP_200_OK,
)
def get_events_last_count(
    count: int = Query(ge=1),
):
    try:
        return get_recent_events(count)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve event history from AWS",
        )


@router.get(
    "/history",
    summary="Get event history",
    description="Retrieve events within the specified time range.",
    status_code=status.HTTP_200_OK,
)
def get_event_history_route(
    from_ms: int = Query(ge=0),
    to_ms: int = Query(ge=0),
):
    if from_ms > to_ms:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_ms must be less than or equal to to_ms",
        )

    try:
        return get_event_history(from_ms, to_ms)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve event history from AWS",
        )