# Deployment Guide - Free Hosting Options

## 🎯 Recommended Free Hosting Platforms

### Option 1: Render (Recommended ⭐)
**Best for:** Full-stack apps with file storage
**Free Tier:** 750 hours/month, sleeps after 15 min inactivity

#### Pros:
- ✅ Easy deployment from GitHub
- ✅ Supports Python/FastAPI
- ✅ SQLite database works
- ✅ File storage persists
- ✅ Auto-deploy on git push

#### Deployment Steps:

1. **Push to GitHub:**
```bash
cd /Volumes/External/MacDisk/Desktop/Spelling
git remote add origin https://github.com/YOUR_USERNAME/spelling-app.git
git push -u origin main
```

2. **Create render.yaml:**
```yaml
services:
  - type: web
    name: spelling-app
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt && cd ../frontend"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

3. **Go to Render.com:**
   - Sign up at https://render.com
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect and deploy

4. **Access your app:**
   - Backend: `https://spelling-app.onrender.com`
   - Frontend: Serve via static site or same backend

---

### Option 2: Railway
**Best for:** Quick deployment with database
**Free Tier:** $5 credit/month, then sleeps

#### Pros:
- ✅ Very easy setup
- ✅ Great for FastAPI
- ✅ File storage works
- ✅ Good dashboard

#### Deployment:

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Login and deploy:**
```bash
railway login
railway init
railway up
```

3. **Or use Railway.app:**
   - Go to https://railway.app
   - Connect GitHub
   - Deploy from repo

---

### Option 3: PythonAnywhere
**Best for:** Python-specific apps
**Free Tier:** 1 web app, limited CPU

#### Pros:
- ✅ Designed for Python
- ✅ Easy file management
- ✅ SQLite support
- ✅ Always on (no sleep)

#### Deployment:

1. **Sign up:** https://www.pythonanywhere.com
2. **Upload files via Web interface**
3. **Configure WSGI:**
```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py
import sys
path = '/home/yourusername/spelling-app/backend'
if path not in sys.path:
    sys.path.append(path)

from main import app as application
```

4. **Set working directory:** `/home/yourusername/spelling-app/backend`
5. **Enable web app**

---

### Option 4: Fly.io
**Best for:** Docker-based deployments
**Free Tier:** 3 shared VMs

#### Deployment:

1. **Install flyctl:**
```bash
brew install flyctl  # macOS
```

2. **Login:**
```bash
flyctl auth login
```

3. **Deploy:**
```bash
flyctl launch
flyctl deploy
```

---

## 🚀 Quick Setup for Render (Easiest)

### Step-by-Step Guide:

#### 1. Prepare for Deployment

Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: spelling-app-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### 2. Update Backend for Production

Edit `backend/main.py`:

```python
import os

# Update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8002",
        "https://your-app.onrender.com"  # Add your Render URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use environment variable for port
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### 3. Create Procfile (optional):

```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 4. Push to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 5. Deploy on Render:

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Settings:
   - **Name:** spelling-app
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"

#### 6. Deploy Frontend:

**Option A: Same Render service**
- Serve frontend through FastAPI static files

**Option B: Separate static site**
1. Create new "Static Site" on Render
2. Point to `frontend/` directory
3. No build command needed

---

## 🌐 Alternative: Local Network (Free!)

**Best for:** Testing on local devices/tablets

### 1. Find Your IP Address:

```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

### 2. Update CORS in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local network
    ...
)
```

### 3. Start Servers:

```bash
# Terminal 1 - Backend
cd backend
~/.local/bin/uv run python main.py

# Terminal 2 - Frontend
cd frontend
~/.local/bin/uv run python -m http.server 8002
```

### 4. Access from Tablet:

On same WiFi network:
```
http://YOUR_IP:8002/index.html
http://YOUR_IP:8002/admin.html
http://YOUR_IP:8002/dashboard.html
```

---

## 📦 Docker Deployment (Advanced)

### Create Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY data/ ./data/

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and run:

```bash
docker build -t spelling-app .
docker run -p 8000:8000 spelling-app
```

---

## 🔧 Configuration for Production

### Environment Variables:

Create `.env` file:

```env
DATABASE_PATH=../data/spelling.db
DRAWINGS_PATH=../data/drawings
REFERENCES_PATH=../data/references
CORS_ORIGINS=https://your-frontend-url.com
PORT=8000
```

### Update database.py:

```python
import os
from pathlib import Path

DB_PATH = os.getenv("DATABASE_PATH", "../data/spelling.db")
```

---

## 📊 Cost Comparison

| Platform | Free Tier | Limitations | Best For |
|----------|-----------|-------------|----------|
| **Render** | 750 hrs/mo | Sleeps after 15 min | Full-stack apps |
| **Railway** | $5 credit | Pay after credit | Quick deploys |
| **PythonAnywhere** | 1 web app | Limited CPU | Python apps |
| **Fly.io** | 3 VMs | 256MB RAM | Docker apps |
| **Local Network** | Unlimited | Same network only | Testing |

---

## ✅ Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Database migrations handled
- [ ] CORS origins configured
- [ ] Environment variables set
- [ ] File uploads working
- [ ] Static files served correctly
- [ ] Error handling in place
- [ ] Logs configured

---

## 🚨 Important Notes

### File Storage:
- **Render/Railway:** Files may be deleted on restart (use cloud storage for production)
- **PythonAnywhere:** Persistent storage
- **Solution:** Use S3/Cloudinary for drawings in production

### Database:
- SQLite works on all platforms
- Consider PostgreSQL for production scale
- Backup database regularly

### Security:
- Change admin password from default
- Use environment variables for secrets
- Enable HTTPS (automatic on Render/Railway)

---

## 🎯 Recommended Path

For **free and easy deployment**:

1. ✅ **Start with Render**
2. Push code to GitHub
3. Connect Render to GitHub repo
4. Deploy in 5 minutes
5. Get free HTTPS URL

For **long-term production**:
1. Use Render/Railway for backend
2. Use Cloudflare R2/S3 for images
3. Add PostgreSQL database
4. Set up CI/CD pipeline

---

## 📚 Next Steps After Deployment

1. Test all features on deployed app
2. Add more word categories
3. Monitor performance
4. Collect user feedback
5. Iterate and improve!

---

## 🆘 Troubleshooting

### App Not Starting:
- Check build logs on platform
- Verify requirements.txt
- Check Python version

### Database Errors:
- Ensure data/ directory exists
- Check file permissions
- Verify database path

### CORS Errors:
- Add deployed URL to allow_origins
- Check frontend is using correct API URL

### File Upload Fails:
- Check write permissions
- Verify storage path exists
- Check disk space limits
