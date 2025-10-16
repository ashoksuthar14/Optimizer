import os

# Support both invocation modes:
# - backend.wsgi:app (repo root)
# - wsgi:app (with root set to backend)
try:
    from .app import app, initialize_orchestrator  # when imported as backend.wsgi
except Exception:
    try:
        from app import app, initialize_orchestrator  # when CWD is backend
    except Exception:
        from backend.app import app, initialize_orchestrator  # when importing from repo root

# Optional: initialize orchestrator on startup if explicitly enabled
if os.getenv("INIT_ORCH_ON_STARTUP") == "1":
    try:
        initialize_orchestrator()
    except Exception as e:
        # Avoid crashing the worker on init errors; endpoints will report the issue
        print(f"Orchestrator init on import failed: {e}")

# Expose `app` for Gunicorn
# Start locally if needed: `python wsgi.py`
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # For local dev, initialize orchestrator once
    try:
        initialize_orchestrator()
    except Exception as e:
        print(f"Local init failed: {e}")
    app.run(host="0.0.0.0", port=port)
