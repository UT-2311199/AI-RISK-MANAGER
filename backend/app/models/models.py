# =============================================================================
# models/models.py — Database Table Definitions
# =============================================================================
# This file defines our database tables using Python classes.
# Each class = one table. Each class attribute = one column.
# SQLAlchemy reads these classes and creates the actual SQL tables for us.
#
# Tables we define here:
#   1. User    → stores registered user accounts
#   2. Project → stores projects created by users
#   3. Risk    → stores AI-identified risks for each project
# =============================================================================

from sqlalchemy import (
    Column,        # Column() defines a single table column
    Integer,       # Integer data type  → stores whole numbers (1, 2, 3...)
    String,        # String data type   → stores text (VARCHAR in SQL)
    Text,          # Text data type     → stores long text (no length limit)
    Float,         # Float data type    → stores decimal numbers (8.5, 3.14)
    DateTime,      # DateTime data type → stores date + time values
    ForeignKey,    # ForeignKey() links a column to another table's column
    JSON           # JSON data type     → stores JSON objects/arrays as text
)

from sqlalchemy.orm import relationship
# 'relationship' defines the Python-level link between two related models.
# Example: user.projects gives us all projects belonging to that user.
# This is NOT a database column — it's a Python convenience feature.

from datetime import datetime, timezone
# 'datetime' lets us get the current date/time.
# 'timezone' lets us specify UTC timezone for consistency.

from app.database import Base
# We import Base from our database.py file.
# All our table classes MUST inherit from Base so SQLAlchemy can track them.


# =============================================================================
# TABLE 1: Users
# =============================================================================
class User(Base):
    """
    Represents the 'users' table in the database.
    Stores account information for registered users.
    """
    __tablename__ = "users"
    # __tablename__ tells SQLAlchemy the actual SQL table name.
    # This is what you'd see if you opened the database and ran: SELECT * FROM users;

    # ── Columns ──────────────────────────────────────────────────────────────

    id = Column(Integer, primary_key=True, index=True)
    # primary_key=True → This is the unique identifier for each row.
    # SQLAlchemy auto-increments this: first user gets id=1, second id=2, etc.
    # index=True → Creates a database index, making lookups by id very fast.

    email = Column(String(255), unique=True, index=True, nullable=False)
    # String(255) → up to 255 characters long (standard for email addresses).
    # unique=True → No two users can have the same email (enforced by DB).
    # index=True  → Fast lookups by email (used during login).
    # nullable=False → This field CANNOT be empty. DB will reject rows without it.

    hashed_password = Column(String(255), nullable=False)
    # We NEVER store plain-text passwords. We store a bcrypt hash of the password.
    # bcrypt hashes look like: "$2b$12$xyz..." — totally unreadable.
    # nullable=False → password is required.

    full_name = Column(String(255), nullable=True)
    # nullable=True → Full name is optional. User doesn't have to provide it.

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # default= → If no value is provided, use this value automatically.
    # lambda: datetime.now(timezone.utc) → A function that returns the CURRENT
    # UTC time when a new user row is inserted. Using UTC ensures consistency
    # regardless of server timezone.

    # ── Relationships ─────────────────────────────────────────────────────────

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    # relationship("Project") → Links User to Project model.
    # back_populates="owner" → In Project model, project.owner gives the User.
    #                          Here, user.projects gives all their Projects.
    # cascade="all, delete-orphan" → If a User is deleted, ALL their projects
    #   are automatically deleted too. "Orphan" projects can't exist without an owner.


