# =============================================================================
# services/auth_service.py — Authentication & Authorization Logic
# =============================================================================
# This service handles two things:
#   1. PASSWORD SECURITY — hashing passwords (never store plain text!)
#   2. JWT TOKENS — creating and verifying access tokens
#
# WHAT IS JWT?
# JWT = JSON Web Token. It's a secure, self-contained token that proves
# who the user is. After login, we give the user a token. They send it
# with every future request. We verify the token to know who they are.
#
# A JWT looks like: xxxxx.yyyyy.zzzzz (3 parts separated by dots)
#   - Header: algorithm used (e.g., HS256)
#   - Payload: data inside (e.g., user_id, expiry time)
#   - Signature: cryptographic proof it hasn't been tampered with
# =============================================================================

from passlib.context import CryptContext
# passlib is a password hashing library.
# CryptContext manages password hashing — we configure it to use bcrypt.
# bcrypt is the industry standard for password hashing because:
#   - It's slow by design (makes brute-force attacks very expensive)
#   - Each hash has a random "salt" (no two hashes are identical even for same password)
#   - It's adaptive (work factor increases over time as hardware improves)

from jose import JWTError, jwt
# python-jose is a JWT library.
# JWTError → Exception raised when token verification fails.
# jwt → the module we use to encode (create) and decode (verify) tokens.

from datetime import datetime, timedelta, timezone
# datetime → current time
# timedelta → represents a duration (e.g., timedelta(hours=24) = 24 hours)
# timezone → for UTC-aware datetimes

from fastapi import Depends, HTTPException, status
# Depends → FastAPI dependency injection (used in get_current_user)
# HTTPException → raise HTTP errors with status codes (e.g., 401 Unauthorized)
# status → convenient HTTP status code constants (status.HTTP_401_UNAUTHORIZED)

from fastapi.security import OAuth2PasswordBearer
# OAuth2PasswordBearer is a FastAPI security utility.
# It reads the JWT token from the "Authorization: Bearer <token>" header.
# When added as a dependency to a route, FastAPI auto-shows a "lock" icon
# in Swagger UI and requires the token for that endpoint.

from sqlalchemy.orm import Session
# Session → type hint for our database session parameter.

import os
# For reading SECRET_KEY from environment variables.

from dotenv import load_dotenv
# Load .env file values.

load_dotenv()
# Read .env file into environment variables.

# ─────────────────────────────────────────────────────────────────────────────
# Configuration Constants
# ─────────────────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
# SECRET_KEY is used to sign JWT tokens cryptographically.
# IMPORTANT: In production, this MUST be a long, random string kept secret.
# Anyone with this key can create valid tokens → NEVER commit it to GitHub.
# Generate a secure key: python -c "import secrets; print(secrets.token_hex(32))"

ALGORITHM = "HS256"
# The hashing algorithm for JWT signing.
# HS256 = HMAC + SHA-256. It uses our SECRET_KEY to sign the token.
# This ensures only WE can create valid tokens (only we know the SECRET_KEY).

ACCESS_TOKEN_EXPIRE_HOURS = 24
# How long a JWT token is valid. After 24 hours, the user must log in again.
# This limits the damage if a token is stolen — it expires automatically.

# ─────────────────────────────────────────────────────────────────────────────
# Password Hashing Setup
# ─────────────────────────────────────────────────────────────────────────────

pwd_context = CryptContext(
    schemes=["bcrypt"],
    # schemes → list of hashing algorithms to support.
    # We use bcrypt — the gold standard for password hashing.

    deprecated="auto"
    # deprecated="auto" → If we ever switch to a stronger algorithm,
    # old bcrypt hashes are automatically marked as deprecated.
    # This allows gradual migration without breaking existing users.
)

# ─────────────────────────────────────────────────────────────────────────────
# OAuth2 Bearer Token Reader
# ─────────────────────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# tokenUrl="/auth/login" → tells Swagger UI which endpoint to use for login.
# When a route uses this as a dependency, FastAPI automatically:
#   1. Looks for "Authorization: Bearer <token>" in the request header
#   2. Extracts the token string
#   3. Passes it to the route/dependency function


