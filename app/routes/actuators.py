# app/routes/actuators.py

from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from botocore.exceptions import BotoCoreError, ClientError

from app.services.commands_service import send_led_command


class LedCommand(BaseModel):
    value: Literal["on", "off", "toggle"] = Field(
        json_schema_extra={"examples": ["toggle"]}
    )


router = APIRouter(
    prefix="/actuators",
    tags=["Actuators"],
)


@router.post(
    "/led",
    summary="Send LED command",
    description="Publish a command to change the LED state.",
    status_code=status.HTTP_202_ACCEPTED,
)
def set_led(cmd: LedCommand):
    try:
        send_led_command(cmd.value)
    except (BotoCoreError, ClientError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to publish LED command to AWS IoT Core",
        )

    return {"accepted": True, "value": cmd.value}
