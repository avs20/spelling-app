"""
Modal deployment configuration for Spelling & Drawing App (Preprod)
Deploys FastAPI backend with persistent volume for images
Uses Turso for database (configured via environment variables)
"""

import modal

app = modal.App("spelling-app-preprod")

# Use Dockerfile to build image
image = modal.Image.from_dockerfile("Dockerfile")

volume = modal.Volume.from_name("spelling-app-preprod-data", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/modal-data": volume},
    min_containers=1,
    timeout=300,
)
@modal.asgi_app()
def fastapi_app():
    """
    Deploy FastAPI app with Turso database (Preprod)
    """
    import sys
    import os
    
    # Set working directory and path for imports
    os.chdir("/app")
    sys.path.insert(0, "/app")
    
    # Import the FastAPI app
    from backend.main import app as fastapi_app
    return fastapi_app

@app.function(
    image=image,
    schedule=modal.Cron("*/5 * * * *"),
)
def keep_warm():
    """
    Ping the app every 5 minutes to prevent cold starts
    """
    import requests
    
    app_url = "https://avs20--spelling-app-preprod-fastapi-app.modal.run"
    
    try:
        response = requests.get(f"{app_url}/api/health", timeout=10)
        print(f"Keep-warm ping: {response.status_code}")
    except Exception as e:
        print(f"Keep-warm ping failed: {e}")
