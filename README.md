# IoT Backend

A small FastAPI service for reading ESP32 sensor telemetry from Amazon DynamoDB and sending LED commands through AWS IoT Core.

## 1. Requirements

- Python 3.10 or newer
- An AWS account with the resources listed below
- AWS credentials authorized to access those resources

## 2. Run locally

Run these commands from the backend project directory (the directory containing `requirements.txt`):

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
python -m pip install fastapi uvicorn boto3 python-dotenv
```

Create a local `.env` file by copying `.env.example`, then fill in the required values. Do not commit `.env` or real credentials to source control.

Start the API:
```bash
uvicorn app.main:app --reload
```

Local URLs:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json
- Health check: http://127.0.0.1:8000/test/health

A successful health check returns `{"status":"ok"}`. This endpoint checks that the API process is running; it does not verify AWS access.

## 3. Environment variables and credentials

Copy `.env.example` to `.env` and configure:

| Variable | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key ID for the local development/test identity, if using static credentials |
| `AWS_SECRET_ACCESS_KEY` | Secret key for that identity; keep it private |
| `AWS_DEFAULT_REGION` | AWS region containing the resources; the example uses `eu-central-1` |
| `TABLE_NAME` | DynamoDB table name, e.g. `iot_telemetry` |
| `DEVICE_ID` | Device identifier used to filter telemetry, e.g. `esp32_7898` |
| `IOT_USER` | AWS IoT topic user segment; set to `OleksiiPok` for the current device/topic |

Example `.env`:
```dotenv
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=eu-central-1
TABLE_NAME=iot_telemetry
DEVICE_ID=esp32_7898
IOT_USER=OleksiiPok
```

Use a dedicated, least-privilege IAM identity for local development. On AWS-hosted compute, prefer an IAM role instead of long-lived access keys. If credentials are supplied through an AWS profile or role, configure that identity using the standard AWS credential chain.

The LED command topic is built in `app/services/commands_service.py` from `IOT_USER`:

```python
TOPIC_CMD = "iot-course/{IOT_USER}/commands/led"
```

With `IOT_USER=OleksiiPok`, the resulting topic is:
```text
iot-course/OleksiiPok/commands/led
```

The `IOT_USER` value must match the user/device segment expected by the AWS IoT topic and the receiving device.

## 4. AWS resources

### DynamoDB

The service reads from the table named by `TABLE_NAME`.

The code expects a table with a partition key named `device_id` and a sort key named `received_at`. The `received_at` values must be numeric millisecond timestamps because the history endpoint queries a numeric range.

- `GET /sensors/latest` returns the newest item for `DEVICE_ID`.
- `GET /sensors/history?from_ms=<start>&to_ms=<end>` returns items for that device in the inclusive timestamp range.

If the table has no matching items, `/sensors/latest` returns HTTP `404`.

### AWS IoT Core

`POST /actuators/led` publishes a JSON command to the topic configured through `IOT_USER`, using QoS 1. Request body:

```json
{"value":"on"}
```

Allowed `value` values are `on`, `off`, and `toggle`. The published payload has this shape:

```json
{"action":"set","value":"on"}
```

The endpoint returns `{"accepted":true,"value":"on"}` if the publish call succeeds. This confirms that AWS accepted the publish request; it does not confirm that the device received or executed the command.

**AWS IoT endpoint note:** the current code creates `boto3.client("iot-data")` without an explicit account-specific IoT data endpoint URL. AWS IoT Data Plane operations commonly require the account's data endpoint. If publishing fails with an endpoint/connection error, retrieve the endpoint for the correct account and region and update the client configuration in `app/services/commands_service.py`.

## 5. IAM permissions

Grant the runtime identity only the permissions needed for the configured resources. Replace `<region>`, `<account-id>`, and `<table-name>` with the actual values.

### DynamoDB read access

Allow `dynamodb:Query` on the telemetry table:

`arn:aws:dynamodb:<region>:<account-id>:table/<table-name>`

The current implementation uses `Query`; it does not require `dynamodb:Scan` or write permissions.

### AWS IoT publish access

Allow `iot:Publish` on the exact command topic generated from `IOT_USER`.

For `IOT_USER=OleksiiPok`, the resource ARN is:

`arn:aws:iot:<region>:<account-id>:topic/iot-course/OleksiiPok/commands/led`

If `IOT_USER` changes, update the IAM policy resource ARN to match the resulting topic. The service does not need IoT subscribe or receive permissions to publish this command.

### Credential setup

For local development, the IAM user's access keys must belong to an identity with the permissions above. For deployment on AWS, attach the equivalent policy to the workload's IAM role. Do not place credentials in source code, commit them, or share them in test reports.

## 6. API quick reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/test/health` | Check API process health |
| `GET` | `/sensors/latest` | Read the latest telemetry item for `DEVICE_ID` |
| `GET` | `/sensors/history?from_ms=<start>&to_ms=<end>` | Read telemetry within a timestamp range |
| `POST` | `/actuators/led` | Publish an LED command to AWS IoT Core |

Example request using curl:
```bash
curl -X POST "http://127.0.0.1:8000/actuators/led" \
  -H "Content-Type: application/json" \
  -d '{"value":"toggle"}'
```

## 7. Troubleshooting

- **HTTP 404 from `/sensors/latest`:** the table has no telemetry item for `DEVICE_ID` yet, or the configured device ID does not match.
- **HTTP 502 from a sensor endpoint:** check AWS credentials, region, table name, IAM `dynamodb:Query` permission, and the table key schema.
- **HTTP 502 from `/actuators/led`:** check AWS credentials, region, IAM `iot:Publish` permission, the topic generated from `IOT_USER`, and the IoT Data Plane endpoint configuration.
- **HTTP 422 from `/sensors/history`:** ensure `from_ms` and `to_ms` are non-negative integers and `from_ms <= to_ms`.

## Notes for maintainers

- CORS is currently configured to allow all origins, with only `GET` and `POST` methods and the `Content-Type` header. Review this before exposing the service beyond a controlled development environment.
- The provided `requirements.txt` is empty in the supplied archive. The installation command above installs the dependencies imported by the current source files; maintainers should populate and pin `requirements.txt` for reproducible builds.
