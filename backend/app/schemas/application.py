"""Application (申請) schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.models import ApplicationStatus


class ApplicationBase(BaseModel):
    """Base application fields."""
    candidate_id: int
    client_company_id: Optional[int] = None
    client_company_name: Optional[str] = Field(None, max_length=200, description="派遣先")


class ApplicationCreate(ApplicationBase):
    """Create application request."""
    pass


class ApplicationUpdate(BaseModel):
    """Update application request."""
    status: Optional[ApplicationStatus] = None
    result_notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    """Application response."""
    id: int
    presented_at: Optional[datetime]
    status: ApplicationStatus
    result_at: Optional[datetime]
    result_notes: Optional[str]
    created_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True
