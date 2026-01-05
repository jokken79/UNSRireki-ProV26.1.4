"""Employee API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, String
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, require_staff
from app.models.models import (
    User, Employee, HakenAssignment, UkeoiAssignment, EmploymentType
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    HakenAssignmentCreate,
    UkeoiAssignmentCreate,
)

router = APIRouter()


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    employment_type: Optional[EmploymentType] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List employees with filtering."""
    query = select(Employee).options(
        selectinload(Employee.haken_assignment),
        selectinload(Employee.ukeoi_assignment)
    )

    if employment_type:
        query = query.where(Employee.employment_type == employment_type)

    if status:
        query = query.where(Employee.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Employee.full_name.ilike(search_pattern)) |
            (Employee.name_kana.ilike(search_pattern)) |
            (Employee.employee_number.cast(String).ilike(search_pattern))
        )

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Employee.employee_number)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/haken", response_model=List[EmployeeResponse])
async def list_haken_employees(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all 派遣社員 (dispatch workers)."""
    query = select(Employee).options(
        selectinload(Employee.haken_assignment)
    ).where(Employee.employment_type == EmploymentType.HAKEN)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/ukeoi", response_model=List[EmployeeResponse])
async def list_ukeoi_employees(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all 請負社員 (contract workers)."""
    query = select(Employee).options(
        selectinload(Employee.ukeoi_assignment)
    ).where(Employee.employment_type == EmploymentType.UKEOI)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single employee with their assignment details."""
    result = await db.execute(
        select(Employee).options(
            selectinload(Employee.haken_assignment),
            selectinload(Employee.ukeoi_assignment)
        ).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Update an employee."""
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)

    return employee


@router.post("/{employee_id}/terminate", response_model=EmployeeResponse)
async def terminate_employee(
    employee_id: int,
    termination_date: str,  # ISO date format
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Terminate an employee (退社)."""
    from datetime import date

    result = await db.execute(
        select(Employee).options(
            selectinload(Employee.haken_assignment),
            selectinload(Employee.ukeoi_assignment)
        ).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Update employee
    employee.status = "退社"
    employee.termination_date = date.fromisoformat(termination_date)

    # Update assignment
    if employee.haken_assignment:
        employee.haken_assignment.status = "退社"
        employee.haken_assignment.end_date = employee.termination_date
    elif employee.ukeoi_assignment:
        employee.ukeoi_assignment.status = "退社"
        employee.ukeoi_assignment.end_date = employee.termination_date

    await db.commit()
    await db.refresh(employee)

    return employee


@router.get("/stats/summary")
async def get_employee_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get employee statistics."""
    # Total active employees
    total_result = await db.execute(
        select(func.count()).where(Employee.status == "在職中")
    )
    total_active = total_result.scalar()

    # Haken count
    haken_result = await db.execute(
        select(func.count()).where(
            Employee.employment_type == EmploymentType.HAKEN,
            Employee.status == "在職中"
        )
    )
    haken_count = haken_result.scalar()

    # Ukeoi count
    ukeoi_result = await db.execute(
        select(func.count()).where(
            Employee.employment_type == EmploymentType.UKEOI,
            Employee.status == "在職中"
        )
    )
    ukeoi_count = ukeoi_result.scalar()

    # Terminated count
    terminated_result = await db.execute(
        select(func.count()).where(Employee.status == "退社")
    )
    terminated_count = terminated_result.scalar()

    return {
        "total_active": total_active,
        "haken_count": haken_count,
        "ukeoi_count": ukeoi_count,
        "terminated_count": terminated_count,
    }
