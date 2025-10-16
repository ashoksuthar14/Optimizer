import os

# Import the Flask app and orchestrator initializer
try:
    from backend.app import app, initialize_orchestrator
except ImportError:
    from app import app, initialize_orchestrator  # fallback for local runs

# Initialize orchestrator on startup if enabled
if os.getenv("INIT_ORCH_ON_STARTUP", "1") == "1":
    try:
        initialize_orchestrator()
        print("✅ Orchestrator initialized successfully.")
    except Exception as e:
        print(f"⚠️ Orchestrator initialization failed: {e}")

# Expose the Flask app for Gunicorn
application = app  # optional alias, Gunicorn uses `app` below
app = app  # keep this line so gunicorn backend.wsgi:app works

# Optional local dev mode
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask locally on 0.0.0.0:{port}")
    try:
        initialize_orchestrator()
    except Exception as e:
        print(f"⚠️ Local orchestrator init failed: {e}")
    app.run(host="0.0.0.0", port=port)
