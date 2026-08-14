# Backend

The backend is the authoritative service for broker/account state, market data normalization, deterministic risk calculations, trade approval, execution intents, and audit logging.

## Start

From the repository root:

```powershell
.\backend\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs:

`http://127.0.0.1:8000/docs`

## Tests

```powershell
python -m pytest
```

Execution and live trading are disabled at this stage.
