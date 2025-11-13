# Modal Deployment Guide

This guide explains how to deploy the Spelling & Drawing App to Modal with Turso database.

## Architecture

- **Backend (FastAPI + Static Files)**: Modal compute (serverless)
- **Database**: Turso (libSQL - SQLite-compatible, free tier)
- **Images/Drawings**: Modal Volume (persistent storage)
- **Keep-Warm**: Cron job pings every 5 minutes (~$0.20/day, ~$6/month)

## Prerequisites

1. **Modal Account**: Sign up at https://modal.com
   - Starter plan: $0 + $30/month free credits
   - Install Modal CLI: `pip install modal`
   - Authenticate: `modal token new`

2. **Turso Account**: Sign up at https://turso.tech
   - Free tier: 500 databases, 9GB storage, 1B row reads/month
   - Install Turso CLI: `curl -sSfL https://get.tur.so/install.sh | bash`

## Step 1: Create Turso Database

```bash
# Login to Turso
turso auth login

# Create database
turso db create spelling-app

# Get database URL
turso db show spelling-app --url
# Output: libsql://spelling-app-[username].turso.io

# Create auth token
turso db tokens create spelling-app
# Output: eyJhbGc... (save this token)
```

## Step 2: Configure Modal Secrets

Create a Modal secret with your Turso credentials:

```bash
modal secret create turso-credentials \
  TURSO_DATABASE_URL="libsql://spelling-app-[username].turso.io" \
  TURSO_AUTH_TOKEN="eyJhbGc..."
```

## Step 3: Initialize Turso Database

Before deploying, initialize the database schema:

```bash
# Set environment variables locally
export TURSO_DATABASE_URL="libsql://spelling-app-[username].turso.io"
export TURSO_AUTH_TOKEN="eyJhbGc..."

# Run database initialization
cd backend
python -c "from database import init_db; init_db()"
```

This creates all necessary tables in your Turso database.

## Step 4: Deploy to Modal

```bash
# From project root directory
modal deploy modal_app.py
```

This will:
- Build the Docker image with all dependencies
- Create a persistent volume for images/drawings
- Deploy the FastAPI app as a web endpoint
- Set up the keep-warm cron job

You'll get a URL like: `https://avs20--spelling-app-fastapi-app.modal.run`

## Step 5: Update Keep-Warm URL

After deployment, update the keep-warm URL in `modal_app.py`:

```python
app_url = "https://your-username--spelling-app-fastapi-app.modal.run"
```

Then redeploy:

```bash
modal deploy modal_app.py
```

## Step 6: Test Deployment

```bash
# Test health endpoint
curl https://your-username--spelling-app-fastapi-app.modal.run/api/health

# Test frontend
open https://your-username--spelling-app-fastapi-app.modal.run
```

## Local Development

Local development continues to use SQLite (no Turso needed):

```bash
# No environment variables needed
cd backend
python -m uvicorn main:app --reload --port 8002
```

The app automatically detects:
- **No TURSO_* env vars**: Uses local SQLite at `data/spelling.db`
- **TURSO_* env vars set**: Uses remote Turso database

## Cost Breakdown

### Modal (with keep-warm)
- **Compute**: ~$0.0000131/core/sec
- **Memory**: ~$0.00000222/GiB/sec
- **Keep-warm cost**: ~$0.20/day (~$6/month)
- **Your credits**: $30/month (covers 5 months)

### Turso
- **Free tier**: 500 databases, 9GB storage, 1B row reads/month
- **Cost**: $0/month (free tier sufficient for this app)

### Total
- **Monthly cost**: ~$6/month (from your $30 Modal credits)
- **Effective cost**: $0 for first 5 months

## Monitoring

### View Logs
```bash
modal app logs spelling-app
```

### View Volume Contents
```bash
modal volume ls spelling-app-data
```

### Check Keep-Warm Status
```bash
modal app logs spelling-app --function keep_warm
```

## Troubleshooting

### Database Connection Issues

If you see "libsql not available" errors:
```bash
# Verify libsql is installed
pip install libsql-experimental
```

### Volume Permission Issues

If drawings aren't saving:
```bash
# Check volume is mounted
modal volume ls spelling-app-data /app/data
```

### Cold Start Issues

If the app is slow to respond:
- Verify keep-warm cron is running: `modal app logs spelling-app --function keep_warm`
- Check keep-warm URL is correct in `modal_app.py`

## Updating the App

```bash
# Make code changes
git add .
git commit -m "Update feature"

# Redeploy to Modal
modal deploy modal_app.py
```

Modal automatically rebuilds and redeploys with zero downtime.

## Migrating Data from Fly.io

If you have existing data on Fly.io:

1. **Export from Fly.io**:
```bash
# SSH into Fly.io container
fly ssh console
# Dump database
sqlite3 /app/data/spelling.db .dump > backup.sql
# Download backup
fly sftp get /app/data/spelling.db
```

2. **Import to Turso**:
```bash
# Import SQL dump
turso db shell spelling-app < backup.sql
```

3. **Copy drawings to Modal Volume**:
```bash
# Use Modal's volume upload
modal volume put spelling-app-data /app/data/drawings ./drawings
```

## Disabling Keep-Warm (to save costs)

If you want to accept cold starts and save costs:

1. Comment out the `keep_warm` function in `modal_app.py`
2. Remove `keep_warm=1` from the `@app.function` decorator
3. Redeploy: `modal deploy modal_app.py`

This reduces costs to near-zero (only pay per request) but adds 20-60s cold start delay.

## Support

- Modal Docs: https://modal.com/docs
- Turso Docs: https://docs.turso.tech
- Modal Discord: https://discord.gg/modal
