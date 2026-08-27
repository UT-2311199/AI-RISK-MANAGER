# =============================================================================
# schemas/schemas.py — Pydantic Request & Response Schemas
# =============================================================================
# "Schemas" are Pydantic models that define the SHAPE of data coming IN to
# our API (request body) and going OUT of our API (response body).
#
# They are DIFFERENT from SQLAlchemy models (models.py):
#   - SQLAlchemy models = database table structure
#   - Pydantic schemas   = API input/output structure
#
# Pydantic automatically:
#   1. Validates incoming data (wrong type? missing field? → 422 error)
#   2. Converts data types (string "123" → integer 123)
#   3. Generates OpenAPI docs for Swagger UI (/docs)
#
# Naming convention:
#   - *Create  → data needed to CREATE something (sent by client)
#   - *Response → data sent BACK to client (never include passwords!)
#   - *Update  → data needed to UPDATE something (usually optional fields)
# =============================================================================

from pydantic import BaseModel, EmailStr
# BaseModel → All Pydantic schemas inherit from this. It provides validation,
#   serialization, and documentation generation automatically.
# EmailStr → A special string type that validates email format.
#   "not-an-email" would be rejected. "user@example.com" is accepted.

from typing import Optional, List
# Optional[X] → The field can be X or None (i.e., it's not required).
# List[X]     → A list containing items of type X. e.g., List[str] = ["a","b"]

from datetime import datetime
# Used to type-hint datetime fields in response schemas.


# =============================================================================
# ── AUTH SCHEMAS ─────────────────────────────────────────────────────────────
# =============================================================================

class UserCreate(BaseModel):
    """
    Schema for REGISTERING a new user.
    This is what the client sends in the request body to POST /auth/register.
    """
    email: EmailStr
    # EmailStr validates the format: must contain '@' and a domain.
    # "test@" → rejected. "test@example.com" → accepted.

    password: str
    # Plain-text password sent by the user. We will hash this before storing.
    # We NEVER store the plain password.

    full_name: Optional[str] = None
    # Optional → client doesn't have to send this. Defaults to None.


class UserResponse(BaseModel):
    """
    Schema for RETURNING user info in API responses.
    IMPORTANT: Never include 'password' or 'hashed_password' here!
    The client should never receive the password back.
    """
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
    # from_attributes=True (formerly orm_mode=True in Pydantic v1)
    # This tells Pydantic: "You can read this data from a SQLAlchemy ORM object,
    # not just from a dict."
    # Without this, you can't do UserResponse.model_validate(user_db_object).
    # With it, Pydantic reads attributes like user.id, user.email directly.


class Token(BaseModel):
    """
    Schema for the LOGIN response.
    After successful login, we return a JWT access token.
    """
    access_token: str
    # The JWT token string. Client stores this and sends it in
    # the Authorization header for all future protected requests.
    # Format: "Authorization: Bearer <access_token>"

    token_type: str
    # Always "bearer" for JWT authentication.
    # "bearer" means: "whoever bears (has) this token is authenticated."


class UserLogin(BaseModel):
    """
    Schema for LOGIN request body.
    Client sends email + password to POST /auth/login.
    """
    email: EmailStr
    password: str


# =============================================================================
# ── PROJECT SCHEMAS ───────────────────────────────────────────────────────────
# =============================================================================

class ProjectCreate(BaseModel):
    """
    Schema for CREATING a new project.
    Sent by client to POST /projects.
    """
    name: str
    # Project name. e.g., "Payment Processing System"

    description: Optional[str] = None
    # What the project does. Optional.

    objective: Optional[str] = None
    # Business goal. e.g., "Process 10k transactions/day securely"

    technologies: Optional[List[str]] = []
    # List of technologies used. e.g., ["React", "FastAPI", "PostgreSQL"]
    # Defaults to empty list if not provided.

    context: Optional[str] = None
    # Additional info the user wants the AI to consider during analysis.
    # e.g., "This app handles medical records and credit card data."
    # The more context, the better the AI's risk analysis.


class ProjectResponse(BaseModel):
    """
    Schema for returning project data in responses.
    """
    id: int
    name: str
    description: Optional[str] = None
    objective: Optional[str] = None
    technologies: Optional[List[str]] = []
    context: Optional[str] = None
    overall_risk_score: Optional[float] = None
    # overall_risk_score is None until the user runs an analysis.
    created_at: datetime
    owner_id: int

    model_config = {"from_attributes": True}


class ProjectSummary(BaseModel):
    """
    A lighter version of ProjectResponse — used in list views.
    Contains only the most important fields (not the full context text).
    """
    id: int
    name: str
    description: Optional[str] = None
    overall_risk_score: Optional[float] = None
    created_at: datetime
    risk_count: Optional[int] = 0
    # Number of risks identified for this project.

    model_config = {"from_attributes": True}


# =============================================================================
# ── RISK SCHEMAS ──────────────────────────────────────────────────────────────
# =============================================================================

class RiskResponse(BaseModel):
    """
    Schema for returning a single risk in API responses.
    This is what the client receives after AI analysis is complete.
    """
    id: int
    title: str
    category: str
    severity: str
    probability: str
    impact: str
    risk_score: float
    explanation: str
    mitigation: Optional[List[str]] = []
    # mitigation is a list of action strings.
    # e.g., ["Use HTTPS", "Encrypt stored data", "Add access logging"]

    status: str
    created_at: datetime
    project_id: int

    model_config = {"from_attributes": True}


class AnalyzeRequest(BaseModel):
    """
    Schema for triggering AI risk analysis.
    Sent by client to POST /projects/{id}/analyze.
    The client can optionally add extra context specifically for this analysis run.
    """
    additional_context: Optional[str] = None
    # Any extra information the user wants to add just for this analysis.
    # e.g., "Focus especially on GDPR compliance risks."
    # If provided, this is appended to the project's base context.


class RiskStatusUpdate(BaseModel):
    """
    Schema for updating a risk's status.
    Sent by client to PATCH /risks/{id}/status.
    """
    status: str
    # New status value. Must be one of:
    # "Open", "Under Review", "Mitigation in Progress", "Resolved", "Accepted"

    # Note: We validate this in the route handler, not here,
    # because enum validation gives better error messages.


class AnalysisResponse(BaseModel):
    """
    Schema for the response after AI analysis completes.
    Returns the updated project score and all identified risks.
    """
    project_id: int
    project_name: str
    overall_risk_score: float
    total_risks: int
    # How many individual risks were identified.

    risks: List[RiskResponse]
    # The full list of all identified risk objects.

    message: str
    # A human-readable summary message.
    # e.g., "Analysis complete. Found 5 risks. Overall score: 7.2/10"
