"""
SQLAlchemy Models for UNS Rirekisho Pro v26.1.4

Based on legacy data sources:
- Access: T_履歴書 (Candidates/CV)
- Excel: DBStaffX (Employee Master)
- Excel: DBGenzaiX (派遣社員 - Dispatch Workers)
- Excel: DBUkeoiX (請負社員 - Contract Workers)
"""
from datetime import datetime, date
from decimal import Decimal
import enum

from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime, Date,
    Numeric, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================
# ENUMS
# ============================================

class UserRole(str, enum.Enum):
    """User roles for access control."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"      # Can approve 入社連絡票
    STAFF = "staff"          # Office staff
    VIEWER = "viewer"        # Read-only access


class CandidateStatus(str, enum.Enum):
    """Candidate workflow status."""
    REGISTERED = "registered"    # Just registered
    PRESENTED = "presented"      # Presented to 派遣先
    ACCEPTED = "accepted"        # Accepted by 派遣先
    REJECTED = "rejected"        # Rejected by 派遣先
    PROCESSING = "processing"    # 入社連絡票 in progress
    HIRED = "hired"              # Converted to employee


class ApplicationStatus(str, enum.Enum):
    """Application (申請) status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class JoiningNoticeStatus(str, enum.Enum):
    """入社連絡票 status."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EmploymentType(str, enum.Enum):
    """Type of employment."""
    HAKEN = "haken"      # 派遣社員 (Dispatch)
    UKEOI = "ukeoi"      # 請負社員 (Contract)


class HousingType(str, enum.Enum):
    """Type of housing."""
    SHATAKU = "shataku"  # 社宅 (Company housing)
    OWN = "own"          # 自宅 (Own home)
    RENTAL = "rental"    # 賃貸 (Rental)
    OTHER = "other"      # その他


class DocumentType(str, enum.Enum):
    """Document types."""
    RIREKISHO = "rirekisho"      # 履歴書/CV
    PHOTO = "photo"               # 証明写真
    ZAIRYU_CARD = "zairyu_card"  # 在留カード
    LICENSE = "license"           # 運転免許
    CONTRACT = "contract"         # 契約書
    OTHER = "other"


# ============================================
# USER & AUTHENTICATION
# ============================================

class User(Base):
    """System users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STAFF)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """JWT refresh tokens."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True))
    user_agent = Column(String(500))
    ip_address = Column(String(45))

    user = relationship("User", back_populates="refresh_tokens")


# ============================================
# CANDIDATES (履歴書)
# ============================================

class Candidate(Base):
    """
    Candidate/CV records.
    Based on Access T_履歴書 table.
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    legacy_id = Column(Integer, unique=True, index=True)  # 履歴書ID from Access

    # Basic Information (基本情報)
    full_name = Column(String(100), nullable=False, index=True)  # 氏名
    name_kana = Column(String(100))  # カナ
    name_romanji = Column(String(100))  # ローマ字
    gender = Column(String(10))  # 性別
    nationality = Column(String(50))  # 国籍
    birth_date = Column(Date)  # 生年月日
    marital_status = Column(String(20))  # 配偶者

    # Contact (連絡先)
    postal_code = Column(String(10))  # 〒
    address = Column(Text)  # 住所
    building_name = Column(String(100))  # 建物名
    phone = Column(String(20))  # 電話番号
    mobile = Column(String(20))  # 携帯電話
    email = Column(String(100))

    # Visa Information (ビザ情報)
    visa_type = Column(String(100))  # ビザ種類
    visa_expiry = Column(Date)  # ビザ期限
    residence_card_number = Column(String(50))  # 在留カード番号

    # Passport
    passport_number = Column(String(50))
    passport_expiry = Column(Date)

    # Physical Information (身体情報)
    height = Column(Numeric(5, 1))  # 身長(cm)
    weight = Column(Numeric(5, 1))  # 体重(kg)
    shoe_size = Column(Numeric(4, 1))  # 靴サイズ
    waist = Column(Integer)  # ウエスト(cm)
    uniform_size = Column(String(10))  # 服のサイズ
    blood_type = Column(String(5))  # 血液型
    vision_right = Column(Numeric(3, 1))  # 視力(右)
    vision_left = Column(Numeric(3, 1))  # 視力(左)
    wears_glasses = Column(Boolean)  # メガネ/コンタクト
    dominant_hand = Column(String(10))  # 利き腕

    # Emergency Contact (緊急連絡先)
    emergency_contact_name = Column(String(100))
    emergency_contact_relation = Column(String(50))
    emergency_contact_phone = Column(String(20))

    # Japanese Ability (日本語能力)
    japanese_level = Column(String(20))  # 日本語検定
    listening_level = Column(String(20))  # 聞く
    speaking_level = Column(String(20))  # 話す
    reading_level = Column(String(20))  # 読む
    writing_level = Column(String(20))  # 書く

    # Education & Work
    education_level = Column(String(50))  # 学歴
    major = Column(String(100))  # 専攻
    work_history = Column(JSON)  # 職歴 (array of objects)
    qualifications = Column(JSON)  # 資格 (array of strings)

    # Family (家族構成 - stored as JSON array)
    family_members = Column(JSON)

    # Self PR
    reason_for_applying = Column(Text)  # 志望動機
    self_pr = Column(Text)  # 自己PR

    # Notes
    notes = Column(Text)  # 備考

    # Status & Workflow
    status = Column(SQLEnum(CandidateStatus), default=CandidateStatus.REGISTERED)
    interview_result = Column(String(20))  # passed, failed, pending
    interview_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    documents = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate")
    joining_notices = relationship("JoiningNotice", back_populates="candidate")


