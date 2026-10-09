# BE/db.py

import os
import time

import boto3
from boto3.dynamodb.conditions import Key

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_DEFAULT_REGION"))

TABLE_NAME = os.getenv("TABLE_NAME")
DEVICE_ID = os.getenv("DEVICE_ID")

table = dynamodb.Table(TABLE_NAME)


def get_latest():
    """Latest measurements"""
    response = table.query(
        KeyConditionExpression=Key("device_id").eq(DEVICE_ID),
        ScanIndexForward=False,
        Limit=1,
    )
    items = response["Items"]
    return items[0] if items else None


def get_history(from_ms, to_ms):
    """Measurements for the selected period"""
    response = table.query(
        KeyConditionExpression=Key("device_id").eq(DEVICE_ID)
        & Key("received_at").between(from_ms, to_ms),
    )
    return response["Items"]
