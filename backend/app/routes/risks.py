# =============================================================================
# routes/risks.py — Risk Analysis & Management Routes
# =============================================================================
# This file contains the CORE endpoints of the application:
#
#   POST  /projects/{id}/analyze  → Trigger AI risk analysis (THE MAIN FEATURE)
#   GET   /projects/{id}/risks    → List all risks for a project
#   GET   /risks/{id}             → Get a single risk's full details
#   PATCH /risks/{id}/status      → Update a risk's status (tracking)
#   DELETE /risks/{id}            → Delete a single risk
#
# The /analyze endpoint is the heart of the entire application.
# It sends project data to Gemini, receives structured risks, saves to DB.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import asyncio
# asyncio is Python's async/await framework.
# We need it because analyze_project_risks() is an async function.

from app.database import get_db
from app.models.models import Project, Risk
from app.schemas.schemas import (
    RiskResponse,
    AnalyzeRequest,
    RiskStatusUpdate,
    AnalysisResponse
)
from app.services.auth_service import get_current_user
from app.services.ai_service import analyze_project_risks
# analyze_project_risks → the async function that calls Gemini API.

router = APIRouter(
    tags=["Risk Analysis"],
    # No prefix here — routes use different path structures:
    # /projects/{id}/analyze, /projects/{id}/risks, /risks/{id}
)

# Valid status values for risk tracking
VALID_STATUSES = [
    "Open",
    "Under Review",
    "Mitigation in Progress",
    "Resolved",
    "Accepted"
]
# We validate user-provided status against this list.
# This prevents arbitrary strings from being stored in the database.


# =============================================================================
# ENDPOINT 1: Trigger AI Risk Analysis (THE CORE ENDPOINT)
# POST /projects/{project_id}/analyze
# =============================================================================

