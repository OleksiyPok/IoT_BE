# app/routes/sensors.py

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, HTTPException, Query, status

from app.services.telemetry_service import get_history, get_latest

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"],
)


@router.get(
    "/latest",
    summary="Get latest sensor readings",
    description="Retrieve the most recent sensor readings.",
    status_code=status.HTTP_200_OK,
)
def sensors_latest():
    try:
        item = get_latest()
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve sensor readings from AWS",
        )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data yet",
        )

    return item


@router.get(
    "/history",
    summary="Get sensor reading history",
    description="Retrieve historical sensor readings.",
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
            detail="Failed to retrieve sensor history from AWS",
        )
