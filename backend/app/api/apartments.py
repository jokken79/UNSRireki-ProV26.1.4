"""API endpoints for company apartments (社宅) management."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user, require_staff
from app.models.models import CompanyApartment, Employee, User
from app.schemas.schemas import (
    CompanyApartmentCreate,
    CompanyApartmentUpdate,
    CompanyApartmentResponse,
)

router = APIRouter()


@router.get("", response_model=list[CompanyApartmentResponse])
async def list_apartments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    has_vacancy: Optional[bool] = None,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """List all company apartments with optional filtering."""
    query = select(CompanyApartment)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            CompanyApartment.name.ilike(search_filter)
            | CompanyApartment.address.ilike(search_filter)
        )

    if is_active is not None:
        query = query.where(CompanyApartment.is_active == is_active)

    if has_vacancy is True:
        query = query.where(CompanyApartment.current_occupants < CompanyApartment.capacity)
    elif has_vacancy is False:
        query = query.where(CompanyApartment.current_occupants >= CompanyApartment.capacity)

    query = query.order_by(CompanyApartment.name).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{apartment_id}", response_model=CompanyApartmentResponse)
async def get_apartment(
    apartment_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get a single apartment by ID."""
    result = await db.execute(
        select(CompanyApartment).where(CompanyApartment.id == apartment_id)
    )
    apartment = result.scalar_one_or_none()

    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    return apartment


@router.post("", response_model=CompanyApartmentResponse, status_code=201)
async def create_apartment(
    apartment_data: CompanyApartmentCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Create a new company apartment."""
    apartment = CompanyApartment(**apartment_data.model_dump())
    db.add(apartment)
    await db.commit()
    await db.refresh(apartment)
    return apartment


@router.put("/{apartment_id}", response_model=CompanyApartmentResponse)
async def update_apartment(
    apartment_id: int,
    apartment_data: CompanyApartmentUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Update a company apartment."""
    result = await db.execute(
        select(CompanyApartment).where(CompanyApartment.id == apartment_id)
    )
    apartment = result.scalar_one_or_none()

    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    for field, value in apartment_data.model_dump(exclude_unset=True).items():
        setattr(apartment, field, value)

    await db.commit()
    await db.refresh(apartment)
    return apartment


@router.delete("/{apartment_id}")
async def deactivate_apartment(
    apartment_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a company apartment (soft delete)."""
    result = await db.execute(
        select(CompanyApartment).where(CompanyApartment.id == apartment_id)
    )
    apartment = result.scalar_one_or_none()

    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    # Check if apartment has current occupants
    if apartment.current_occupants > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate apartment with current occupants"
        )

    apartment.is_active = False
    await db.commit()

    return {"message": "Apartment deactivated successfully"}


@router.get("/{apartment_id}/occupants")
async def get_apartment_occupants(
    apartment_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get list of employees living in this apartment."""
    result = await db.execute(
        select(CompanyApartment).where(CompanyApartment.id == apartment_id)
    )
    apartment = result.scalar_one_or_none()

    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    # Get employees assigned to this apartment
    employees_result = await db.execute(
        select(Employee)
        .where(Employee.apartment_id == apartment_id)
        .where(Employee.status == "active")
    )
    employees = employees_result.scalars().all()

    return {
        "apartment_id": apartment_id,
        "apartment_name": apartment.name,
        "capacity": apartment.capacity,
        "current_occupants": apartment.current_occupants,
        "vacancy": apartment.capacity - apartment.current_occupants if apartment.capacity else 0,
        "occupants": [
            {
                "id": emp.id,
                "employee_number": emp.employee_number,
                "full_name": emp.full_name,
                "employment_type": emp.employment_type.value if emp.employment_type else None,
            }
            for emp in employees
        ],
    }


@router.get("/stats/summary")
async def get_apartment_stats(
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get apartment statistics."""
    # Total apartments
    total_result = await db.execute(select(func.count(CompanyApartment.id)))
    total = total_result.scalar() or 0

    # Active apartments
    active_result = await db.execute(
        select(func.count(CompanyApartment.id)).where(CompanyApartment.is_active == True)
    )
    active = active_result.scalar() or 0

    # Total capacity
    capacity_result = await db.execute(
        select(func.sum(CompanyApartment.capacity)).where(CompanyApartment.is_active == True)
    )
    total_capacity = capacity_result.scalar() or 0

    # Total occupants
    occupants_result = await db.execute(
        select(func.sum(CompanyApartment.current_occupants)).where(CompanyApartment.is_active == True)
    )
    total_occupants = occupants_result.scalar() or 0

    return {
        "total_apartments": total,
        "active_apartments": active,
        "total_capacity": total_capacity,
        "total_occupants": total_occupants,
        "vacancy": total_capacity - total_occupants,
        "occupancy_rate": round((total_occupants / total_capacity * 100), 1) if total_capacity > 0 else 0,
    }
