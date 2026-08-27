# GitHub Push & Deployment Guide (DEPLOYMENT.md)
## Step-by-Step Deployment Guide for Vercel & GitHub

Yes! You can push **AI Risk Manager** to GitHub and deploy it live on **Vercel** (for the React Frontend) paired with a free hosting provider like **Render** / **Railway** / **Koyeb** (for the FastAPI Backend & PostgreSQL Database).

---

## 1. Pushing the Codebase to GitHub

### Step 1.1: Verify `.gitignore`
We created a root `.gitignore` file to ensure secrets (`.env`), Python virtual environments (`venv/`), SQLite database files (`*.db`), and Node packages (`node_modules/`) are **NEVER committed to GitHub**.

### Step 1.2: Initialize & Commit via Terminal
Open your terminal in `d:\Projects\AI-RISK-MANAGER` and execute:

```powershell
# 1. Initialize git (if not already initialized)
git init

# 2. Stage all project files
git add .

# 3. Commit the code
git commit -m "Initial commit - AI Risk Manager platform"

# 4. Set default branch to main
git branch -M main

# 5. Link your GitHub repository (replace with your actual GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/AI-RISK-MANAGER.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 2. Deploying the Backend & Database

FastAPI requires an active server environment, and SQLite disk storage is read-only / temporary on serverless platforms. For production, deploy the backend to **Render** (Free tier) connected to a free **Neon.tech PostgreSQL database**.

### Step 2.1: Create a Free PostgreSQL DB (Neon.tech or Supabase)
1. Sign up at [Neon.tech](https://neon.tech) (Free Tier).
2. Create a new database named `ai_risk_manager`.
3. Copy your connection URL (e.g., `postgresql://user:pass@ep-xyz.neon.tech/ai_risk_manager?sslmode=require`).

### Step 2.2: Deploy Backend to Render (Render.com)
1. Sign up at [Render.com](https://render.com) and click **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository `AI-RISK-MANAGER`.
3. Configure settings:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables** in Render settings:
   - `GEMINI_API_KEY`: `your_actual_gemini_api_key`
   - `SECRET_KEY`: `ba8fe37e9e9662f96a2b2337a06345ae1e974f0bb65a88df9ef05709969e359c`
   - `DATABASE_URL`: `your_neon_postgresql_url`
5. Click **Deploy Web Service**. You will get a backend URL like `https://ai-risk-manager-api.onrender.com`.

---

## 3. Deploying the React Frontend on Vercel

Vercel is the ultimate platform for deploying Vite + React applications.

### Step 3.1: Deploy via Vercel Dashboard
1. Go to [Vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** $\rightarrow$ **Project**.
3. Select your `AI-RISK-MANAGER` GitHub repository.
4. Configure Deployment Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click `Edit` and select `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Click **Deploy**. Vercel will build and launch your site at `https://ai-risk-manager.vercel.app`.

---

## 4. Connecting Frontend to Live Backend

In `frontend/src/api/client.js`, update the base API URL or configure environment variable support:

```javascript
// frontend/src/api/client.js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

Add `VITE_API_URL` in your Vercel Project Settings $\rightarrow$ Environment Variables:
- **Key**: `VITE_API_URL`
- **Value**: `https://ai-risk-manager-api.onrender.com`

---

## 5. Summary Checklist Before Going Live

- [x] Secrets (`.env`) & database files (`*.db`) excluded via `.gitignore`.
- [x] Gemini API key configured in Production Environment Variables.
- [x] CORS middleware in `backend/app/main.py` updated to allow your Vercel domain (`https://ai-risk-manager.vercel.app`).
- [x] Database updated to production PostgreSQL via `DATABASE_URL`.
