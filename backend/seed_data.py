import asyncio
import logging
from dotenv import load_dotenv
import os

load_dotenv()

from app.core.database import init_db, async_session_maker
from app.models.models import User, UserRole, Candidate, CandidateStatus, EmploymentType, JoiningNotice, JoiningNoticeStatus
from app.core.security import get_password_hash
from sqlalchemy import select
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    logger.info("Initializing database...")
    await init_db()
    
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            logger.info("Creating admin user...")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin"),
                role=UserRole.SUPER_ADMIN,
                full_name="System Administrator",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Admin user created (admin/admin)")
        else:
            logger.info("Admin user already exists")

        # Create some dummy data for dashboard
        logger.info("Creating dummy data...")
        
        # Candidate 1
        result = await session.execute(select(Candidate).where(Candidate.full_name == "山田 太郎"))
        if not result.scalar_one_or_none():
            candidate1 = Candidate(
                full_name="山田 太郎",
                name_kana="ヤマダ タロウ",
                status=CandidateStatus.REGISTERED,
                gender="Male",
                birth_date=date(1990, 1, 1),
                created_by=1
            )
            session.add(candidate1)
        
        # Candidate 2 (Hired)
        result = await session.execute(select(Candidate).where(Candidate.full_name == "佐藤 花子"))
        if not result.scalar_one_or_none():
            candidate2 = Candidate(
                full_name="佐藤 花子",
                name_kana="サトウ ハナコ",
                status=CandidateStatus.HIRED,
                 gender="Female",
                birth_date=date(1995, 5, 5),
                created_by=1
            )
            session.add(candidate2)

        await session.commit()
        logger.info("Seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_data())