@router.post(
    "/projects/{project_id}/analyze",
    response_model=AnalysisResponse
)
async def analyze_risk(
    # 'async def' → This route function is asynchronous because it calls
    # 'await analyze_project_risks(...)' inside. Any function using 'await'
    # MUST be declared with 'async def'.

    project_id: int,
    # Extracted from URL: POST /projects/5/analyze → project_id = 5

    request_body: AnalyzeRequest,
    # Optional request body with 'additional_context' field.
    # Client can send: {} or {"additional_context": "Focus on GDPR risks"}

    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    ⭐ THE MAIN ENDPOINT ⭐

    Analyzes a project with Gemini AI and saves identified risks to the database.

    Full flow:
    1. Verify project exists and belongs to current user
    2. Collect all project data (name, description, technologies, context)
    3. Call Gemini AI with structured prompt
    4. Receive JSON list of risks from Gemini
    5. Save each risk to the database
    6. Calculate overall project risk score
    7. Update the project's overall_risk_score
    8. Return all risks + score to client

    Expected duration: 5-15 seconds (Gemini API call time)
    """

    # ── Step 1: Find and validate the project ────────────────────────────────

    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found."
        )

    if project.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to analyze this project."
        )

    # ── Step 2: Build the context for AI ─────────────────────────────────────

    full_context = project.context or ""
    # Start with the project's stored context.

    if request_body.additional_context:
        # If the user added extra context in THIS request (not stored in project),
        # append it to the context we send to Gemini.
        full_context = f"{full_context}\n\nAdditional Analysis Focus:\n{request_body.additional_context}"
        # f-string with \n → newline character. Creates line breaks in the text.

    # ── Step 3: Call Gemini AI ────────────────────────────────────────────────

    try:
        ai_risks = await analyze_project_risks(
            # 'await' → pauses this async function and waits for analyze_project_risks
            # to complete. While waiting, FastAPI can handle other requests.
            # This is the benefit of async — the server isn't BLOCKED waiting for Gemini.

            project_name=project.name,
            description=project.description or "",
            objective=project.objective or "",
            technologies=project.technologies or [],
            context=full_context
        )
        # ai_risks is now a list of validated risk dicts from Gemini.

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            # 503 Service Unavailable → "A dependency (Gemini API) is unavailable."
            # More informative than 500 Internal Server Error.
            detail=f"AI analysis failed: {str(e)}"
        )

    # ── Step 4: Delete previous risks (fresh analysis) ───────────────────────

    db.query(Risk).filter(Risk.project_id == project_id).delete()
    # If the user runs analysis again, we want fresh results, not accumulated old ones.
    # DELETE FROM risks WHERE project_id = ?
    # .delete() deletes all matching rows in one SQL statement (efficient).

    # ── Step 5: Save each identified risk to the database ────────────────────

    saved_risks = []
    for risk_data in ai_risks:
        # Iterate over each risk dict returned by Gemini.

        new_risk = Risk(
            title=risk_data["title"],
            category=risk_data["category"],
            probability=risk_data["probability"],
            impact=risk_data["impact"],
            risk_score=risk_data["risk_score"],
            severity=risk_data["severity"],
            explanation=risk_data["explanation"],
            mitigation=risk_data["mitigation"],
            # mitigation is a list → stored as JSON in the DB column.
            status="Open",
            # All new risks start as "Open".
            project_id=project_id
        )
        db.add(new_risk)
        saved_risks.append(new_risk)
        # We add each risk to the DB session and also keep a local reference.

    # ── Step 6: Calculate the overall project risk score ─────────────────────

    if saved_risks:
        all_scores = [risk.risk_score for risk in saved_risks]
        # List comprehension: extracts risk_score from each Risk object.
        # e.g., [8.3, 5.0, 6.7, 3.3, 10.0]

        overall_score = sum(all_scores) / len(all_scores)
        # Calculate average: total / count.
        # e.g., (8.3 + 5.0 + 6.7 + 3.3 + 10.0) / 5 = 6.66

        overall_score = round(overall_score, 1)
        # Round to 1 decimal place.
    else:
        overall_score = 0.0

    # ── Step 7: Update the project's overall risk score ───────────────────────

    project.overall_risk_score = overall_score
    # Update the project object (in memory).

    db.commit()
    # db.commit() saves EVERYTHING: all new Risk rows + the project update.
    # SQLAlchemy batches all pending changes into one transaction.

    # Refresh all saved risks to get their auto-assigned IDs and created_at
    for risk in saved_risks:
        db.refresh(risk)
    # After commit, each risk has its DB-assigned id. We need to refresh
    # to access risk.id in the response.

    db.refresh(project)
    # Refresh project too to confirm the score was saved.

    # ── Step 8: Build and return the response ────────────────────────────────

    return AnalysisResponse(
        project_id=project.id,
        project_name=project.name,
        overall_risk_score=overall_score,
        total_risks=len(saved_risks),
        risks=[RiskResponse.model_validate(risk) for risk in saved_risks],
        # List comprehension: converts each SQLAlchemy Risk object to a
        # RiskResponse Pydantic model. model_validate() reads ORM attributes
        # because we have model_config = {"from_attributes": True}.

        message=f"Analysis complete. Found {len(saved_risks)} risks. Overall risk score: {overall_score}/10"
    )


# =============================================================================
# ENDPOINT 2: Get all risks for a project
# GET /projects/{project_id}/risks
# =============================================================================

@router.get(
    "/projects/{project_id}/risks",
    response_model=List[RiskResponse]
)
def get_project_risks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get all risks identified for a specific project.
    Results are sorted by risk_score descending (most critical first).
    """

    # Verify project exists and belongs to user
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if project.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    risks = (
        db.query(Risk)
        .filter(Risk.project_id == project_id)
        .order_by(Risk.risk_score.desc())
        # ORDER BY risk_score DESC → highest risk score (most critical) comes first.
        # This way the dashboard always shows the most important risks at the top.
        .all()
    )

    return risks


# =============================================================================
# ENDPOINT 3: Get a single risk by ID
# GET /risks/{risk_id}
# =============================================================================

@router.get(
    "/risks/{risk_id}",
    response_model=RiskResponse
)
def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Get full details of a single risk.
    Only accessible by the owner of the project this risk belongs to.
    """

    risk = db.query(Risk).filter(Risk.id == risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found.")

    # Verify the risk's project belongs to current user
    project = db.query(Project).filter(Project.id == risk.project_id).first()
    if not project or project.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return risk


# =============================================================================
# ENDPOINT 4: Update risk status
# PATCH /risks/{risk_id}/status
# =============================================================================

@router.patch(
    "/risks/{risk_id}/status",
    response_model=RiskResponse
)
def update_risk_status(
    risk_id: int,
    status_update: RiskStatusUpdate,
    # status_update → request body with {"status": "Resolved"}
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Update the tracking status of a risk.

    Valid statuses:
        "Open" → "Under Review" → "Mitigation in Progress" → "Resolved"
        Or: "Accepted" (team knowingly accepts the risk)

    This is the risk TRACKING feature — allows teams to manage risks over time.
    """

    # Validate the provided status
    if status_update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            # 400 Bad Request → "The request contains invalid data."
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        )

    risk = db.query(Risk).filter(Risk.id == risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found.")

    # Verify ownership through the parent project
    project = db.query(Project).filter(Project.id == risk.project_id).first()
    if not project or project.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    risk.status = status_update.status
    # Update the status field on the risk object.

    db.commit()
    # Save the change to the database.

    db.refresh(risk)
    # Reload the risk from DB to confirm the change was saved.

    return risk


# =============================================================================
# ENDPOINT 5: Delete a single risk
# DELETE /risks/{risk_id}
# =============================================================================

@router.delete(
    "/risks/{risk_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Delete a single risk from a project.
    Only the project owner can delete risks.
    """

    risk = db.query(Risk).filter(Risk.id == risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found.")

    project = db.query(Project).filter(Project.id == risk.project_id).first()
    if not project or project.owner_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    db.delete(risk)
    db.commit()

    return None
