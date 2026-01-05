#!/usr/bin/env python3
"""
Import extracted data from Access/Excel into the database.

Usage:
    python scripts/import_data.py
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.database import Base
from app.models.models import (
    Candidate, CandidateStatus, Employee, EmploymentType,
    HakenAssignment, UkeoiAssignment, HousingType
)


def parse_date(value):
    """Parse date from various formats."""
    if not value:
        return None
    if isinstance(value, str):
        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y/%m/%d']:
            try:
                return datetime.strptime(value.split('T')[0], fmt).date()
            except:
                continue
    return None


def parse_int(value):
    """Parse integer safely."""
    if value is None:
        return None
    try:
        return int(float(value))
    except:
        return None


def parse_bool(value):
    """Parse boolean from various formats."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', '有', 'あり')
    return bool(value)


async def import_candidates(session: AsyncSession, data_path: Path):
    """Import candidates from JSON file."""
    json_path = data_path / "candidates_raw.json"
    if not json_path.exists():
        print(f"Warning: {json_path} not found, skipping candidates import")
        return 0

    with open(json_path, 'r', encoding='utf-8') as f:
        candidates_data = json.load(f)

    count = 0
    for record in candidates_data:
        # Map Access fields to Candidate model
        candidate = Candidate(
            legacy_id=parse_int(record.get('履歴書ID')),
            full_name=record.get('氏名') or 'Unknown',
            name_kana=record.get('カナ'),
            name_romanji=record.get('氏名(ローマン)'),
            gender=record.get('性別'),
            nationality=record.get('国籍'),
            birth_date=parse_date(record.get('生年月日')),
            marital_status=record.get('配偶者'),
            postal_code=record.get('郵便番号'),
            address=record.get('住所県'),
            building_name=record.get('建物名'),
            phone=record.get('電話番号'),
            mobile=record.get('携帯電話'),
            email=record.get('メール'),
            visa_type=record.get('ビザ種類') or record.get('在留資格'),
            visa_expiry=parse_date(record.get('(在留カード記載)在留期限') or record.get('ビザ期限')),
            residence_card_number=record.get('在留カード番号'),
            passport_number=record.get('パスポート番号'),
            passport_expiry=parse_date(record.get('パスポート期限')),
            height=parse_int(record.get('身長')),
            weight=parse_int(record.get('体重')),
            shoe_size=parse_int(record.get('靴のサイズ')),
            waist=parse_int(record.get('ウエスト')),
            uniform_size=record.get('服サイズ'),
            blood_type=record.get('血液型'),
            dominant_hand=record.get('利き腕'),
            emergency_contact_name=record.get('緊急連絡先　氏名'),
            emergency_contact_relation=record.get('緊急連絡先　続柄'),
            emergency_contact_phone=record.get('緊急連絡先　電話番号'),
            japanese_level=record.get('日本語能力試験') or record.get('日本語能力試験Level'),
            education_level=record.get('最終学歴'),
            self_pr=record.get('自己PR') or record.get('志望動機'),
            notes=record.get('備考'),
            status=CandidateStatus.REGISTERED,
        )
        session.add(candidate)
        count += 1

    await session.commit()
    return count


