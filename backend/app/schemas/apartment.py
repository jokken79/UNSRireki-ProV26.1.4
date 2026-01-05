"""Pydantic schemas for company apartments."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CompanyApartmentBase(BaseModel):
    """Base schema for company apartment."""
    name: str
    postal_code: Optional[str] = None
    address: Optional[str] = None
    building_name: Optional[str] = None
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    monthly_rent: Optional[Decimal] = None
    notes: Optional[str] = None


class CompanyApartmentCreate(CompanyApartmentBase):
    """Schema for creating a company apartment."""
    current_occupants: int = 0
    is_active: bool = True


class CompanyApartmentUpdate(BaseModel):
    """Schema for updating a company apartment."""
    name: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    building_name: Optional[str] = None
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    current_occupants: Optional[int] = None
    monthly_rent: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyApartmentResponse(CompanyApartmentBase):
    """Schema for company apartment response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    current_occupants: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @property
    def vacancy(self) -> int:
        """Calculate available vacancy."""
        if self.capacity is None:
            return 0
        return self.capacity - self.current_occupants
