"""Joining Notice (入社連絡票) API endpoints."""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user, require_staff, require_manager
from app.models.models import (
    User, Candidate, Application, JoiningNotice,
    Employee, HakenAssignment, UkeoiAssignment,
    JoiningNoticeStatus, CandidateStatus, EmploymentType, ApplicationStatus
)
from app.schemas.joining_notice import (
    JoiningNoticeCreate,
    JoiningNoticeUpdate,
    JoiningNoticeResponse,
    JoiningNoticeReject,
)

router = APIRouter()


@router.get("", response_model=List[JoiningNoticeResponse])
async def list_joining_notices(
    status: Optional[JoiningNoticeStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all joining notices."""
    query = select(JoiningNotice)

    if status:
        query = query.where(JoiningNotice.status == status)

    query = query.order_by(JoiningNotice.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{notice_id}", response_model=JoiningNoticeResponse)
async def get_joining_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single joining notice."""
    result = await db.execute(
        select(JoiningNotice).where(JoiningNotice.id == notice_id)
    )
    notice = result.scalar_one_or_none()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joining notice not found"
        )

    return notice


@router.post("", response_model=JoiningNoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_joining_notice(
    notice_data: JoiningNoticeCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new joining notice (入社連絡票).
    Should only be created for ACCEPTED applications.
    """
    # Verify candidate exists and is accepted
    result = await db.execute(
        select(Candidate).where(Candidate.id == notice_data.candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    if candidate.status != CandidateStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate must be accepted before creating joining notice"
        )

    # If application_id provided, verify it's accepted
    if notice_data.application_id:
        app_result = await db.execute(
            select(Application).where(Application.id == notice_data.application_id)
        )
        application = app_result.scalar_one_or_none()

        if not application or application.status != ApplicationStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application must be accepted"
            )

    # Create joining notice
    notice = JoiningNotice(
        **notice_data.model_dump(),
        status=JoiningNoticeStatus.DRAFT,
        created_by=current_user.id
    )
    db.add(notice)

    # Update candidate status
    candidate.status = CandidateStatus.PROCESSING

    await db.commit()
    await db.refresh(notice)

    return notice


@router.put("/{notice_id}", response_model=JoiningNoticeResponse)
async def update_joining_notice(
    notice_id: int,
    notice_data: JoiningNoticeUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Update a joining notice (only in DRAFT status)."""
    result = await db.execute(
        select(JoiningNotice).where(JoiningNotice.id == notice_id)
    )
    notice = result.scalar_one_or_none()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joining notice not found"
        )

    if notice.status != JoiningNoticeStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only edit joining notices in DRAFT status"
        )

    # Update fields
    update_data = notice_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notice, field, value)

    await db.commit()
    await db.refresh(notice)

    return notice


@router.post("/{notice_id}/submit", response_model=JoiningNoticeResponse)
async def submit_for_approval(
    notice_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Submit joining notice for manager approval."""
    result = await db.execute(
        select(JoiningNotice).where(JoiningNotice.id == notice_id)
    )
    notice = result.scalar_one_or_none()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joining notice not found"
        )

    if notice.status != JoiningNoticeStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joining notice is not in DRAFT status"
        )

    # Validate required fields
    if not notice.full_name or not notice.employment_type or not notice.housing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields"
        )

    if notice.housing_type == "shataku" and not notice.apartment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apartment is required for 社宅 housing type"
        )

    if notice.employment_type == EmploymentType.UKEOI:
        if not notice.bank_account_name or not notice.account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank information is required for 請負社員"
            )

    notice.status = JoiningNoticeStatus.PENDING
    notice.submitted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(notice)

    return notice


@router.post("/{notice_id}/approve", response_model=JoiningNoticeResponse)
async def approve_joining_notice(
    notice_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve joining notice and create employee.
    This is the critical step that converts a candidate to an employee.
    """
    result = await db.execute(
        select(JoiningNotice).where(JoiningNotice.id == notice_id)
    )
    notice = result.scalar_one_or_none()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joining notice not found"
        )

    if notice.status != JoiningNoticeStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joining notice is not pending approval"
        )

    # Generate next employee number
    max_emp_result = await db.execute(
        select(Employee.employee_number).order_by(Employee.employee_number.desc()).limit(1)
    )
    max_emp = max_emp_result.scalar_one_or_none()
    next_emp_number = (max_emp or 0) + 1

    # Create employee from joining notice
    employee = Employee(
        employee_number=next_emp_number,
        joining_notice_id=notice.id,
        candidate_id=notice.candidate_id,
        full_name=notice.full_name,
        name_kana=notice.name_kana,
        gender=notice.gender,
        nationality=notice.nationality,
        birth_date=notice.birth_date,
        visa_expiry=notice.visa_expiry,
        visa_type=notice.visa_type,
        postal_code=notice.postal_code,
        address=notice.address,
        building_name=notice.building_name,
        hire_date=notice.move_in_date or datetime.now(timezone.utc).date(),
        employment_type=notice.employment_type,
        housing_type=notice.housing_type,
        apartment_id=notice.apartment_id,
    )
    db.add(employee)
    await db.flush()  # Get employee ID

    # Create appropriate assignment based on employment type
    if notice.employment_type == EmploymentType.HAKEN:
        assignment = HakenAssignment(
            employee_id=employee.id,
            client_company_id=notice.assignment_company_id,
            client_company=notice.assignment_company,
            assignment_location=notice.assignment_location,
            assignment_line=notice.assignment_line,
            job_description=notice.job_description,
            hourly_rate=notice.hourly_rate,
            billing_rate=notice.billing_rate,
            move_in_date=notice.move_in_date,
            start_date=notice.move_in_date,
        )
        db.add(assignment)
    else:  # UKEOI
        assignment = UkeoiAssignment(
            employee_id=employee.id,
            hourly_rate=notice.hourly_rate,
            move_in_date=notice.move_in_date,
            start_date=notice.move_in_date,
            bank_account_name=notice.bank_account_name,
            bank_name=notice.bank_name,
            branch_number=notice.branch_number,
            branch_name=notice.branch_name,
            account_number=notice.account_number,
        )
        db.add(assignment)

    # Update notice status
    notice.status = JoiningNoticeStatus.APPROVED
    notice.approved_at = datetime.now(timezone.utc)
    notice.approved_by = current_user.id

    # Update candidate status
    candidate_result = await db.execute(
        select(Candidate).where(Candidate.id == notice.candidate_id)
    )
    candidate = candidate_result.scalar_one_or_none()
    if candidate:
        candidate.status = CandidateStatus.HIRED

    await db.commit()
    await db.refresh(notice)

    return notice


@router.post("/{notice_id}/reject", response_model=JoiningNoticeResponse)
async def reject_joining_notice(
    notice_id: int,
    reject_data: JoiningNoticeReject,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """Reject a joining notice."""
    result = await db.execute(
        select(JoiningNotice).where(JoiningNotice.id == notice_id)
    )
    notice = result.scalar_one_or_none()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joining notice not found"
        )

    if notice.status != JoiningNoticeStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joining notice is not pending approval"
        )

    notice.status = JoiningNoticeStatus.REJECTED
    notice.rejection_reason = reject_data.reason
    notice.approved_by = current_user.id

    await db.commit()
    await db.refresh(notice)

    return notice
