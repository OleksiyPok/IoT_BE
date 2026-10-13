# app/routes/sensors.py

import time

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, HTTPException, Query, status

from app.services.telemetry_service import (
    get_latest_sensor,
    get_recent_sensors,
    get_sensor_history,
)

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"],
)


@router.get(
    "/latest",
    summary="Get the latest sensor reading",
    description="Retrieve the single most recent sensor reading.",
    status_code=status.HTTP_200_OK,
)
def get_latest_sensor_route():
    try:
        item = get_latest_sensor()
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
    "/last-hours",
    summary="Get sensor readings from the last hours",
    description="Retrieve sensor readings from the specified number of past hours.",
    status_code=status.HTTP_200_OK,
)
def get_sensor_readings_last_hours(
    hours: int = Query(gt=0, le=24),
):
    now_ms = int(time.time() * 1000)
    from_ms = now_ms - hours * 60 * 60 * 1000

    try:
        return get_sensor_history(from_ms, now_ms)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve sensor history from AWS",
        )


@router.get(
    "/last-count",
    summary="Get the last sensor readings",
    description="Retrieve the specified number of most recent sensor readings.",
    status_code=status.HTTP_200_OK,
)
def get_sensor_readings_last_count(
    count: int = Query(ge=1),
):
    try:
        return get_recent_sensors(count)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve sensor data from AWS",
        )


@router.get(
    "/history",
    summary="Get sensor reading history",
    description="Retrieve sensor readings within the specified time range.",
    status_code=status.HTTP_200_OK,
)
def get_sensor_history_route(
    from_ms: int = Query(ge=0),
    to_ms: int = Query(ge=0),
):
    if from_ms > to_ms:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_ms must be less than or equal to to_ms",
        )

    try:
        return get_sensor_history(from_ms, to_ms)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve sensor history from AWS",

        )
