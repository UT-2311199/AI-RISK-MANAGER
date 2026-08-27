# =============================================================================
# routes/auth.py — Authentication Routes
# =============================================================================
# This file defines two API endpoints:
#   POST /auth/register → Create a new user account
#   POST /auth/login    → Login and receive a JWT token
#
# HOW FASTAPI ROUTING WORKS:
# ──────────────────────────
# Instead of putting ALL routes in main.py (which gets messy), FastAPI lets
# us split routes into separate files using "APIRouter".
# Each router is like a mini-app. We "include" it in main.py to register it.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
# APIRouter → Creates a router object. We attach route decorators (@router.post)
#   to it, just like we'd use @app.post on the main app.
# Depends → FastAPI dependency injection system.
# HTTPException → Raises HTTP errors (like 400 Bad Request, 409 Conflict).
# status → Provides named HTTP status codes (cleaner than hardcoding numbers).

from sqlalchemy.orm import Session
# Session → type hint for the SQLAlchemy DB session.

from app.database import get_db
# get_db → our database dependency from database.py.
# Using Depends(get_db) automatically opens a DB session for each request.

from app.models.models import User
# User → our SQLAlchemy User model (the 'users' table).

from app.schemas.schemas import UserCreate, UserResponse, Token, UserLogin
# Import the Pydantic schemas for input validation and response shaping.

from app.services.auth_service import hash_password, verify_password, create_access_token
# Import our auth utility functions from auth_service.py.

# ─────────────────────────────────────────────────────────────────────────────
# Create Router
# ─────────────────────────────────────────────────────────────────────────────

router = APIRouter(
    prefix="/auth",
    # prefix="/auth" → All routes in this file automatically get "/auth" prepended.
    # So @router.post("/register") becomes POST /auth/register
    # And @router.post("/login") becomes POST /auth/login

    tags=["Authentication"],
    # tags → Groups these routes together under "Authentication" in Swagger UI (/docs).
    # This makes the API documentation much easier to navigate.
)


# =============================================================================
# ENDPOINT 1: Register a new user
# POST /auth/register
# =============================================================================

@router.post(
    "/register",
    response_model=UserResponse,
    # response_model=UserResponse → FastAPI will serialize the return value
    # using the UserResponse Pydantic schema. This ensures:
    #   1. Only the fields defined in UserResponse are returned
    #   2. Fields like 'hashed_password' are automatically excluded
    #   3. The response is properly formatted JSON

    status_code=status.HTTP_201_CREATED
    # status_code=201 → "Created". Standard HTTP code when a resource is created.
    # Default is 200 "OK", but 201 is more semantically correct for registration.
)
def register(
    user_data: UserCreate,
    # user_data: UserCreate → FastAPI reads the request body and validates it
    # against UserCreate schema. If email or password is missing → 422 error.

    db: Session = Depends(get_db)
    # db: Session = Depends(get_db) → dependency injection.
    # FastAPI calls get_db(), gets a DB session, and passes it as 'db'.
    # When the function returns, get_db()'s finally block closes the session.
):
    """
    Register a new user account.

    Request body: { "email": "...", "password": "...", "full_name": "..." }
    Response: User object (without password)

    HTTP 409 if email already exists.
    HTTP 201 + user object on success.
    """

    # Check if email already exists in database
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    # db.query(User) → start a SELECT query on the 'users' table.
    # .filter(User.email == user_data.email) → WHERE email = 'user@example.com'
    # .first() → return the first matching row, or None if not found.
    # This is equivalent to: SELECT * FROM users WHERE email = '...' LIMIT 1;

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            # 409 Conflict → "The request conflicts with current state of the server."
            # Semantically correct: there's a CONFLICT because this email exists.
            detail="An account with this email already exists."
        )
    # If existing_user is not None (i.e., email is taken), we stop here
    # and return a 409 error. The rest of the function doesn't execute.

    # Hash the password before storing
    hashed = hash_password(user_data.password)
    # NEVER store plain text passwords!
    # hash_password() applies bcrypt: "mypassword" → "$2b$12$xyz..."

    # Create new User object (this doesn't save to DB yet)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        # created_at is set automatically by the column default in models.py
    )
    # This creates a Python User object in memory. Nothing in the DB yet.

    db.add(new_user)
    # db.add() → stages the new user for insertion.
    # Equivalent to: "prepare this INSERT statement"
    # Still not in the DB yet!

    db.commit()
    # db.commit() → executes the INSERT and saves to the database permanently.
    # After this, the user exists in the DB.

    db.refresh(new_user)
    # db.refresh() → reloads the object from the database.
    # This is important because the DB assigns the 'id' and 'created_at' values.
    # After refresh, new_user.id contains the auto-assigned ID.

    return new_user
    # FastAPI takes this SQLAlchemy User object and serializes it using
    # UserResponse schema (because of response_model=UserResponse).
    # This works because we have model_config = {"from_attributes": True} in UserResponse.


# =============================================================================
# ENDPOINT 2: Login
# POST /auth/login
# =============================================================================

@router.post(
    "/login",
    response_model=Token
    # response_model=Token → returns {"access_token": "...", "token_type": "bearer"}
)
def login(
    user_credentials: UserLogin,
    # user_credentials: UserLogin → expects {"email": "...", "password": "..."}
    db: Session = Depends(get_db)
):
    """
    Login with email and password. Returns a JWT access token.

    Request body: { "email": "...", "password": "..." }
    Response: { "access_token": "eyJ...", "token_type": "bearer" }

    HTTP 401 if credentials are wrong.
    HTTP 200 + token on success.

    The client must store this token and send it in all future requests:
    Authorization: Bearer <access_token>
    """

    # Find the user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    # Same query as registration — look up the user by email.

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # 401 Unauthorized → "You are not authenticated."
            detail="Invalid email or password.",
            # SECURITY NOTE: We use a VAGUE error message on purpose.
            # "Invalid email or password" (not "Email not found") prevents
            # attackers from using this endpoint to discover valid emails.
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the password
    if not verify_password(user_credentials.password, user.hashed_password):
        # verify_password() hashes the submitted password and compares to stored hash.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            # Same vague message — don't tell them whether email or password was wrong.
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Both checks passed — create a JWT token
    access_token = create_access_token(
        data={"sub": str(user.id)}
        # "sub" (subject) is a standard JWT claim. We store the user's ID as a string.
        # Why string? JWT standard recommends "sub" be a string.
        # In get_current_user(), we convert it back to int with int(user_id).
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
        # "bearer" is the OAuth2 token type for JWT tokens.
        # The client sends it as: Authorization: Bearer <access_token>
    )
    # This returns: {"access_token": "eyJhbGci...", "token_type": "bearer"}
