# app/routes/sensors.py

import time

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, HTTPException, Query, status

from app.services.telemetry_service import get_history, get_latest

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"],
)


@router.get(
    "/latest",
    summary="Get latest sensor reading",
    description="Retrieve the most recent sensor reading.",
    status_code=status.HTTP_200_OK,
)
def sensors_latest():
    try:
        item = get_latest()
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve sensor data from AWS",
        )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sensor data found",
        )

    return item


@router.get(
    "/history",
    summary="Get sensor reading history",
    description="Retrieve sensor readings within the specified time range.",
    status_code=status.HTTP_200_OK,
)
def sensors_history(
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
            detail="Failed to retrieve sensor data from AWS",
        )


@router.get(
    "/history/hours",
    summary="Get sensor readings for the last N hours",
    description="Retrieve sensor readings from the specified number of past hours.",
    status_code=status.HTTP_200_OK,
)
def sensors_history_hours(
    hours: int = Query(gt=0),
):
    now_ms = int(time.time() * 1000)
    from_ms = now_ms - hours * 60 * 60 * 1000

    try:
        return get_history(from_ms, now_ms)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve sensor data from AWS",
        )
