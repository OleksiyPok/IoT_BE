# BE/routes/sensors.py

from fastapi import APIRouter, HTTPException, status

import db

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
    item = db.get_latest()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data yet")
    return item


@router.get(
    "/history",
    summary="Get sensor reading history",
    description="Retrieve historical sensor readings.",
    status_code=status.HTTP_200_OK,
)
def sensors_history(from_ms: int, to_ms: int):
    return db.get_history(from_ms, to_ms)
