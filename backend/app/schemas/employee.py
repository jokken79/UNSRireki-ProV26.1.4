"""Employee schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.models.models import EmploymentType, HousingType


class EmployeeBase(BaseModel):
    """Base employee fields (from DBStaffX)."""
    employee_number: int = Field(..., description="社員№")
    status: str = Field(default="在職中", description="在職中/退社")
    office: Optional[str] = Field(None, max_length=50, description="事務所")

    # Personal
    full_name: str = Field(..., max_length=100, description="氏名")
    name_kana: Optional[str] = Field(None, max_length=100, description="カナ")
    gender: Optional[str] = Field(None, max_length=10, description="性別")
    nationality: Optional[str] = Field(None, max_length=50, description="国籍")
    birth_date: Optional[date] = Field(None, description="生年月日")

    # Visa
    visa_expiry: Optional[date] = Field(None, description="ビザ期限")
    visa_type: Optional[str] = Field(None, max_length=100, description="ビザ種類")

    # Family
    has_spouse: Optional[bool] = Field(None, description="配偶者")

    # Address
    postal_code: Optional[str] = Field(None, max_length=10, description="〒")
    address: Optional[str] = Field(None, description="住所")
    building_name: Optional[str] = Field(None, max_length=100, description="建物名")

    # Dates
    hire_date: Optional[date] = Field(None, description="入社日")
    termination_date: Optional[date] = Field(None, description="退社日")

    # Employment
    employment_type: EmploymentType = Field(..., description="派遣 or 請負")

    # Housing
    housing_type: Optional[HousingType] = None
    apartment_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    """Create employee request (usually from approved 入社連絡票)."""
    joining_notice_id: Optional[int] = None
    candidate_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    """Update employee request."""
    status: Optional[str] = None
    office: Optional[str] = None
    full_name: Optional[str] = None
    name_kana: Optional[str] = None
    visa_expiry: Optional[date] = None
    visa_type: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    building_name: Optional[str] = None
    termination_date: Optional[date] = None
    housing_type: Optional[HousingType] = None
    apartment_id: Optional[int] = None
    photo_url: Optional[str] = None


class HakenAssignmentBase(BaseModel):
    """派遣社員 assignment fields (from DBGenzaiX)."""
    status: str = Field(default="在職中", description="現在")

    # Assignment
    client_company_id: Optional[int] = Field(None, description="派遣先ID")
    client_company: Optional[str] = Field(None, max_length=200, description="派遣先")
    assignment_location: Optional[str] = Field(None, max_length=200, description="配属先")
    assignment_line: Optional[str] = Field(None, max_length=100, description="配属ライン")
    job_description: Optional[str] = Field(None, description="仕事内容")

    # Financial
    hourly_rate: Optional[int] = Field(None, ge=0, description="時給")
    hourly_rate_history: Optional[str] = Field(None, description="時給改定")
    billing_rate: Optional[int] = Field(None, ge=0, description="請求単価")
    billing_rate_history: Optional[str] = Field(None, description="請求改定")
    profit_margin: Optional[int] = Field(None, description="差額利益")

    # Insurance
    standard_salary: Optional[int] = Field(None, description="標準報酬")
    health_insurance: Optional[int] = Field(None, description="健康保険")
    nursing_insurance: Optional[int] = Field(None, description="介護保険")
    pension: Optional[int] = Field(None, description="厚生年金")
    social_insurance_enrolled: Optional[bool] = Field(None, description="社保加入")

    # Apartment
    apartment_name: Optional[str] = Field(None, max_length=100, description="ｱﾊﾟｰﾄ")
    move_in_date: Optional[date] = Field(None, description="入居")
    move_out_date: Optional[date] = Field(None, description="退去")

    # Dates
    start_date: Optional[date] = Field(None, description="入社日")
    end_date: Optional[date] = Field(None, description="退社日")
    current_hire_date: Optional[date] = Field(None, description="現入社")

    # License
    license_type: Optional[str] = Field(None, max_length=100, description="免許種類")
    license_expiry: Optional[date] = Field(None, description="免許期限")
    commute_method: Optional[str] = Field(None, max_length=50, description="通勤方法")
    optional_insurance_expiry: Optional[date] = Field(None, description="任意保険期限")

    # Certifications
    japanese_certification: Optional[str] = Field(None, max_length=50, description="日本語検定")
    career_up_5th_year: Optional[date] = Field(None, description="キャリアアップ5年目")

    notes: Optional[str] = None


class HakenAssignmentCreate(HakenAssignmentBase):
    """Create 派遣社員 assignment."""
    employee_id: int


class UkeoiAssignmentBase(BaseModel):
    """請負社員 assignment fields (from DBUkeoiX)."""
    status: str = Field(default="在職中", description="現在")

    # Work
    job_type: Optional[str] = Field(None, max_length=200, description="請負業務")

    # Financial
    hourly_rate: Optional[int] = Field(None, ge=0, description="時給")
    hourly_rate_history: Optional[str] = Field(None, description="時給改定")
    profit_margin: Optional[int] = Field(None, description="差額利益")

    # Insurance
    standard_salary: Optional[int] = Field(None, description="標準報酬")
    health_insurance: Optional[int] = Field(None, description="健康保険")
    nursing_insurance: Optional[int] = Field(None, description="介護保険")
    pension: Optional[int] = Field(None, description="厚生年金")
    social_insurance_enrolled: Optional[bool] = Field(None, description="社保加入")

    # Transportation
    commute_distance: Optional[Decimal] = Field(None, description="通勤距離")
    transport_allowance: Optional[int] = Field(None, description="交通費")

    # Apartment
    apartment_name: Optional[str] = Field(None, max_length=100, description="ｱﾊﾟｰﾄ")
    move_in_date: Optional[date] = Field(None, description="入居")
    move_out_date: Optional[date] = Field(None, description="退去")

    # Dates
    start_date: Optional[date] = Field(None, description="入社日")
    end_date: Optional[date] = Field(None, description="退社日")

    # Banking
    bank_account_name: Optional[str] = Field(None, max_length=100, description="口座名義")
    bank_name: Optional[str] = Field(None, max_length=100, description="銀行名")
    branch_number: Optional[str] = Field(None, max_length=10, description="支店番号")
    branch_name: Optional[str] = Field(None, max_length=100, description="支店名")
    account_number: Optional[str] = Field(None, max_length=20, description="口座番号")

    notes: Optional[str] = None


class UkeoiAssignmentCreate(UkeoiAssignmentBase):
    """Create 請負社員 assignment."""
    employee_id: int


class HakenAssignmentResponse(HakenAssignmentBase):
    """派遣社員 assignment response."""
    id: int
    employee_id: int
    visa_alert: Optional[str]
    entry_request: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UkeoiAssignmentResponse(UkeoiAssignmentBase):
    """請負社員 assignment response."""
    id: int
    employee_id: int
    visa_alert: Optional[str]
    entry_request: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeBase):
    """Employee response."""
    id: int
    joining_notice_id: Optional[int]
    candidate_id: Optional[int]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    haken_assignment: Optional[HakenAssignmentResponse] = None
    ukeoi_assignment: Optional[UkeoiAssignmentResponse] = None

    class Config:
        from_attributes = True
