"""Dashboard API endpoints."""
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    User, Candidate, Application, JoiningNotice, Employee,
    CandidateStatus, ApplicationStatus, JoiningNoticeStatus, EmploymentType
)

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics."""

    # Candidate stats
    total_candidates = await db.scalar(select(func.count(Candidate.id)))
    new_candidates = await db.scalar(
        select(func.count(Candidate.id)).where(
            Candidate.status == CandidateStatus.REGISTERED
        )
    )
    pending_candidates = await db.scalar(
        select(func.count(Candidate.id)).where(
            Candidate.status.in_([CandidateStatus.PRESENTED, CandidateStatus.ACCEPTED])
        )
    )

    # Application stats
    pending_applications = await db.scalar(
        select(func.count(Application.id)).where(
            Application.status == ApplicationStatus.PENDING
        )
    )

    # Joining notice stats
    pending_notices = await db.scalar(
        select(func.count(JoiningNotice.id)).where(
            JoiningNotice.status == JoiningNoticeStatus.PENDING
        )
    )
    draft_notices = await db.scalar(
        select(func.count(JoiningNotice.id)).where(
            JoiningNotice.status == JoiningNoticeStatus.DRAFT
        )
    )

    # Employee stats
    total_employees = await db.scalar(
        select(func.count(Employee.id)).where(Employee.status == "在職中")
    )
    haken_employees = await db.scalar(
        select(func.count(Employee.id)).where(
            Employee.employment_type == EmploymentType.HAKEN,
            Employee.status == "在職中"
        )
    )
    ukeoi_employees = await db.scalar(
        select(func.count(Employee.id)).where(
            Employee.employment_type == EmploymentType.UKEOI,
            Employee.status == "在職中"
        )
    )

    # Visa alerts (expiring within 90 days)
    ninety_days_from_now = datetime.now().date() + timedelta(days=90)
    visa_alerts = await db.scalar(
        select(func.count(Employee.id)).where(
            Employee.visa_expiry <= ninety_days_from_now,
            Employee.status == "在職中"
        )
    )

    return {
        "candidates": {
            "total": total_candidates or 0,
            "new": new_candidates or 0,
            "pending": pending_candidates or 0,
        },
        "applications": {
            "pending": pending_applications or 0,
        },
        "joining_notices": {
            "pending_approval": pending_notices or 0,
            "draft": draft_notices or 0,
        },
        "employees": {
            "total_active": total_employees or 0,
            "haken": haken_employees or 0,
            "ukeoi": ukeoi_employees or 0,
        },
        "alerts": {
            "visa_expiring_soon": visa_alerts or 0,
        },
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity for the dashboard."""

    # Recent candidates
    recent_candidates_result = await db.execute(
        select(Candidate.id, Candidate.full_name, Candidate.status, Candidate.created_at)
        .order_by(Candidate.created_at.desc())
        .limit(limit)
    )
    recent_candidates = [
        {
            "type": "candidate",
            "id": row.id,
            "name": row.full_name,
            "status": row.status.value,
            "timestamp": row.created_at.isoformat() if row.created_at else None,
        }
        for row in recent_candidates_result
    ]

    # Recent applications
    recent_apps_result = await db.execute(
        select(Application.id, Application.client_company_name, Application.status, Application.created_at)
        .order_by(Application.created_at.desc())
        .limit(limit)
    )
    recent_applications = [
        {
            "type": "application",
            "id": row.id,
            "company": row.client_company_name,
            "status": row.status.value,
            "timestamp": row.created_at.isoformat() if row.created_at else None,
        }
        for row in recent_apps_result
    ]

    # Recent approvals
    recent_approvals_result = await db.execute(
        select(JoiningNotice.id, JoiningNotice.full_name, JoiningNotice.status, JoiningNotice.approved_at)
        .where(JoiningNotice.status == JoiningNoticeStatus.APPROVED)
        .order_by(JoiningNotice.approved_at.desc())
        .limit(limit)
    )
    recent_approvals = [
        {
            "type": "approval",
            "id": row.id,
            "name": row.full_name,
            "status": row.status.value,
            "timestamp": row.approved_at.isoformat() if row.approved_at else None,
        }
        for row in recent_approvals_result
    ]

    return {
        "recent_candidates": recent_candidates,
        "recent_applications": recent_applications,
        "recent_approvals": recent_approvals,
    }
