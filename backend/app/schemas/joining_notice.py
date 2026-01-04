"""Joining Notice (入社連絡票) schemas."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.models import EmploymentType, HousingType, JoiningNoticeStatus


class JoiningNoticeBase(BaseModel):
    """Base joining notice fields."""
    employment_type: EmploymentType = Field(..., description="派遣 or 請負")

    # Personal info (inherited from candidate but editable)
    full_name: str = Field(..., max_length=100, description="氏名")
    name_kana: Optional[str] = Field(None, max_length=100, description="カナ")
    gender: Optional[str] = Field(None, max_length=10, description="性別")
    nationality: Optional[str] = Field(None, max_length=50, description="国籍")
    birth_date: Optional[date] = Field(None, description="生年月日")

    # Visa
    visa_type: Optional[str] = Field(None, max_length=100, description="ビザ種類")
    visa_expiry: Optional[date] = Field(None, description="ビザ期限")

    # Address
    postal_code: Optional[str] = Field(None, max_length=10, description="〒")
    address: Optional[str] = Field(None, description="住所")
    building_name: Optional[str] = Field(None, max_length=100, description="建物名")

    # Housing
    housing_type: HousingType = Field(..., description="社宅/自宅/賃貸/その他")
    apartment_id: Optional[int] = Field(None, description="社宅ID (if housing_type=shataku)")
    move_in_date: Optional[date] = Field(None, description="入居")

    # Assignment (mainly for 派遣)
    assignment_company_id: Optional[int] = Field(None, description="派遣先ID")
    assignment_company: Optional[str] = Field(None, max_length=200, description="派遣先")
    assignment_location: Optional[str] = Field(None, max_length=200, description="配属先")
    assignment_line: Optional[str] = Field(None, max_length=100, description="配属ライン")
    job_description: Optional[str] = Field(None, description="仕事内容")

    # Salary
    hourly_rate: Optional[int] = Field(None, ge=0, description="時給")
    billing_rate: Optional[int] = Field(None, ge=0, description="請求単価 (派遣 only)")

    # Banking (mainly for 請負)
    bank_account_name: Optional[str] = Field(None, max_length=100, description="口座名義")
    bank_name: Optional[str] = Field(None, max_length=100, description="銀行名")
    branch_number: Optional[str] = Field(None, max_length=10, description="支店番号")
    branch_name: Optional[str] = Field(None, max_length=100, description="支店名")
    account_number: Optional[str] = Field(None, max_length=20, description="口座番号")


class JoiningNoticeCreate(JoiningNoticeBase):
    """Create joining notice request."""
    application_id: Optional[int] = None
    candidate_id: int


class JoiningNoticeUpdate(BaseModel):
    """Update joining notice request."""
    full_name: Optional[str] = None
    name_kana: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    visa_type: Optional[str] = None
    visa_expiry: Optional[date] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    building_name: Optional[str] = None
    housing_type: Optional[HousingType] = None
    apartment_id: Optional[int] = None
    move_in_date: Optional[date] = None
    assignment_company_id: Optional[int] = None
    assignment_company: Optional[str] = None
    assignment_location: Optional[str] = None
    assignment_line: Optional[str] = None
    job_description: Optional[str] = None
    hourly_rate: Optional[int] = None
    billing_rate: Optional[int] = None
    bank_account_name: Optional[str] = None
    bank_name: Optional[str] = None
    branch_number: Optional[str] = None
    branch_name: Optional[str] = None
    account_number: Optional[str] = None


class JoiningNoticeResponse(JoiningNoticeBase):
    """Joining notice response."""
    id: int
    application_id: Optional[int]
    candidate_id: int
    status: JoiningNoticeStatus
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    approved_by: Optional[int]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class JoiningNoticeSubmit(BaseModel):
    """Submit joining notice for approval."""
    pass  # No additional fields needed


class JoiningNoticeApprove(BaseModel):
    """Approve joining notice."""
    pass  # Creates employee automatically


class JoiningNoticeReject(BaseModel):
    """Reject joining notice."""
    reason: str = Field(..., min_length=1, description="Rejection reason")