class CandidateDocument(Base):
    """
    Documents attached to candidates.
    Migrated from Access 写真 (Attachment) field.
    """
    __tablename__ = "candidate_documents"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)  # Storage URL
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))

    candidate = relationship("Candidate", back_populates="documents")


# ============================================
# CLIENT COMPANIES (派遣先)
# ============================================

class ClientCompany(Base):
    """Client companies where workers are dispatched."""
    __tablename__ = "client_companies"

    id = Column(Integer, primary_key=True, index=True)
    legacy_id = Column(Integer, unique=True)  # 派遣先ID
    name = Column(String(200), nullable=False, index=True)  # 派遣先
    name_kana = Column(String(200))  # カナ
    company_type = Column(String(20))  # 'haken' or 'ukeoi'
    postal_code = Column(String(10))
    address = Column(Text)
    phone = Column(String(20))
    fax = Column(String(20))
    contact_person = Column(String(100))
    contact_email = Column(String(100))
    billing_rate_default = Column(Numeric(10, 2))  # Default billing rate
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    applications = relationship("Application", back_populates="client_company")
    haken_assignments = relationship("HakenAssignment", back_populates="client_company_rel")


# ============================================
# APPLICATIONS (申請)
# ============================================

class Application(Base):
    """
    Application records when presenting candidates to 派遣先.
    Tracks accept/reject results.
    """
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    client_company_id = Column(Integer, ForeignKey("client_companies.id"))
    client_company_name = Column(String(200))  # Denormalized for history

    presented_at = Column(DateTime(timezone=True))
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    result_at = Column(DateTime(timezone=True))
    result_notes = Column(Text)

    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    client_company = relationship("ClientCompany", back_populates="applications")
    joining_notice = relationship("JoiningNotice", back_populates="application", uselist=False)


# ============================================
# JOINING NOTICE (入社連絡票)
# ============================================

