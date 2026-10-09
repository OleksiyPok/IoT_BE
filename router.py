# BE/router.py

from fastapi import APIRouter

from routes.actuators import router as actuators_router
from routes.sensors import router as telemetry_router
from routes.tests import router as test_router

router = APIRouter()

router.include_router(telemetry_router)
router.include_router(actuators_router)
router.include_router(test_router)