async def import_employees(session: AsyncSession, data_path: Path):
    """Import employees and assignments from JSON files."""
    emp_count = 0
    haken_count = 0
    ukeoi_count = 0

    # Track employee IDs and assignments by employee_number
    employee_map = {}  # employee_number -> employee_id
    haken_imported = set()  # Track which employees already have haken assignment
    ukeoi_imported = set()  # Track which employees already have ukeoi assignment

    # Import haken (派遣社員) directly - they contain employee info
    haken_path = data_path / "haken_assignments.json"
    if haken_path.exists():
        with open(haken_path, 'r', encoding='utf-8') as f:
            haken_data = json.load(f)

        # Sort by status (在職中 first) and start_date (newest first) to get most recent
        haken_data.sort(key=lambda x: (
            x.get('status') != '在職中',  # Active status first
            parse_date(x.get('start_date')) or datetime.min.date()
        ), reverse=True)

        for h in haken_data:
            emp_num = parse_int(h.get('employee_number'))
            if not emp_num:
                continue

            # Check if employee already exists
            if emp_num not in employee_map:
                # Create employee from haken data
                employee = Employee(
                    employee_number=emp_num,
                    status=h.get('status', '在職中'),
                    full_name=h.get('full_name') or 'Unknown',
                    employment_type=EmploymentType.HAKEN,
                    hire_date=parse_date(h.get('start_date')),
                    termination_date=parse_date(h.get('end_date')),
                )
                session.add(employee)
                await session.flush()
                employee_map[emp_num] = employee.id
                emp_count += 1

            # Skip if already imported haken assignment for this employee
            if emp_num in haken_imported:
                continue

            employee_id = employee_map[emp_num]

            # Create haken assignment (only one per employee due to unique constraint)
            haken = HakenAssignment(
                employee_id=employee_id,
                status=h.get('status', '在職中'),
                client_company=h.get('client_company'),
                assignment_location=h.get('assignment_location'),
                assignment_line=h.get('assignment_line'),
                job_description=h.get('job_description'),
                hourly_rate=parse_int(h.get('hourly_rate')),
                hourly_rate_history=h.get('hourly_rate_history'),
                billing_rate=parse_int(h.get('billing_rate')),
                billing_rate_history=h.get('billing_rate_history'),
                profit_margin=parse_int(h.get('profit_margin')),
                standard_salary=parse_int(h.get('standard_salary')),
                health_insurance=parse_int(h.get('health_insurance')),
                nursing_insurance=parse_int(h.get('nursing_insurance')),
                pension=parse_int(h.get('pension')),
                social_insurance_enrolled=parse_bool(h.get('social_insurance_enrolled')),
                apartment_name=h.get('apartment_name'),
                move_in_date=parse_date(h.get('move_in_date')),
                start_date=parse_date(h.get('start_date')),
                end_date=parse_date(h.get('end_date')),
                license_type=h.get('license_type'),
                license_expiry=parse_date(h.get('license_expiry')),
                commute_method=h.get('commute_method'),
                japanese_certification=h.get('japanese_certification'),
            )
            session.add(haken)
            haken_imported.add(emp_num)
            haken_count += 1

    # Import ukeoi (請負社員) directly
    ukeoi_path = data_path / "ukeoi_assignments.json"
    if ukeoi_path.exists():
        with open(ukeoi_path, 'r', encoding='utf-8') as f:
            ukeoi_data = json.load(f)

        # Sort by status (在職中 first) and start_date (newest first) to get most recent
        ukeoi_data.sort(key=lambda x: (
            x.get('status') != '在職中',  # Active status first
            parse_date(x.get('start_date')) or datetime.min.date()
        ), reverse=True)

        for u in ukeoi_data:
            emp_num = parse_int(u.get('employee_number'))
            if not emp_num:
                continue

            # Check if employee already exists (might be in both haken and ukeoi)
            if emp_num not in employee_map:
                # Create employee from ukeoi data
                employee = Employee(
                    employee_number=emp_num,
                    status=u.get('status', '在職中'),
                    full_name=u.get('full_name') or 'Unknown',
                    employment_type=EmploymentType.UKEOI,
                    hire_date=parse_date(u.get('start_date')),
                    termination_date=parse_date(u.get('end_date')),
                )
                session.add(employee)
                await session.flush()
                employee_map[emp_num] = employee.id
                emp_count += 1

            # Skip if already imported ukeoi assignment for this employee
            if emp_num in ukeoi_imported:
                continue

            employee_id = employee_map[emp_num]

            # Create ukeoi assignment (only one per employee due to unique constraint)
            ukeoi = UkeoiAssignment(
                employee_id=employee_id,
                status=u.get('status', '在職中'),
                job_type=u.get('job_type'),
                hourly_rate=parse_int(u.get('hourly_rate')),
                hourly_rate_history=u.get('hourly_rate_history'),
                profit_margin=parse_int(u.get('profit_margin')),
                commute_distance=u.get('commute_distance'),
                transport_allowance=parse_int(u.get('transport_allowance')),
                apartment_name=u.get('apartment_name'),
                move_in_date=parse_date(u.get('move_in_date')),
                start_date=parse_date(u.get('start_date')),
                end_date=parse_date(u.get('end_date')),
                bank_account_name=u.get('bank_account_name'),
                bank_name=u.get('bank_name'),
                branch_number=u.get('branch_number'),
                branch_name=u.get('branch_name'),
                account_number=u.get('account_number'),
            )
            session.add(ukeoi)
            ukeoi_imported.add(emp_num)
            ukeoi_count += 1

    await session.commit()
    return emp_count, haken_count, ukeoi_count


async def main():
    """Main import function."""
    # Use a fresh database for import
    db_url = "sqlite+aiosqlite:///./uns_rirekisho_prod.db"
    print(f"Database URL: {db_url}")

    # Create engine
    engine = create_async_engine(db_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    data_path = Path(__file__).parent.parent / "exports"

    async with async_session() as session:
        print("\n=== Importing Candidates ===")
        candidate_count = await import_candidates(session, data_path)
        print(f"Imported {candidate_count} candidates")

        print("\n=== Importing Employees ===")
        emp_count, haken_count, ukeoi_count = await import_employees(session, data_path)
        print(f"Imported {emp_count} employees")
        print(f"Imported {haken_count} haken assignments")
        print(f"Imported {ukeoi_count} ukeoi assignments")

    await engine.dispose()

    print("\n=== Import Complete ===")
    print(f"Total candidates: {candidate_count}")
    print(f"Total employees: {emp_count}")
    print(f"  - Haken assignments: {haken_count}")
    print(f"  - Ukeoi assignments: {ukeoi_count}")


if __name__ == "__main__":
    asyncio.run(main())
