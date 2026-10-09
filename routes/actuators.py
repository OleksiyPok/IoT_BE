# BE/routes/actuators.py

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from iot_client import send_led_command


class LedCommand(BaseModel):
    value: Literal["on", "off"]


router = APIRouter(
    prefix="/actuators",
    tags=["Actuators"],
)


@router.post(
    "/led",
    summary="Send LED command",
    description="Send LED command",
    status_code=202,
)
def set_led(cmd: LedCommand):
    try:
        send_led_command(cmd.value)
    except Exception:
        raise HTTPException(502, "AWS IoT unavailable")

    return {"accepted": True, "value": cmd.value}