# =============================================================================
# FUNCTION 1: Hash a password
# =============================================================================
def hash_password(plain_password: str) -> str:
    """
    Takes a plain-text password and returns a bcrypt hash.

    Example:
        plain:  "mypassword123"
        hashed: "$2b$12$abc...xyz" (60-char bcrypt hash)

    We store the hashed version in the database. NEVER the plain password.
    """
    return pwd_context.hash(plain_password)
    # pwd_context.hash() applies bcrypt:
    # 1. Generates a random salt
    # 2. Combines salt + password
    # 3. Runs bcrypt hashing
    # 4. Returns the final hash string


# =============================================================================
# FUNCTION 2: Verify a password
# =============================================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches a stored hash.

    During login:
        - User sends: "mypassword123"
        - DB has:     "$2b$12$abc...xyz"
        - This function: hashes "mypassword123" and compares → True/False

    Returns True if match, False if wrong password.
    """
    return pwd_context.verify(plain_password, hashed_password)
    # pwd_context.verify() safely compares without timing attacks.
    # (It uses constant-time comparison to prevent side-channel attacks.)


# =============================================================================
# FUNCTION 3: Create a JWT access token
# =============================================================================
def create_access_token(data: dict) -> str:
    """
    Creates a signed JWT token containing the provided data.

    Args:
        data: dict containing the payload, e.g., {"sub": "user_id_123"}
              "sub" (subject) is the standard JWT claim for the user identifier.

    Returns:
        A signed JWT token string.

    Example flow:
        token = create_access_token({"sub": str(user.id)})
        # Returns: "eyJhbGci..." (the JWT string)
    """
    to_encode = data.copy()
    # Copy the dict so we don't modify the original.

    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    # Calculate the expiry time: current UTC time + 24 hours.
    # datetime.now(timezone.utc) → current time in UTC.
    # timedelta(hours=24) → a duration of 24 hours.

    to_encode.update({"exp": expire})
    # Add the "exp" (expiration) claim to the payload.
    # JWT standard: "exp" tells the verifier when this token expires.
    # python-jose automatically checks "exp" when decoding tokens.

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # jwt.encode() creates the JWT:
    # 1. Encodes payload as base64 JSON
    # 2. Creates a signature using SECRET_KEY + ALGORITHM
    # 3. Returns: header.payload.signature (dot-separated)

    return encoded_jwt


# =============================================================================
# FUNCTION 4: Get current logged-in user (FastAPI Dependency)
# =============================================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    # Depends(oauth2_scheme) → FastAPI automatically extracts the JWT token
    # from the "Authorization: Bearer <token>" request header.
    # If header is missing, FastAPI returns 401 before even calling this function.
):
    """
    FastAPI dependency that verifies the JWT token and returns the user's ID.

    Usage in routes:
        @router.get("/protected")
        def protected_route(user_id: int = Depends(get_current_user)):
            # user_id is the authenticated user's ID
            return {"user_id": user_id}

    Returns the user's ID (int) if token is valid.
    Raises HTTPException(401) if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        # 401 = "You need to log in" (not authenticated).
        detail="Could not validate credentials",
        # Error message sent to the client.
        headers={"WWW-Authenticate": "Bearer"},
        # WWW-Authenticate header tells the client what auth scheme to use.
        # This is the OAuth2 standard for telling clients to use Bearer tokens.
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # jwt.decode() verifies and decodes the JWT:
        # 1. Checks the signature (was this token created by us?)
        # 2. Checks "exp" (is the token still valid / not expired?)
        # 3. Returns the payload dict if valid.
        # Raises JWTError if token is invalid or expired.

        user_id: str = payload.get("sub")
        # Extract the "sub" (subject) claim from the payload.
        # We stored the user's ID as a string in "sub" when creating the token.

        if user_id is None:
            raise credentials_exception
        # If there's no "sub" in the token payload, the token is malformed.

    except JWTError:
        raise credentials_exception
    # If jwt.decode() raises any error (invalid signature, expired, malformed),
    # we catch it and raise our 401 exception to the client.

    return int(user_id)
    # Return the user's ID as an integer.
    # Routes that depend on get_current_user will receive this integer
    # as their "current_user_id" parameter.
