# BE/routes/tests.py

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/test",
    tags=["Tests"],
)


@router.get(
    "/health",
    summary="Health Check",
    description="Health Check",
    status_code=status.HTTP_200_OK,
)
def health():
    return {"status": "ok"}
