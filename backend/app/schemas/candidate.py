"""Candidate schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr

from app.models.models import CandidateStatus, DocumentType


class FamilyMember(BaseModel):
    """Family member structure."""
    name: Optional[str] = None
    relation: Optional[str] = None
    age: Optional[int] = None
    living_together: Optional[bool] = None
    address: Optional[str] = None


class WorkHistoryEntry(BaseModel):
    """Work history entry."""
    company_name: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class EmergencyContact(BaseModel):
    """Emergency contact info."""
    name: str
    relation: str
    phone: str


class CandidateBase(BaseModel):
    """Base candidate fields."""
    # Basic Information
    full_name: str = Field(..., min_length=1, max_length=100, description="氏名")
    name_kana: Optional[str] = Field(None, max_length=100, description="カナ")
    name_romanji: Optional[str] = Field(None, max_length=100, description="ローマ字")
    gender: Optional[str] = Field(None, max_length=10, description="性別")
    nationality: Optional[str] = Field(None, max_length=50, description="国籍")
    birth_date: Optional[date] = Field(None, description="生年月日")
    marital_status: Optional[str] = Field(None, max_length=20, description="配偶者")
    photo_url: Optional[str] = Field(None, max_length=500, description="証明写真 URL")

    # Contact
    postal_code: Optional[str] = Field(None, max_length=10, description="〒")
    address: Optional[str] = Field(None, description="住所")
    building_name: Optional[str] = Field(None, max_length=100, description="建物名")
    phone: Optional[str] = Field(None, max_length=20, description="電話番号")
    mobile: Optional[str] = Field(None, max_length=20, description="携帯電話")
    email: Optional[EmailStr] = None

    # Visa
    visa_type: Optional[str] = Field(None, max_length=100, description="ビザ種類")
    visa_expiry: Optional[date] = Field(None, description="ビザ期限")
    residence_card_number: Optional[str] = Field(None, max_length=50, description="在留カード番号")

    # Passport
    passport_number: Optional[str] = Field(None, max_length=50)
    passport_expiry: Optional[date] = None

    # Physical
    height: Optional[Decimal] = Field(None, description="身長(cm)")
    weight: Optional[Decimal] = Field(None, description="体重(kg)")
    shoe_size: Optional[Decimal] = Field(None, description="靴サイズ")
    waist: Optional[int] = Field(None, description="ウエスト(cm)")
    uniform_size: Optional[str] = Field(None, max_length=10, description="服のサイズ")
    blood_type: Optional[str] = Field(None, max_length=5, description="血液型")
    vision_right: Optional[Decimal] = Field(None, description="視力(右)")
    vision_left: Optional[Decimal] = Field(None, description="視力(左)")
    wears_glasses: Optional[bool] = Field(None, description="メガネ/コンタクト")
    dominant_hand: Optional[str] = Field(None, max_length=10, description="利き腕")

    # Emergency Contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    # Japanese Ability
    japanese_level: Optional[str] = Field(None, max_length=20, description="日本語検定")
    listening_level: Optional[str] = None
    speaking_level: Optional[str] = None
    reading_level: Optional[str] = None
    writing_level: Optional[str] = None

    # Education
    education_level: Optional[str] = None
    major: Optional[str] = None
    work_history: Optional[List[WorkHistoryEntry]] = None
    qualifications: Optional[List[str]] = None

    # Family
    family_members: Optional[List[FamilyMember]] = None

    # Self PR
    reason_for_applying: Optional[str] = None
    self_pr: Optional[str] = None

    # Notes
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Create candidate request."""
    legacy_id: Optional[int] = Field(None, description="履歴書ID from Access")


class CandidateUpdate(BaseModel):
    """Update candidate request (all fields optional)."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_kana: Optional[str] = None
    name_romanji: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    marital_status: Optional[str] = None
    photo_url: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    building_name: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    visa_type: Optional[str] = None
    visa_expiry: Optional[date] = None
    residence_card_number: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    japanese_level: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[CandidateStatus] = None
    interview_result: Optional[str] = None
    interview_notes: Optional[str] = None


class CandidateDocumentResponse(BaseModel):
    """Document response."""
    id: int
    document_type: DocumentType
    file_name: str
    file_url: str
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class CandidateResponse(CandidateBase):
    """Candidate response."""
    id: int
    legacy_id: Optional[int]
    status: CandidateStatus
    interview_result: Optional[str]
    interview_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    documents: List[CandidateDocumentResponse] = []

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Paginated candidate list response."""
    items: List[CandidateResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    id: int
    file_name: str
    file_url: str
    document_type: DocumentType
    uploaded_at: datetime
