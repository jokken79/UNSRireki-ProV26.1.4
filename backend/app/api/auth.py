"""Authentication API endpoints."""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    require_admin,
)
from app.models.models import User, RefreshToken, UserRole
from app.schemas.auth import (
    Token,
    UserLogin,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.core.limiter import limiter

router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT tokens."""
    # Find user
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.username})

    # Store refresh token
    token_record = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.fromtimestamp(decode_token(refresh_token)["exp"], tz=timezone.utc),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(token_record)
    await db.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    token: str = Query(..., description="Refresh token"),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Decode and validate
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Check if token is in database and not revoked
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.revoked == False
        )
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found or revoked",
        )

    # Get user
    username = payload.get("sub")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Revoke old refresh token
    token_record.revoked = True
    token_record.revoked_at = datetime.now(timezone.utc)

    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    # Store new refresh token
    new_token_record = RefreshToken(
        token=new_refresh_token,
        user_id=user.id,
        expires_at=datetime.fromtimestamp(decode_token(new_refresh_token)["exp"], tz=timezone.utc),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(new_token_record)
    await db.commit()

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user by revoking all refresh tokens."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked == False
        )
    )
    tokens = result.scalars().all()

    for token in tokens:
        token.revoked = True
        token.revoked_at = datetime.now(timezone.utc)

    await db.commit()
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)."""
    result = await db.execute(select(User))
    return result.scalars().all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin only)."""
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a user (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user
