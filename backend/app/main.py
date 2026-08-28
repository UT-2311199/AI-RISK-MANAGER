# =============================================================================
# app/main.py — FastAPI Application Entry Point
# =============================================================================
# This is the CENTRAL file that wires everything together.
# It does 4 things:
#   1. Creates the FastAPI application instance
#   2. Adds CORS middleware (allows React frontend to call the API)
#   3. Registers all route files (auth, projects, risks)
#   4. Creates all database tables on startup
# =============================================================================

from fastapi import FastAPI
# FastAPI is the main class. We create ONE instance of it (our 'app').
# This app is what uvicorn runs: uvicorn app.main:app

from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware handles Cross-Origin Resource Sharing (CORS).
#
# WHAT IS CORS?
# ─────────────
# Browsers block JavaScript from calling APIs on DIFFERENT domains by default.
# This is a security feature. But our setup has:
#   Frontend: http://localhost:5173 (React/Vite)
#   Backend:  http://localhost:8000 (FastAPI)
# These are DIFFERENT origins (different ports = different origin).
# Without CORS, the browser would block all API calls from React.
# CORSMiddleware tells the browser: "it's okay, I allow these origins."

from app.database import engine, Base
# engine → our SQLAlchemy connection to the database.
# Base → the parent class all our table models inherit from.

from app.models import models
# Import the models module. This is CRITICAL!
# Even though we don't use 'models' directly here, importing it ensures
# that all our model classes (User, Project, Risk) are REGISTERED with Base.
# Without this import, Base.metadata.create_all() would create NO tables.

from app.routes import auth, projects, risks
# Import our three router modules. Each contains an APIRouter instance
# with route definitions.


# =============================================================================
# Create FastAPI Application
# =============================================================================

app = FastAPI(
    title="AI Risk Manager API",
    # Shows in Swagger UI (/docs) as the page title.

    description="""
    ## AI-Powered Risk Assessment and Management API

    This API allows you to:
    - **Register and Login** to manage your account
    - **Create Projects** to organize your risk assessments
    - **Run AI Analysis** using Google Gemini to identify risks
    - **Track Risks** and update their status over time

    ### Authentication
    All project and risk endpoints require a JWT token.
    1. Register via `POST /auth/register`
    2. Login via `POST /auth/login` to get your token
    3. Click **Authorize** (🔒) in Swagger UI and paste your token
    """,
    # Multi-line description shown in Swagger UI. Markdown is supported.

    version="1.0.0",
    # API version number. Shown in Swagger UI.

    docs_url="/docs",
    # URL for Swagger UI interactive documentation. Default is /docs.

    redoc_url="/redoc"
    # URL for ReDoc documentation. Alternative, cleaner doc format.
)


# =============================================================================
# CORS Configuration
# =============================================================================

import os

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
custom_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://ai-risk-manager-tau.vercel.app",
] + custom_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if not allowed_origins_env == "*" else ["*"],
    # Allow all Vercel preview URLs (*.vercel.app) AND all Render service URLs (*.onrender.com)
    allow_origin_regex=r"https://(.*\.vercel\.app|.*\.onrender\.com)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Create Database Tables
# =============================================================================

Base.metadata.create_all(bind=engine)
# This is the AUTO-MIGRATION command.
# SQLAlchemy looks at all models registered with Base (User, Project, Risk)
# and creates their corresponding tables IF THEY DON'T EXIST.
#
# create_all() is SAFE to call every time:
# - If tables don't exist → CREATE TABLE
# - If tables already exist → do nothing (no data loss)
#
# This runs ONCE when the server starts up.
# In production, you'd use Alembic for proper migrations.


# =============================================================================
# Register Route Files
# =============================================================================

app.include_router(auth.router)
# Registers all routes from routes/auth.py.
# POST /auth/register and POST /auth/login are now active.

app.include_router(projects.router)
# Registers all routes from routes/projects.py.
# POST /projects, GET /projects, GET /projects/{id}, DELETE /projects/{id}

app.include_router(risks.router)
# Registers all routes from routes/risks.py.
# POST /projects/{id}/analyze, GET /projects/{id}/risks, etc.


# =============================================================================
# Root Endpoint (Health Check)
# =============================================================================

@app.get(
    "/",
    tags=["Health"]
    # tags=["Health"] → groups this endpoint under "Health" in Swagger UI.
)
def root():
    """
    Health check endpoint. Returns a status message.
    Use this to verify the API server is running correctly.
    """
    return {
        "status": "healthy",
        "message": "AI Risk Manager API is running!",
        "version": "1.0.0",
        "docs": "Visit /docs for interactive API documentation"
    }
