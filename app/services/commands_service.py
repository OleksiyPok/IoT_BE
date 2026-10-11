# app/services/commands_service.py

import json
import os

import boto3
from dotenv import load_dotenv

load_dotenv()

IOT_USER = os.getenv("IOT_USER")
if not IOT_USER:
    raise ValueError("IOT_USER is not set in the .env file")

TOPIC_CMD = f"iot-course/{IOT_USER}/commands/led"

iot = boto3.client("iot-data")


def publish_led_command(value: str):
    """Publish an LED command to AWS IoT Core."""
    payload = json.dumps(
        {"action": "set", "value": value},
        separators=(",", ":"),
    )
    iot.publish(topic=TOPIC_CMD, qos=1, payload=payload)