class JoiningNotice(Base):
    """
    入社連絡票 - Joining notification form.
    Created when candidate is accepted by 派遣先.
    Must be approved to create employee.
    """
    __tablename__ = "joining_notices"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    # Employment Type
    employment_type = Column(SQLEnum(EmploymentType), nullable=False)

    # Inherited from candidate (can be edited)
    full_name = Column(String(100), nullable=False)
    name_kana = Column(String(100))
    gender = Column(String(10))
    nationality = Column(String(50))
    birth_date = Column(Date)

    # Visa
    visa_type = Column(String(100))
    visa_expiry = Column(Date)

    # Address
    postal_code = Column(String(10))
    address = Column(Text)
    building_name = Column(String(100))

    # Housing
    housing_type = Column(SQLEnum(HousingType), nullable=False)
    apartment_id = Column(Integer, ForeignKey("company_apartments.id"))
    move_in_date = Column(Date)

    # Assignment (for 派遣)
    assignment_company_id = Column(Integer, ForeignKey("client_companies.id"))
    assignment_company = Column(String(200))
    assignment_location = Column(String(200))  # 配属先
    assignment_line = Column(String(100))  # 配属ライン
    job_description = Column(Text)  # 仕事内容

    # Salary
    hourly_rate = Column(Integer)  # 時給
    billing_rate = Column(Integer)  # 請求単価 (派遣 only)

    # Banking (請負 mainly)
    bank_account_name = Column(String(100))  # 口座名義
    bank_name = Column(String(100))  # 銀行名
    branch_number = Column(String(10))  # 支店番号
    branch_name = Column(String(100))  # 支店名
    account_number = Column(String(20))  # 口座番号

    # Workflow
    status = Column(SQLEnum(JoiningNoticeStatus), default=JoiningNoticeStatus.DRAFT)
    submitted_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    application = relationship("Application", back_populates="joining_notice")
    candidate = relationship("Candidate", back_populates="joining_notices")
    apartment = relationship("CompanyApartment")


# ============================================
# EMPLOYEES (社員)
# ============================================

