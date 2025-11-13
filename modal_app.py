"""
Modal deployment configuration for Spelling & Drawing App
Deploys FastAPI backend with persistent volume for images
Uses Turso for database (configured via environment variables)
"""

import modal
import os

app = modal.App("spelling-app")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements("backend/requirements.txt")
)

volume = modal.Volume.from_name("spelling-app-data", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/app/data": volume},
    secrets=[
        modal.Secret.from_name("turso-credentials")
    ],
    keep_warm=1,
    timeout=300,
    allow_concurrent_inputs=100,
)
@modal.asgi_app()
def fastapi_app():
    import sys
    sys.path.insert(0, "/root")
    
    from backend.main import app as fastapi_app
    return fastapi_app

@app.function(
    image=image,
    schedule=modal.Cron("*/5 * * * *"),
    secrets=[modal.Secret.from_name("turso-credentials")],
)
def keep_warm():
    """
    Ping the app every 5 minutes to prevent cold starts
    This keeps the container warm and ensures fast response times
    Cost: ~$0.20/day (~$6/month) within Modal's $30/month free credits
    """
    import requests
    
    app_url = "https://avs20--spelling-app-fastapi-app.modal.run"
    
    try:
        response = requests.get(f"{app_url}/api/health", timeout=10)
        print(f"Keep-warm ping: {response.status_code}")
    except Exception as e:
        print(f"Keep-warm ping failed: {e}")
