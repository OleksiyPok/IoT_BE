# BE/routes/sensors.py

from fastapi import APIRouter, Depends, HTTPException, status

import db

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"],
)


@router.get(
    "/latest",
    summary="Get latest sensor",
    description="Get latest sensor",
    status_code=status.HTTP_200_OK,
)
def sensors_latest():
    item = db.get_latest()
    if item is None:
        raise HTTPException(status_code=404, detail="No data yet")
    return item


@router.get(
    "/history",
    summary="Get latest sensor history",
    description="Get latest sensor history",
    status_code=status.HTTP_200_OK,
)
def sensors_history(from_ms: int, to_ms: int):
    return db.get_history(from_ms, to_ms)
