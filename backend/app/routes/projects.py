# =============================================================================
# routes/projects.py — Project Management Routes
# =============================================================================
# CRUD endpoints for managing projects:
#   POST   /projects         → Create a new project
#   GET    /projects         → List all projects (for logged-in user)
#   GET    /projects/{id}    → Get one project by ID
#   DELETE /projects/{id}    → Delete a project
#
# ALL routes here require authentication (JWT token).
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import Project, Risk
from app.schemas.schemas import ProjectCreate, ProjectResponse, ProjectSummary
from app.services.auth_service import get_current_user
# get_current_user → our auth dependency. If JWT is missing or invalid,
# FastAPI returns 401 before the route function even runs.

router = APIRouter(
    prefix="/projects",
    # All routes get /projects prefix:
    # @router.post("/") becomes POST /projects
    # @router.get("/{id}") becomes GET /projects/{id}

    tags=["Projects"],
    # Groups these routes under "Projects" in Swagger UI.
)


# =============================================================================
# ENDPOINT 1: Create a new project
# POST /projects
# =============================================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_project(
    project_data: ProjectCreate,
    # project_data → validated request body. Fields:
    # name (required), description, objective, technologies, context (all optional)

    db: Session = Depends(get_db),
    # db → open SQLAlchemy session for this request.

    current_user_id: int = Depends(get_current_user)
    # current_user_id → the ID of the logged-in user, extracted from JWT.
    # If no valid JWT, FastAPI returns 401 before this function runs.
    # This is how we associate the new project with the correct user.
):
    """
    Create a new project for the authenticated user.

    Requires: Authorization: Bearer <token>
    Request body: { "name": "...", "description": "...", "technologies": [...], ... }
    Response: Full project object with id and created_at.
    """

    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        objective=project_data.objective,
        technologies=project_data.technologies,
        context=project_data.context,
        owner_id=current_user_id,
        # owner_id → from JWT token. Links this project to the logged-in user.
        # This ensures users can only see their own projects.
        # overall_risk_score → starts as None (set after AI analysis)
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    # Standard SQLAlchemy pattern:
    # add() → stage the object
    # commit() → write to database
    # refresh() → reload from DB to get auto-assigned id, created_at, etc.

    return new_project


# =============================================================================
# ENDPOINT 2: List all projects for logged-in user
# GET /projects
# =============================================================================

@router.get(
    "",
    response_model=List[ProjectSummary]
)
@router.get(
    "/",
    response_model=List[ProjectSummary],
    include_in_schema=False
    # response_model=List[ProjectSummary] → returns an ARRAY of ProjectSummary objects.
    # We use ProjectSummary (not full ProjectResponse) to keep the list lightweight.
    # No need to send the full 'context' text in every list item.
)
def get_projects(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get all projects belonging to the currently logged-in user.

    Users can ONLY see their own projects — not other users' projects.
    This is enforced by filtering with owner_id = current_user_id.
    """

    projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user_id)
        # WHERE owner_id = <logged-in user's ID>
        # Critical security filter: users CANNOT see each other's projects.

        .order_by(Project.created_at.desc())
        # ORDER BY created_at DESC → newest projects first.
        # .desc() = descending order.

        .all()
        # .all() → execute the query and return ALL matching rows as a list.
    )

    # Add risk_count to each project for the summary view
    result = []
    for project in projects:
        risk_count = db.query(Risk).filter(Risk.project_id == project.id).count()
        # .count() → returns the number of matching rows (faster than fetching all rows).
        # Equivalent to: SELECT COUNT(*) FROM risks WHERE project_id = ?

        # Create a dict from the project's attributes + add risk_count
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "overall_risk_score": project.overall_risk_score,
            "created_at": project.created_at,
            "risk_count": risk_count,
        }
        result.append(ProjectSummary(**project_dict))
        # ProjectSummary(**project_dict) → creates a Pydantic object from the dict.
        # ** (double star) "unpacks" the dict as keyword arguments.

    return result


# =============================================================================
# ENDPOINT 3: Get a single project by ID
# GET /projects/{id}
# =============================================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: int,
    # project_id → extracted from the URL path.
    # For GET /projects/5, project_id = 5.
    # FastAPI auto-converts the URL string "5" to int.
    # If the URL has "abc" (not a number), FastAPI returns 422 validation error.

    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get full details of a single project.

    Only the owner can access their project.
    HTTP 404 if project not found.
    HTTP 403 if project belongs to a different user.
    """

    project = db.query(Project).filter(Project.id == project_id).first()
    # Query by project ID. .first() returns None if not found.

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            # 404 → "Resource not found"
            detail=f"Project with id {project_id} not found."
        )

    if project.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            # 403 Forbidden → "You don't have permission to access this resource."
            # 403 vs 404: We use 403 (not 404) when the resource EXISTS but the
            # user doesn't have permission. Some argue 404 is safer to prevent
            # revealing if a resource exists. For our MVP, 403 is fine.
            detail="You don't have permission to access this project."
        )

    return project


# =============================================================================
# ENDPOINT 4: Delete a project
# DELETE /projects/{id}
# =============================================================================

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
    # 204 No Content → "Action completed successfully, nothing to return."
    # Standard HTTP code for successful DELETE operations.
    # We don't send a response body, just the 204 status.
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Delete a project and ALL its associated risks (cascade delete).

    Only the project owner can delete it.
    """

    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found."
        )

    if project.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this project."
        )

    db.delete(project)
    # db.delete() → stages the project for deletion.
    # Because of cascade="all, delete-orphan" in the Project→Risk relationship,
    # all associated risks are ALSO deleted automatically.

    db.commit()
    # db.commit() → executes the DELETE in the database.

    return None
    # Returning None with status_code=204 means: "success, nothing to return."
    # FastAPI handles this correctly — sends empty 204 response.
