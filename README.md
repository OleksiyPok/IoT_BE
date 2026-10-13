# IoT Backend

[English](README/README.en.md) | [Українська](README/README.uk.md)

FastAPI backend for retrieving ESP32 telemetry and event records from Amazon DynamoDB and publishing LED commands through AWS IoT Core.

- **API documentation:** `http://127.0.0.1:8000/docs`
- **OpenAPI schema:** `http://127.0.0.1:8000/openapi.json`
- **Web LED control page:** `http://127.0.0.1:8000/`
- **Health check:** `http://127.0.0.1:8000/test/health`

## 1. Requirements

- Python 3.10 or newer.
- An AWS account and access to the project's AWS resources.
- AWS credentials with the permissions described in [AWS configuration and permissions](#4-aws-configuration-and-permissions).
- The DynamoDB tables and AWS IoT Core topic used by the device must already exist and match the configuration below.

## 2. Run on another computer

Run all commands from the backend project root—the directory containing `app/` and `.env.example`.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn boto3 python-dotenv
Copy-Item .env.example .env
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install fastapi uvicorn boto3 python-dotenv
cp .env.example .env
```

Edit `.env` as described in the next section, then start the API:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore and call the endpoints.

To stop the server, press `Ctrl+C`.

> The supplied archive does not contain a populated `requirements.txt`. The installation commands above install the direct Python dependencies used by the application. For repeatable installation, maintain a `requirements.txt` with pinned versions.

## 3. Environment configuration

Create `.env` from `.env.example` and configure it for your AWS account and device.

| Variable | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key ID for local development, if using static credentials. |
| `AWS_SECRET_ACCESS_KEY` | Secret key paired with the access key. Keep it private. |
| `AWS_DEFAULT_REGION` | AWS region containing the DynamoDB tables and IoT resources. The example uses `eu-central-1` (Frankfurt). |
| `TELEMETRY_TABLE_NAME` | Name of the DynamoDB table containing sensor telemetry. |
| `EVENTS_TABLE_NAME` | Name of the DynamoDB table containing device events. |
| `DEVICE_ID` | Device identifier used to select records from both tables. It must match the `device_id` stored in DynamoDB. |
| `IOT_USER` | User/device segment used to build the LED command topic. It must match the topic expected by the ESP32 and AWS IoT policies. |

Example:

```dotenv
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=eu-central-1
TELEMETRY_TABLE_NAME=iot_telemetry
EVENTS_TABLE_NAME=iot_events
DEVICE_ID=your_actual_device_id
IOT_USER=your_topic_user
```

Replace all example credentials and identifiers with the actual values.

Do not commit `.env` or share its secrets.

For local development, use a dedicated IAM identity with least-privilege permissions. If credentials are already provided through an AWS profile or another supported AWS credential source, the static access-key variables may be omitted.

On AWS-hosted compute, prefer an IAM role over long-lived access keys.

## 4. AWS configuration and permissions

### 4.1. DynamoDB tables

The application reads from two separate tables:

- `TELEMETRY_TABLE_NAME` — sensor telemetry.
- `EVENTS_TABLE_NAME` — device events.

The code expects each table to have the following key schema:

- Partition key: `device_id`
- Sort key: `received_at`

`device_id` must match `DEVICE_ID`.

`received_at` must be a numeric Unix timestamp in **milliseconds**. The history endpoints use an inclusive range query on `received_at`.

The application performs DynamoDB `Query` operations. The IAM identity used by the backend needs `dynamodb:Query` permission on both configured tables.

The current code does not require `dynamodb:Scan` or DynamoDB write permissions.

### 4.2. AWS IoT Core

The LED command topic is built in `app/services/commands_service.py`:

```text
iot-course/{IOT_USER}/commands/led
```

For example, if `IOT_USER=StudentName`, the topic is:

```text
iot-course/StudentName/commands/led
```

The AWS identity used by the backend needs `iot:Publish` permission on the corresponding topic ARN, for example:

```text
arn:aws:iot:eu-central-1:<account-id>:topic/iot-course/StudentName/commands/led
```

The command publisher currently creates `boto3.client("iot-data")` without an explicit account-specific IoT Data Plane endpoint URL.

If command publishing fails with an endpoint or connection error, verify the IoT Data Plane endpoint for the correct AWS account and region. Configure the client in `app/services/commands_service.py` if necessary.

A successful command response means the backend's publish call succeeded. It **does not** prove that the ESP32 received or executed the command.

Device-side confirmation requires telemetry, an event, or another acknowledgement mechanism.

## 5. API reference

The interactive request schemas and response models available to FastAPI are shown in Swagger UI:

`http://127.0.0.1:8000/docs`

### 5.1. Health check and web page

| Method and path | Parameters / body | Behavior |
|---|---|---|
| `GET /test/health` | None | Returns `{"status":"ok"}` if the API process responds. It does not test AWS credentials or connectivity. |
| `GET /` | None | Serves the built-in LED control page from `app/static/led_control.html`. |

### 5.2. Sensors — telemetry table

All sensor endpoints read from `TELEMETRY_TABLE_NAME` and filter records by `DEVICE_ID`.

| Method and path | Parameters | Behavior |
|---|---|---|
| `GET /sensors/latest` | None | Returns the most recent telemetry record for the configured device. Returns `404` if no record is found. |
| `GET /sensors/last-count?count=10` | Required `count`, integer `>= 1`. | Returns up to `count` recent telemetry records, ordered by `received_at` from newest to oldest. |
| `GET /sensors/last-hours?hours=2` | Required `hours`, integer from `1` through `24`. | Returns telemetry for the specified number of preceding hours, calculated using server time. |
| `GET /sensors/history?from_ms=...&to_ms=...` | Required `from_ms` and `to_ms`: non-negative Unix timestamps in milliseconds; `from_ms <= to_ms`. | Returns telemetry records whose `received_at` falls within the inclusive time range. |

#### Which sensor endpoint should I use?

- **Latest reading:** `/sensors/latest` — retrieves one most recent record.
- **Fixed number of records:** `/sensors/last-count?count=10` — retrieves up to 10 recent records.
- **Rolling time interval:** `/sensors/last-hours?hours=2` — retrieves records from the preceding two hours.
- **Exact time interval:** `/sensors/history?from_ms=...&to_ms=...` — retrieves records within the specified timestamp range.

Use `last-count` when the number of records matters more than their age.

Use `last-hours` when you need a simple rolling time interval without calculating timestamps yourself.

Use `history` when the caller controls the time range, for example through a Grafana time picker.

#### Examples

Latest reading:

```http
GET http://127.0.0.1:8000/sensors/latest
```

Last 10 readings:

```http
GET http://127.0.0.1:8000/sensors/last-count?count=10
```

Readings from the last two hours:

```http
GET http://127.0.0.1:8000/sensors/last-hours?hours=2
```

Readings within a specific time range:

```http
GET http://127.0.0.1:8000/sensors/history?from_ms=1791741000000&to_ms=1791741600000
```

### 5.3. Events — events table

All event endpoints read from `EVENTS_TABLE_NAME` and filter records by `DEVICE_ID`.

| Method and path | Parameters | Behavior |
|---|---|---|
| `GET /events/latest` | None | Returns the most recent event. Returns `404` if no event is found. |
| `GET /events/last-count?count=20` | Required `count`, integer `>= 1`. | Returns up to the requested number of newest events. |
| `GET /events/last-hours?hours=6` | Required `hours`, integer from `1` through `24`. | Returns events from the specified number of preceding hours, calculated using server time. |
| `GET /events/history?from_ms=...&to_ms=...` | Required `from_ms` and `to_ms`: non-negative Unix timestamps in milliseconds; `from_ms <= to_ms`. | Returns events within the inclusive time range. |

#### Which events endpoint should I use?

- **One newest event:** `/events/latest`.
- **A fixed number of newest events:** `/events/last-count?count=20`.
- **A rolling time interval:** `/events/last-hours?hours=6`.
- **An exact time interval:** `/events/history?from_ms=...&to_ms=...`.

#### Examples

Latest event:

```http
GET http://127.0.0.1:8000/events/latest
```

Last 20 events:

```http
GET http://127.0.0.1:8000/events/last-count?count=20
```

Events from the last six hours:

```http
GET http://127.0.0.1:8000/events/last-hours?hours=6
```

Events within a specific time range:

```http
GET http://127.0.0.1:8000/events/history?from_ms=1791741000000&to_ms=1791741600000
```

### 5.4. Actuators — LED commands

| Method and path | JSON body | Behavior |
|---|---|---|
| `POST /actuators/led` | `{"value":"on"}`, `{"value":"off"}`, or `{"value":"toggle"}` | Publishes an LED command to AWS IoT Core. Returns HTTP `202 Accepted` when the publish call succeeds. |

#### Request example

```bash
curl -X POST "http://127.0.0.1:8000/actuators/led" \
  -H "Content-Type: application/json" \
  -d '{"value":"toggle"}'
```

The backend publishes the following payload to the configured topic:

```json
{"action":"set","value":"toggle"}
```

The accepted `value` strings are lowercase and must be exactly:

- `on`
- `off`
- `toggle`

The `toggle` operation asks the device to change its current LED state. The endpoint itself does not read the current state.

When the publish call succeeds, the API returns HTTP `202 Accepted` with a response similar to:

```json
{
  "accepted": true,
  "value": "toggle"
}
```

This confirms successful publication by the backend, not execution by the device.

The built-in page at `http://127.0.0.1:8000/` currently provides **Led ON** and **Led OFF** buttons. The API also accepts `toggle`.

## 6. HTTP status codes and troubleshooting

| HTTP status | Meaning / what to check |
|---|---|
| `200 OK` | The request succeeded. |
| `202 Accepted` | The LED command publish call succeeded; device execution is not confirmed. |
| `404 Not Found` | The requested latest sensor/event record was not found. Check that data exists and `DEVICE_ID` matches the DynamoDB records. |
| `422 Unprocessable Entity` | A query parameter or request body failed validation. Check parameter types, allowed ranges, and timestamp order. |
| `502 Bad Gateway` | The API could not complete an AWS operation. Check credentials, region, table names, DynamoDB key schema and permissions, IoT publish permission, topic, and IoT Data Plane endpoint. |

`GET /test/health` only checks whether the FastAPI application responds. A successful response does not establish that AWS access works.

## 7. Security notes

- Restrict IAM permissions to the required DynamoDB tables and exact IoT command topic.
- Do not commit `.env`, AWS keys, or other secrets.
- CORS is configured to allow all origins (`*`) for this demo. Before exposing the backend publicly, replace this with the specific frontend origins you trust.
- The current application allows only `GET` and `POST` CORS methods and the `Content-Type` header.
- The current test routes contain only `/test/health`; there is no dedicated AWS connectivity test endpoint in this archive.

---

[Back to top](#iot-backend) | [Українська](README/README.uk.md)