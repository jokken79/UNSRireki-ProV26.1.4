"""
Seed sample data for development and testing.

Usage:
    python scripts/seed_data.py

This script creates sample data including:
- Users with different roles
- Sample candidates
- Sample client companies
- Sample apartments
"""
import asyncio
import sys
import os
from datetime import date, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.models.models import (
    User, UserRole, Candidate, CandidateStatus,
    ClientCompany, CompanyApartment
)
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Sample data
SAMPLE_USERS = [
    {"username": "manager1", "email": "manager1@universal-kikaku.co.jp", "full_name": "山田 太郎", "role": UserRole.MANAGER},
    {"username": "staff1", "email": "staff1@universal-kikaku.co.jp", "full_name": "佐藤 花子", "role": UserRole.STAFF},
    {"username": "staff2", "email": "staff2@universal-kikaku.co.jp", "full_name": "鈴木 一郎", "role": UserRole.STAFF},
    {"username": "viewer1", "email": "viewer1@universal-kikaku.co.jp", "full_name": "高橋 美香", "role": UserRole.VIEWER},
]

SAMPLE_CANDIDATES = [
    {"full_name": "GARCIA MARTINEZ, Carlos", "name_kana": "ガルシア マルティネス カルロス", "nationality": "Peru", "gender": "男", "visa_type": "技術・人文知識・国際業務", "japanese_level": "N3"},
    {"full_name": "SANTOS, Maria Elena", "name_kana": "サントス マリア エレナ", "nationality": "Brazil", "gender": "女", "visa_type": "定住者", "japanese_level": "N2"},
    {"full_name": "NGUYEN, Van Minh", "name_kana": "グエン バン ミン", "nationality": "Vietnam", "gender": "男", "visa_type": "技能実習", "japanese_level": "N4"},
    {"full_name": "LOPEZ, Ana Patricia", "name_kana": "ロペス アナ パトリシア", "nationality": "Philippines", "gender": "女", "visa_type": "特定技能1号", "japanese_level": "N3"},
    {"full_name": "CHEN, Wei", "name_kana": "チェン ウェイ", "nationality": "China", "gender": "男", "visa_type": "技術・人文知識・国際業務", "japanese_level": "N1"},
    {"full_name": "RODRIGUEZ, Jose Luis", "name_kana": "ロドリゲス ホセ ルイス", "nationality": "Mexico", "gender": "男", "visa_type": "永住者", "japanese_level": "N2"},
    {"full_name": "TANAKA, Yuki", "name_kana": "タナカ ユキ", "nationality": "Japan", "gender": "女", "visa_type": None, "japanese_level": None},
    {"full_name": "KIM, Min-jun", "name_kana": "キム ミンジュン", "nationality": "Korea", "gender": "男", "visa_type": "特定活動", "japanese_level": "N2"},
]

SAMPLE_COMPANIES = [
    {"name": "株式会社トヨタ自動車", "name_kana": "カブシキガイシャトヨタジドウシャ", "address": "愛知県豊田市トヨタ町1番地", "contact_person": "製造部 田中"},
    {"name": "株式会社デンソー", "name_kana": "カブシキガイシャデンソー", "address": "愛知県刈谷市昭和町1-1", "contact_person": "人事部 山本"},
    {"name": "アイシン精機株式会社", "name_kana": "アイシンセイキカブシキガイシャ", "address": "愛知県刈谷市朝日町2-1", "contact_person": "総務部 伊藤"},
    {"name": "株式会社豊田自動織機", "name_kana": "カブシキガイシャトヨタジドウショッキ", "address": "愛知県刈谷市豊田町2-1", "contact_person": "製造課 小林"},
    {"name": "ジェイテクト株式会社", "name_kana": "ジェイテクトカブシキガイシャ", "address": "愛知県刈谷市朝日町1-1", "contact_person": "業務部 渡辺"},
]

SAMPLE_APARTMENTS = [
    {"name": "ユニバーサル寮A棟", "address": "愛知県安城市三河安城町1-1-1", "capacity": 8, "monthly_rent": 25000},
    {"name": "ユニバーサル寮B棟", "address": "愛知県安城市三河安城町1-1-2", "capacity": 6, "monthly_rent": 28000},
    {"name": "刈谷社宅", "address": "愛知県刈谷市東境町2-2-2", "capacity": 4, "monthly_rent": 30000},
    {"name": "豊田寮", "address": "愛知県豊田市若林西町3-3-3", "capacity": 10, "monthly_rent": 22000},
]


async def seed_data():
    """Seed sample data."""

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create sample users
        print("Creating sample users...")
        for user_data in SAMPLE_USERS:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=pwd_context.hash("Password123!"),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
            )
            session.add(user)

        # Create sample candidates
        print("Creating sample candidates...")
        statuses = [CandidateStatus.REGISTERED, CandidateStatus.PRESENTED, CandidateStatus.ACCEPTED]
        for i, cand_data in enumerate(SAMPLE_CANDIDATES):
            candidate = Candidate(
                full_name=cand_data["full_name"],
                name_kana=cand_data["name_kana"],
                nationality=cand_data["nationality"],
                gender=cand_data["gender"],
                birth_date=date(1985 + i, random.randint(1, 12), random.randint(1, 28)),
                visa_type=cand_data["visa_type"],
                visa_expiry=date.today() + timedelta(days=random.randint(180, 730)) if cand_data["visa_type"] else None,
                japanese_level=cand_data["japanese_level"],
                status=random.choice(statuses),
                phone=f"090-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                postal_code=f"{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                address="愛知県名古屋市中村区" + f"○○町{random.randint(1, 10)}-{random.randint(1, 30)}",
            )
            session.add(candidate)

        # Create sample companies
        print("Creating sample client companies...")
        for comp_data in SAMPLE_COMPANIES:
            company = ClientCompany(
                name=comp_data["name"],
                name_kana=comp_data["name_kana"],
                address=comp_data["address"],
                contact_person=comp_data["contact_person"],
                phone=f"0566-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
                billing_rate_default=random.randint(1800, 2500),
                is_active=True,
            )
            session.add(company)

        # Create sample apartments
        print("Creating sample apartments...")
        for apt_data in SAMPLE_APARTMENTS:
            apartment = CompanyApartment(
                name=apt_data["name"],
                address=apt_data["address"],
                capacity=apt_data["capacity"],
                current_occupants=random.randint(0, apt_data["capacity"]),
                monthly_rent=apt_data["monthly_rent"],
                is_active=True,
            )
            session.add(apartment)

        await session.commit()

        print("\n" + "=" * 50)
        print("Sample data created successfully!")
        print("=" * 50)
        print(f"Users: {len(SAMPLE_USERS)}")
        print(f"Candidates: {len(SAMPLE_CANDIDATES)}")
        print(f"Client Companies: {len(SAMPLE_COMPANIES)}")
        print(f"Apartments: {len(SAMPLE_APARTMENTS)}")
        print("=" * 50)
        print("\nAll users have password: Password123!")
        print("=" * 50 + "\n")


async def main():
    """Main entry point."""
    try:
        await seed_data()
    except Exception as e:
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
