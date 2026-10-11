# app/router.py

from fastapi import APIRouter

from app.routes.actuators import router as actuators_router
from app.routes.events import router as events_router
from app.routes.sensors import router as telemetry_router
from app.routes.tests import router as test_router

router = APIRouter()

router.include_router(telemetry_router)
router.include_router(actuators_router)
router.include_router(events_router)
router.include_router(test_router)