class Employee(Base):
    """
    Employee master table.
    Based on Excel DBStaffX (17 columns).
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(Integer, unique=True, nullable=False, index=True)  # 社員№
    joining_notice_id = Column(Integer, ForeignKey("joining_notices.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    # Status
    status = Column(String(20), default="在職中")  # 在職中/退社
    office = Column(String(50))  # 事務所

    # Personal Information (from DBStaffX)
    full_name = Column(String(100), nullable=False, index=True)  # 氏名
    name_kana = Column(String(100))  # カナ
    gender = Column(String(10))  # 性別
    nationality = Column(String(50))  # 国籍
    birth_date = Column(Date)  # 生年月日

    # Visa
    visa_expiry = Column(Date)  # ビザ期限
    visa_type = Column(String(100))  # ビザ種類

    # Family
    has_spouse = Column(Boolean)  # 配偶者

    # Address
    postal_code = Column(String(10))  # 〒
    address = Column(Text)  # 住所
    building_name = Column(String(100))  # 建物名

    # Employment Dates
    hire_date = Column(Date)  # 入社日
    termination_date = Column(Date)  # 退社日

    # Photo
    photo_url = Column(String(500))

    # Employment Type (determines which assignment table to use)
    employment_type = Column(SQLEnum(EmploymentType), nullable=False)

    # Housing
    housing_type = Column(SQLEnum(HousingType))
    apartment_id = Column(Integer, ForeignKey("company_apartments.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    haken_assignment = relationship("HakenAssignment", back_populates="employee", uselist=False)
    ukeoi_assignment = relationship("UkeoiAssignment", back_populates="employee", uselist=False)
    apartment = relationship("CompanyApartment", back_populates="employees")


# ============================================
# HAKEN ASSIGNMENTS (派遣社員)
# ============================================

class HakenAssignment(Base):
    """
    派遣社員 assignment details.
    Based on Excel DBGenzaiX (42 columns).
    """
    __tablename__ = "haken_assignments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False)

    # Status
    status = Column(String(20), default="在職中")  # 現在

    # Assignment
    client_company_id = Column(Integer, ForeignKey("client_companies.id"))  # 派遣先ID
    client_company = Column(String(200))  # 派遣先
    assignment_location = Column(String(200))  # 配属先
    assignment_line = Column(String(100))  # 配属ライン
    job_description = Column(Text)  # 仕事内容

    # Financial (派遣 specific)
    hourly_rate = Column(Integer)  # 時給
    hourly_rate_history = Column(Text)  # 時給改定
    billing_rate = Column(Integer)  # 請求単価
    billing_rate_history = Column(Text)  # 請求改定
    profit_margin = Column(Integer)  # 差額利益

    # Insurance
    standard_salary = Column(Integer)  # 標準報酬
    health_insurance = Column(Integer)  # 健康保険
    nursing_insurance = Column(Integer)  # 介護保険
    pension = Column(Integer)  # 厚生年金
    social_insurance_enrolled = Column(Boolean)  # 社保加入

    # Apartment
    apartment_name = Column(String(100))  # ｱﾊﾟｰﾄ
    move_in_date = Column(Date)  # 入居
    move_out_date = Column(Date)  # 退去

    # Dates
    start_date = Column(Date)  # 入社日
    end_date = Column(Date)  # 退社日
    current_hire_date = Column(Date)  # 現入社

    # Visa Alert
    visa_alert = Column(String(50))  # ｱﾗｰﾄ(ﾋﾞｻﾞ更新)

    # License
    license_type = Column(String(100))  # 免許種類
    license_expiry = Column(Date)  # 免許期限
    commute_method = Column(String(50))  # 通勤方法
    optional_insurance_expiry = Column(Date)  # 任意保険期限

    # Certifications
    japanese_certification = Column(String(50))  # 日本語検定
    career_up_5th_year = Column(Date)  # キャリアアップ5年目

    # Entry Request
    entry_request = Column(String(50))  # 入社依頼

    notes = Column(Text)  # 備考

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="haken_assignment")
    client_company_rel = relationship("ClientCompany", back_populates="haken_assignments")


# ============================================
# UKEOI ASSIGNMENTS (請負社員)
# ============================================

class UkeoiAssignment(Base):
    """
    請負社員 assignment details.
    Based on Excel DBUkeoiX (36 columns).
    """
    __tablename__ = "ukeoi_assignments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False)

    # Status
    status = Column(String(20), default="在職中")  # 現在

    # Work
    job_type = Column(String(200))  # 請負業務

    # Financial
    hourly_rate = Column(Integer)  # 時給
    hourly_rate_history = Column(Text)  # 時給改定
    profit_margin = Column(Integer)  # 差額利益

    # Insurance
    standard_salary = Column(Integer)  # 標準報酬
    health_insurance = Column(Integer)  # 健康保険
    nursing_insurance = Column(Integer)  # 介護保険
    pension = Column(Integer)  # 厚生年金
    social_insurance_enrolled = Column(Boolean)  # 社保加入

    # Transportation
    commute_distance = Column(Numeric(5, 2))  # 通勤距離
    transport_allowance = Column(Integer)  # 交通費

    # Apartment
    apartment_name = Column(String(100))  # ｱﾊﾟｰﾄ
    move_in_date = Column(Date)  # 入居
    move_out_date = Column(Date)  # 退去

    # Dates
    start_date = Column(Date)  # 入社日
    end_date = Column(Date)  # 退社日

    # Visa Alert
    visa_alert = Column(String(50))  # ｱﾗｰﾄ(ﾋﾞｻﾞ更新)

    # Banking (請負 specific)
    bank_account_name = Column(String(100))  # 口座名義
    bank_name = Column(String(100))  # 銀行名
    branch_number = Column(String(10))  # 支店番号
    branch_name = Column(String(100))  # 支店名
    account_number = Column(String(20))  # 口座番号

    # Entry Request
    entry_request = Column(String(50))  # 入社依頼

    notes = Column(Text)  # 備考

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="ukeoi_assignment")


# ============================================
# COMPANY APARTMENTS (社宅)
# ============================================

class CompanyApartment(Base):
    """Company housing (社宅)."""
    __tablename__ = "company_apartments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    postal_code = Column(String(10))
    address = Column(Text)
    building_name = Column(String(100))
    room_number = Column(String(20))
    capacity = Column(Integer)
    current_occupants = Column(Integer, default=0)
    monthly_rent = Column(Numeric(10, 2))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="apartment")


# ============================================
# AUDIT LOG
# ============================================

class AuditLog(Base):
    """Audit trail for important actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # create, update, delete, approve, reject
    entity_type = Column(String(50), nullable=False)  # candidate, employee, joining_notice, etc.
    entity_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
