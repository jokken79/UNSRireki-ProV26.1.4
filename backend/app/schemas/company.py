"""Pydantic schemas for client companies."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ClientCompanyBase(BaseModel):
    """Base schema for client company."""
    name: str
    name_kana: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    billing_rate_default: Optional[Decimal] = None
    notes: Optional[str] = None


class ClientCompanyCreate(ClientCompanyBase):
    """Schema for creating a client company."""
    is_active: bool = True


class ClientCompanyUpdate(BaseModel):
    """Schema for updating a client company."""
    name: Optional[str] = None
    name_kana: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    billing_rate_default: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientCompanyResponse(ClientCompanyBase):
    """Schema for client company response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
