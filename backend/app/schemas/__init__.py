"""Pydantic schemas package."""
from app.schemas.auth import (
    Token,
    TokenPayload,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    DocumentUploadResponse,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)
from app.schemas.joining_notice import (
    JoiningNoticeCreate,
    JoiningNoticeUpdate,
    JoiningNoticeResponse,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    HakenAssignmentCreate,
    UkeoiAssignmentCreate,
)
from app.schemas.company import (
    ClientCompanyCreate,
    ClientCompanyUpdate,
    ClientCompanyResponse,
)
from app.schemas.apartment import (
    CompanyApartmentCreate,
    CompanyApartmentUpdate,
    CompanyApartmentResponse,
)

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    # Candidate
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "CandidateListResponse",
    "DocumentUploadResponse",
    # Application
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    # Joining Notice
    "JoiningNoticeCreate",
    "JoiningNoticeUpdate",
    "JoiningNoticeResponse",
    # Employee
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "HakenAssignmentCreate",
    "UkeoiAssignmentCreate",
    # Company
    "ClientCompanyCreate",
    "ClientCompanyUpdate",
    "ClientCompanyResponse",
    # Apartment
    "CompanyApartmentCreate",
    "CompanyApartmentUpdate",
    "CompanyApartmentResponse",
]
