"""
Create initial admin user script.

Usage:
    python scripts/create_admin.py

This script creates the initial super_admin user for the UNS Rirekisho Pro system.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.models import User, UserRole
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user():
    """Create the initial admin user."""

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Admin user already exists!")
            return

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@universal-kikaku.co.jp",
            hashed_password=pwd_context.hash("Admin@123!"),
            full_name="System Administrator",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )

        session.add(admin_user)
        await session.commit()

        print("\n" + "=" * 50)
        print("Initial admin user created successfully!")
        print("=" * 50)
        print(f"Username: admin")
        print(f"Password: Admin@123!")
        print(f"Role: super_admin")
        print("=" * 50)
        print("\nIMPORTANT: Please change this password immediately after first login!")
        print("=" * 50 + "\n")


async def main():
    """Main entry point."""
    try:
        await create_admin_user()
    except Exception as e:
        print(f"Error creating admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
