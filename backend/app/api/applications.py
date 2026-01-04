"""Application (申請) API endpoints."""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user, require_staff
from app.models.models import (
    User, Candidate, Application, ApplicationStatus, CandidateStatus
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)

router = APIRouter()


@router.get("", response_model=List[ApplicationResponse])
async def list_applications(
    status: Optional[ApplicationStatus] = None,
    candidate_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all applications with optional filtering."""
    query = select(Application)

    if status:
        query = query.where(Application.status == status)

    if candidate_id:
        query = query.where(Application.candidate_id == candidate_id)

    query = query.order_by(Application.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single application."""
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return application


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new application (present candidate to 派遣先).
    This marks the candidate as "presented".
    """
    # Verify candidate exists
    result = await db.execute(
        select(Candidate).where(Candidate.id == application_data.candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Create application
    application = Application(
        **application_data.model_dump(),
        presented_at=datetime.now(timezone.utc),
        status=ApplicationStatus.PENDING,
        created_by=current_user.id
    )
    db.add(application)

    # Update candidate status
    candidate.status = CandidateStatus.PRESENTED

    await db.commit()
    await db.refresh(application)

    return application


@router.put("/{application_id}/result", response_model=ApplicationResponse)
async def record_result(
    application_id: int,
    result_data: ApplicationUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Record the result of an application (👍 accepted / 👎 rejected).
    If accepted, candidate status changes to 'accepted' and can proceed to 入社連絡票.
    If rejected, candidate status changes to 'rejected' but record is preserved.
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application result already recorded"
        )

    # Update application
    application.status = result_data.status
    application.result_at = datetime.now(timezone.utc)
    application.result_notes = result_data.result_notes

    # Update candidate status
    candidate_result = await db.execute(
        select(Candidate).where(Candidate.id == application.candidate_id)
    )
    candidate = candidate_result.scalar_one_or_none()

    if candidate:
        if result_data.status == ApplicationStatus.ACCEPTED:
            candidate.status = CandidateStatus.ACCEPTED
        elif result_data.status == ApplicationStatus.REJECTED:
            candidate.status = CandidateStatus.REJECTED

    await db.commit()
    await db.refresh(application)

    return application