# =============================================================================
# TABLE 2: Projects
# =============================================================================
class Project(Base):
    """
    Represents the 'projects' table in the database.
    Each project belongs to one user and can have many risks.
    """
    __tablename__ = "projects"

    # ── Columns ──────────────────────────────────────────────────────────────

    id = Column(Integer, primary_key=True, index=True)
    # Auto-incrementing unique ID for each project.

    name = Column(String(255), nullable=False)
    # The project name, e.g., "E-Commerce Platform v2".

    description = Column(Text, nullable=True)
    # A longer description of what the project does.
    # Text (not String) because descriptions can be very long.

    objective = Column(Text, nullable=True)
    # The business objective of the project.
    # e.g., "Increase online sales by 30% in Q4 2024"

    technologies = Column(JSON, nullable=True)
    # Stores a Python list as JSON in the database.
    # Example value: ["React", "FastAPI", "PostgreSQL"]
    # JSON type lets us store lists and dicts directly without needing extra tables.

    context = Column(Text, nullable=True)
    # Additional context or information the user provides for risk analysis.
    # e.g., "This app will store credit card data and user health records."
    # The AI uses this field to understand what to look for during risk analysis.

    overall_risk_score = Column(Float, nullable=True)
    # Stores the average/overall risk score after AI analysis.
    # Range: 1.0 to 10.0. Example: 7.5 means "High Risk overall".
    # nullable=True → No score exists until the user runs the first analysis.

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # Automatically set to the current UTC time when project is created.

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # ForeignKey("users.id") → This column references the 'id' column
    # in the 'users' table. This is how we link a project to its owner.
    # SQL: FOREIGN KEY (owner_id) REFERENCES users(id)

    # ── Relationships ─────────────────────────────────────────────────────────

    owner = relationship("User", back_populates="projects")
    # owner → gives us the User object who owns this project.
    # back_populates="projects" → mirrors the 'projects' relationship in User.
    # Usage: project.owner.email → gets the email of this project's owner.

    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    # risks → gives us a list of all Risk objects for this project.
    # cascade → deleting a project also deletes all its risks.


# =============================================================================
# TABLE 3: Risks
# =============================================================================
class Risk(Base):
    """
    Represents the 'risks' table in the database.
    Each risk is identified by the AI and belongs to one project.
    This is the core data model of the entire application.
    """
    __tablename__ = "risks"

    # ── Columns ──────────────────────────────────────────────────────────────

    id = Column(Integer, primary_key=True, index=True)
    # Auto-incrementing unique ID for each risk.

    title = Column(String(500), nullable=False)
    # Short name of the risk. e.g., "Sensitive Data Exposure"
    # String(500) → up to 500 chars (AI risk titles can be descriptive).

    category = Column(String(100), nullable=False)
    # The risk category. One of:
    # "Security", "Privacy", "Technical", "Financial",
    # "Operational", "Compliance", "Project", "AI/Ethical"

    severity = Column(String(50), nullable=False)
    # Severity level: "Low", "Medium", "High", or "Critical"
    # Determined by the AI based on impact and probability.

    probability = Column(String(50), nullable=False)
    # How likely the risk is to occur: "Low", "Medium", or "High"
    # e.g., "High" probability means this risk will almost certainly happen.

    impact = Column(String(50), nullable=False)
    # How bad the consequences would be if the risk occurs: "Low", "Medium", "High"
    # e.g., "High" impact means business-critical damage.

    risk_score = Column(Float, nullable=False)
    # Numerical risk score from 1.0 to 10.0.
    # Formula: Risk Score = Probability × Impact (scaled to 1-10).
    # Higher = more dangerous. Allows sorting risks by priority.

    explanation = Column(Text, nullable=False)
    # The AI's detailed explanation of WHY this is a risk.
    # e.g., "The application stores payment data without mentioning encryption,
    #         which could expose users to financial fraud if breached."
    # This makes risks understandable to non-technical users.

    mitigation = Column(JSON, nullable=True)
    # A JSON array of recommended actions to reduce this risk.
    # Example: ["Encrypt all PII", "Use HTTPS", "Add access logging"]
    # Stored as JSON so we can retrieve it as a Python list directly.

    status = Column(String(50), default="Open")
    # Current status of this risk. Possible values:
    # "Open"                 → Newly identified, not yet acted on
    # "Under Review"         → Team is analyzing this risk
    # "Mitigation in Progress" → Team is actively fixing it
    # "Resolved"             → Risk has been fixed/eliminated
    # "Accepted"             → Team knowingly accepts this risk
    # default="Open" → All newly found risks start as "Open".

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # Timestamp of when this risk was identified by the AI.

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    # ForeignKey → links this risk to the project it belongs to.
    # Every risk MUST belong to a project (nullable=False).

    # ── Relationships ─────────────────────────────────────────────────────────

    project = relationship("Project", back_populates="risks")
    # project → gives us the Project object this risk belongs to.
    # Usage: risk.project.name → gets the name of the project this risk is in.
