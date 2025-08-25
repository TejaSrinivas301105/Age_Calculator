# Village Bus Service Backend

This is a FastAPI + SQLite backend for village bus occupancy and search.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## APIs

- `GET /search?from_stop=Village%20A&to_stop=Village%20C` — list buses with availability
- `GET /bus/{bus_id}` — bus status
- `GET /bus/by-registration/{registration}` — bus status
- `POST /device/location` with header `X-Device-Key` — update location
- `POST /device/occupancy` with header `X-Device-Key` — update occupancy

Open interactive docs at `/docs`.

## Simulate Device

In another terminal (server running):

```bash
python -m scripts.device_simulator
```
