# =============================================================================
# database.py — Database Engine & Session Setup
# =============================================================================
# This file is the foundation of our database layer.
# It does three things:
#   1. Creates the connection to the database (the "engine")
#   2. Creates a "session factory" to open/close DB conversations
#   3. Creates a "Base" class that all our DB table models will inherit from
# =============================================================================

from sqlalchemy import create_engine
# 'create_engine' is the SQLAlchemy function that creates a connection
# to the database. It takes a connection string (URL) and returns an
# engine object that knows HOW to talk to the database.

from sqlalchemy.ext.declarative import declarative_base
# 'declarative_base' creates a base class. Every database TABLE we define
# will inherit from this Base. SQLAlchemy uses it to track all our models
# and know which tables to create in the database.

from sqlalchemy.orm import sessionmaker
# 'sessionmaker' creates a factory for database sessions.
# A "session" is a temporary workspace — like opening a conversation
# with the database. You use it to read/write data, then close it.

import os
# We import 'os' to read environment variables (like DATABASE_URL from .env)

from dotenv import load_dotenv
# 'load_dotenv' reads the .env file and loads its key=value pairs
# into environment variables so os.getenv() can access them.

# ─────────────────────────────────────────────────────────────────────────────
# Load .env file
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()
# This reads the .env file in our project root and makes all variables
# inside it available via os.getenv(). MUST be called before os.getenv().

# ─────────────────────────────────────────────────────────────────────────────
# Database URL
# ─────────────────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./risk_manager.db")
# os.getenv("DATABASE_URL") tries to read DATABASE_URL from environment.
# The second argument "sqlite:///./risk_manager.db" is the DEFAULT value
# if DATABASE_URL is not set in .env.
#
# SQLite URL format:  sqlite:///./filename.db
#   - 'sqlite' = database type
#   - '///' = relative path (3 slashes)
#   - './risk_manager.db' = file in current directory
#
# PostgreSQL URL format: postgresql://user:password@localhost/dbname
# To switch to PostgreSQL later, just set DATABASE_URL in .env!

# ─────────────────────────────────────────────────────────────────────────────
# Create Engine
# ─────────────────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    # connect_args is SQLite-specific.
    # By default, SQLite only allows one thread to use a connection.
    # FastAPI handles many requests simultaneously (multiple threads),
    # so we disable that restriction with check_same_thread=False.
    # For PostgreSQL this is NOT needed, so we use an empty dict {}.
)
# The engine doesn't open a connection immediately — it just stores the
# configuration. Connections are opened only when we actually need them.

# ─────────────────────────────────────────────────────────────────────────────
# Session Factory
# ─────────────────────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    # autocommit=False means we control when to COMMIT (save) changes.
    # We must explicitly call db.commit() to save changes.
    # This gives us control and lets us rollback on errors.

    autoflush=False,
    # autoflush=False means SQLAlchemy won't automatically send pending
    # changes to the DB before each query. We control this manually.
    # This prevents accidental partial writes.

    bind=engine
    # bind=engine tells the session which database engine to use.
    # Every session created from this factory will connect to our DB.
)
# SessionLocal is a CLASS (not an instance). To open a session, you call:
#   db = SessionLocal()   ← opens a session
#   db.close()            ← closes it

# ─────────────────────────────────────────────────────────────────────────────
# Base Class for Models
# ─────────────────────────────────────────────────────────────────────────────
Base = declarative_base()
# Base is the parent class for ALL our database table definitions.
# When we write:
#   class User(Base):
#       __tablename__ = "users"
#       ...
# SQLAlchemy knows this class represents the "users" table.


# ─────────────────────────────────────────────────────────────────────────────
# Database Dependency (FastAPI Dependency Injection)
# ─────────────────────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI Dependency — provides a database session to each route.

    How it works:
    1. Opens a new DB session for the incoming request
    2. 'yields' (hands) that session to the route function
    3. After the route finishes (success OR error), closes the session

    Usage in a route:
        @router.get("/something")
        def my_route(db: Session = Depends(get_db)):
            # 'db' is now an open database session
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    # Opens a new session — like starting a conversation with the database.

    try:
        yield db
        # 'yield' turns this function into a generator.
        # FastAPI calls next() on it to get 'db', injects it into the route,
        # and then resumes here (after the yield) when the route is done.
        # This pattern is called "dependency injection".

    finally:
        db.close()
        # 'finally' runs ALWAYS — even if an exception/error occurred.
        # This guarantees the session is closed and resources are freed.
        # Without this, database connections would leak!
