"""API endpoints for client companies (派遣先) management."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, require_staff
from app.models.models import ClientCompany, User
from app.schemas import (
    ClientCompanyCreate,
    ClientCompanyUpdate,
    ClientCompanyResponse,
)

router = APIRouter()


@router.get("", response_model=list[ClientCompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """List all client companies with optional filtering."""
    query = select(ClientCompany)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            ClientCompany.name.ilike(search_filter)
            | ClientCompany.name_kana.ilike(search_filter)
        )

    if is_active is not None:
        query = query.where(ClientCompany.is_active == is_active)

    query = query.order_by(ClientCompany.name).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{company_id}", response_model=ClientCompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get a single company by ID."""
    result = await db.execute(
        select(ClientCompany).where(ClientCompany.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.post("", response_model=ClientCompanyResponse, status_code=201)
async def create_company(
    company_data: ClientCompanyCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Create a new client company."""
    company = ClientCompany(**company_data.model_dump())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.put("/{company_id}", response_model=ClientCompanyResponse)
async def update_company(
    company_id: int,
    company_data: ClientCompanyUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Update a client company."""
    result = await db.execute(
        select(ClientCompany).where(ClientCompany.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in company_data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}")
async def deactivate_company(
    company_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a client company (soft delete)."""
    result = await db.execute(
        select(ClientCompany).where(ClientCompany.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.is_active = False
    await db.commit()

    return {"message": "Company deactivated successfully"}


@router.get("/stats/summary")
async def get_company_stats(
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get company statistics."""
    # Total companies
    total_result = await db.execute(select(func.count(ClientCompany.id)))
    total = total_result.scalar() or 0

    # Active companies
    active_result = await db.execute(
        select(func.count(ClientCompany.id)).where(ClientCompany.is_active == True)
    )
    active = active_result.scalar() or 0

    return {
        "total": total,
        "active": active,
        "inactive": total - active,
    }
