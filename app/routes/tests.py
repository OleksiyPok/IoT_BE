# app/routes/tests.py

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/test",
    tags=["Tests"],
)


@router.get(
    "/health",
    summary="Check service health",
    description="Check whether the API service is operational.",
    status_code=status.HTTP_200_OK,
)
def health():
    return {"status": "ok"}
