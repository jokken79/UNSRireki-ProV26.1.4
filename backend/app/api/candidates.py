"""Candidate API endpoints."""
from typing import List, Optional
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, require_staff
from app.models.models import User, Candidate, CandidateDocument, CandidateStatus, DocumentType
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    DocumentUploadResponse,
)

router = APIRouter()

@router.get("/debug/{candidate_id}")
async def debug_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Debug: Show model columns
    from sqlalchemy import inspect as sa_inspect
    mapper = sa_inspect(Candidate)
    columns = [c.key for c in mapper.columns]
    has_photo_url = 'photo_url' in columns

    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        return {"error": "not found", "model_columns": columns, "has_photo_url": has_photo_url}

    return {
        "id": candidate.id,
        "full_name": candidate.full_name,
        "photo_url": candidate.photo_url,
        "photo_url_type": type(candidate.photo_url).__name__,
        "model_columns": columns,
        "has_photo_url_column": has_photo_url,
    }




@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[CandidateStatus] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List candidates with pagination and filtering."""
    query = select(Candidate).options(selectinload(Candidate.documents))

    # Apply filters
    if status:
        query = query.where(Candidate.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Candidate.full_name.ilike(search_pattern)) |
            (Candidate.name_kana.ilike(search_pattern)) |
            (Candidate.nationality.ilike(search_pattern))
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Candidate.created_at.desc())

    result = await db.execute(query)
    candidates = result.scalars().all()

    return CandidateListResponse(
        items=candidates,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single candidate by ID."""
    result = await db.execute(
        select(Candidate).options(selectinload(Candidate.documents)).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Debug: Log photo_url
    print(f"DEBUG - Candidate {candidate_id} photo_url: {candidate.photo_url}")

    return candidate


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate (履歴書)."""
    candidate = Candidate(
        **candidate_data.model_dump(),
        status=CandidateStatus.REGISTERED,
        created_by=current_user.id
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)

    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Update a candidate."""
    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Update fields
    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)

    return candidate


@router.post("/{candidate_id}/documents", response_model=DocumentUploadResponse)
async def upload_document(
    candidate_id: int,
    file: UploadFile = File(...),
    document_type: DocumentType = Query(DocumentType.OTHER),
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document for a candidate."""
    # Verify candidate exists
    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, "candidates", str(candidate_id), unique_filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save file
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes"
        )

    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record
    file_url = f"/uploads/candidates/{candidate_id}/{unique_filename}"
    document = CandidateDocument(
        candidate_id=candidate_id,
        document_type=document_type,
        file_name=file.filename,
        file_url=file_url,
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return DocumentUploadResponse(
        id=document.id,
        file_name=document.file_name,
        file_url=document.file_url,
        document_type=document.document_type,
        uploaded_at=document.uploaded_at
    )


@router.get("/{candidate_id}/documents", response_model=List[DocumentUploadResponse])
async def list_documents(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents for a candidate."""
    result = await db.execute(
        select(CandidateDocument).where(CandidateDocument.candidate_id == candidate_id)
    )
    documents = result.scalars().all()

    return [
        DocumentUploadResponse(
            id=doc.id,
            file_name=doc.file_name,
            file_url=doc.file_url,
            document_type=doc.document_type,
            uploaded_at=doc.uploaded_at
        )
        for doc in documents
    ]


@router.delete("/{candidate_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    candidate_id: int,
    document_id: int,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document."""
    result = await db.execute(
        select(CandidateDocument).where(
            CandidateDocument.id == document_id,
            CandidateDocument.candidate_id == candidate_id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete file from storage
    file_path = os.path.join(settings.UPLOAD_DIR, document.file_url.lstrip("/uploads/"))
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete record
    await db.delete(document)
    await db.commit()
