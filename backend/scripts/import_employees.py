#!/usr/bin/env python3
"""
Import Employees from 社員台帳 Excel to SQLite Database
=======================================================

Imports employee data from:
- DBStaffX (Master Employee Data)
- DBGenzaiX (派遣社員 - Dispatch Workers)
- DBUkeoiX (請負社員 - Contract Workers)

Usage:
    python import_employees.py                                    # Auto-detect Excel file
    python import_employees.py --excel "C:/path/to/社員台帳.xlsm"  # Specify Excel file
    python import_employees.py --dry-run                          # Preview without importing
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.models import Employee, HakenAssignment, UkeoiAssignment, EmploymentType


# Excel column mappings for DBGenzaiX (派遣社員 - 42 columns)
GENZAI_COLUMN_MAP = {
    0: 'status',                # 現在 (A)
    1: 'employee_number',       # 社員№ (B)
    2: 'client_company_id',     # 派遣先ID (C)
    3: 'client_company',        # 派遣先 (D)
    4: 'assignment_location',   # 配属先 (E)
    5: 'assignment_line',       # 配属ライン (F)
    6: 'job_description',       # 仕事内容 (G)
    7: 'full_name',             # 氏名 (H)
    8: 'name_kana',             # カナ (I)
    9: 'gender',                # 性別 (J)
    10: 'nationality',          # 国籍 (K)
    11: 'birth_date',           # 生年月日 (L)
    12: 'age',                  # 年齢 (M)
    13: 'hourly_rate',          # 時給 (N)
    14: 'hourly_rate_history',  # 時給改定 (O)
    15: 'billing_rate',         # 請求単価 (P)
    16: 'billing_rate_history', # 請求改定 (Q)
    17: 'profit_margin',        # 差額利益 (R)
    18: 'standard_salary',      # 標準報酬 (S)
    19: 'health_insurance',     # 健康保険 (T)
    20: 'nursing_insurance',    # 介護保険 (U)
    21: 'pension',              # 厚生年金 (V)
    22: 'visa_expiry',          # ビザ期限 (W)
    23: 'visa_type',            # ビザ種類 (X)
    24: 'visa_alert',           # ｱﾗｰﾄ(ﾋﾞｻﾞ更新) (Y)
    25: 'postal_code',          # 〒 (Z)
    26: 'address',              # 住所 (AA)
    27: 'apartment_name',       # ｱﾊﾟｰﾄ (AB)
    28: 'move_in_date',         # 入居 (AC)
    29: 'start_date',           # 入社日 (AD)
    30: 'end_date',             # 退社日 (AE)
    31: 'current_hire_date',    # 現入社 (AF)
    32: 'social_insurance_enrolled', # 社保加入 (AG)
    33: 'move_out_date',        # 退去 (AH)
    34: 'entry_request',        # 入社依頼 (AI)
    35: 'career_up_5th_year',   # キャリアアップ5年目 (AJ)
    36: 'license_type',         # 免許種類 (AK)
    37: 'license_expiry',       # 免許期限 (AL)
    38: 'commute_method',       # 通勤方法 (AM)
    39: 'optional_insurance_expiry',  # 任意保険期限 (AN)
    40: 'japanese_certification',  # 日本語検定 (AO)
    41: 'notes',                # 備考 (AP)
}

# Excel column mappings for DBUkeoiX (請負社員 - 36 columns)
UKEOI_COLUMN_MAP = {
    0: 'status',               # 現在 (A)
    1: 'employee_number',      # 社員№ (B)
    2: 'job_type',             # 請負業務 (C)
    3: 'full_name',            # 氏名 (D)
    4: 'name_kana',            # カナ (E)
    5: 'gender',               # 性別 (F)
    6: 'nationality',          # 国籍 (G)
    7: 'birth_date',           # 生年月日 (H)
    8: 'age',                  # 年齢 (I)
    9: 'hourly_rate',          # 時給 (J)
    10: 'hourly_rate_history', # 時給改定 (K)
    11: 'standard_salary',     # 標準報酬 (L)
    12: 'health_insurance',    # 健康保険 (M)
    13: 'nursing_insurance',   # 介護保険 (N)
    14: 'pension',             # 厚生年金 (O)
    15: 'commute_distance',    # 通勤距離 (P)
    16: 'transport_allowance', # 交通費 (Q)
    17: 'profit_margin',       # 差額利益 (R)
    18: 'visa_expiry',         # ビザ期限 (S)
    19: 'visa_type',           # ビザ種類 (T)
    20: 'visa_alert',          # ｱﾗｰﾄ(ﾋﾞｻﾞ更新) (U)
    21: 'postal_code',         # 〒 (V)
    22: 'address',             # 住所 (W)
    23: 'apartment_name',      # ｱﾊﾟｰﾄ (X)
    24: 'move_in_date',        # 入居 (Y)
    25: 'start_date',          # 入社日 (Z)
    26: 'end_date',            # 退社日 (AA)
    27: 'social_insurance_enrolled',  # 社保加入 (AB)
    28: 'move_out_date',       # 退去 (AC)
    29: 'bank_account_name',   # 口座名義 (AD)
    30: 'bank_name',           # 銀行名 (AE)
    31: 'branch_number',       # 支店番号 (AF)
    32: 'branch_name',         # 支店名 (AG)
    33: 'account_number',      # 口座番号 (AH)
    34: 'entry_request',       # 入社依頼 (AI)
    35: 'notes',               # 備考 (AJ)
}

# Date fields for parsing
DATE_FIELDS = {
    'birth_date', 'visa_expiry', 'move_in_date', 'start_date', 'end_date',
    'move_out_date', 'license_expiry', 'optional_insurance_expiry',
    'current_hire_date', 'career_up_5th_year'
}

# Integer fields
INT_FIELDS = {
    'hourly_rate', 'billing_rate', 'profit_margin', 'standard_salary',
    'health_insurance', 'nursing_insurance', 'pension', 'transport_allowance'
}


def find_excel_file() -> Optional[Path]:
    """Find the 社員台帳 Excel file in common locations."""
    search_locations = [
        Path.home() / "OneDrive" / "DATABASEJP" / "社員台帳.xlsm",
        Path.home() / "OneDrive" / "Documents" / "社員台帳.xlsm",
        Path.home() / "Documents" / "社員台帳.xlsm",
        Path.home() / "Desktop" / "社員台帳.xlsm",
        Path("C:/Users/Jpkken/OneDrive/DATABASEJP/社員台帳.xlsm"),
        Path("D:/DATABASEJP/社員台帳.xlsm"),
    ]

    for path in search_locations:
        if path.exists():
            return path

    # Search current directory and parents
    current = Path.cwd()
    for _ in range(5):
        for pattern in ["社員台帳.xlsm", "*.xlsm"]:
            matches = list(current.glob(pattern))
            if matches:
                return matches[0]
        current = current.parent

    return None


def parse_date(value) -> Optional[date]:
    """Parse various date formats to date object."""
    if value is None or pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    # Excel serial date number
    if isinstance(value, (int, float)) and value > 25000:
        try:
            from datetime import timedelta
            base_date = datetime(1899, 12, 30)
            return (base_date + timedelta(days=int(value))).date()
        except:
            pass

    # String parsing
    if isinstance(value, str):
        for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%Y年%m月%d日', '%m/%d/%Y']:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue

    return None


def parse_int(value) -> Optional[int]:
    """Parse integer value."""
    if value is None or pd.isna(value):
        return None
    try:
        return int(float(value))
    except:
        return None


def parse_float(value) -> Optional[float]:
    """Parse float value."""
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except:
        return None


def clean_string(value) -> Optional[str]:
    """Clean and normalize string value."""
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    return s if s and s != '0' else None


def normalize_status(status: str) -> str:
    """Normalize status values."""
    if not status:
        return "在職中"
    status_map = {
        '在職中': '在職中',
        '0': '在職中',
        '待機中': '待機中',
        '退社': '退社',
        '1': '退社',
    }
    return status_map.get(str(status).strip(), '在職中')


def read_genzai_sheet(excel_path: Path) -> List[Dict[str, Any]]:
    """Read DBGenzaiX (派遣社員) sheet."""
    print(f"Reading DBGenzaiX sheet...")

    try:
        df = pd.read_excel(excel_path, sheet_name='DBGenzaiX', header=0)
    except Exception as e:
        print(f"  Error reading DBGenzaiX: {e}")
        return []

    records = []
    for idx, row in df.iterrows():
        # Skip empty rows
        emp_num = row.iloc[1] if len(row) > 1 else None
        if pd.isna(emp_num):
            continue

        record = {'employment_type': 'haken'}

        for col_idx, field_name in GENZAI_COLUMN_MAP.items():
            if col_idx >= len(row):
                continue

            value = row.iloc[col_idx]

            if field_name in DATE_FIELDS:
                record[field_name] = parse_date(value)
            elif field_name in INT_FIELDS:
                record[field_name] = parse_int(value)
            elif field_name == 'employee_number':
                record[field_name] = parse_int(value)
            elif field_name == 'social_insurance_enrolled':
                record[field_name] = str(value).strip() == '有' if value else False
            else:
                record[field_name] = clean_string(value)

        record['status'] = normalize_status(record.get('status'))
        records.append(record)

    print(f"  Found {len(records)} records")
    return records


def read_ukeoi_sheet(excel_path: Path) -> List[Dict[str, Any]]:
    """Read DBUkeoiX (請負社員) sheet."""
    print(f"Reading DBUkeoiX sheet...")

    try:
        df = pd.read_excel(excel_path, sheet_name='DBUkeoiX', header=0)
    except Exception as e:
        print(f"  Error reading DBUkeoiX: {e}")
        return []

    records = []
    for idx, row in df.iterrows():
        # Skip empty rows
        emp_num = row.iloc[1] if len(row) > 1 else None
        if pd.isna(emp_num):
            continue

        record = {'employment_type': 'ukeoi'}

        for col_idx, field_name in UKEOI_COLUMN_MAP.items():
            if col_idx >= len(row):
                continue

            value = row.iloc[col_idx]

            if field_name in DATE_FIELDS:
                record[field_name] = parse_date(value)
            elif field_name in INT_FIELDS:
                record[field_name] = parse_int(value)
            elif field_name == 'employee_number':
                record[field_name] = parse_int(value)
            elif field_name == 'commute_distance':
                record[field_name] = parse_float(value)
            elif field_name == 'social_insurance_enrolled':
                record[field_name] = str(value).strip() == '有' if value else False
            else:
                record[field_name] = clean_string(value)

        record['status'] = normalize_status(record.get('status'))
        records.append(record)

    print(f"  Found {len(records)} records")
    return records


def import_to_database(records: List[Dict[str, Any]], session, dry_run: bool = False) -> Dict[str, int]:
    """Import records to database."""
    stats = {'inserted': 0, 'updated': 0, 'errors': 0}

    for record in records:
        emp_num = record.get('employee_number')
        if not emp_num:
            stats['errors'] += 1
            continue

        try:
            # Check if employee exists
            existing = session.query(Employee).filter(
                Employee.employee_number == emp_num
            ).first()

            employment_type = (
                EmploymentType.HAKEN if record['employment_type'] == 'haken'
                else EmploymentType.UKEOI
            )

            if existing:
                # Update existing employee
                if not dry_run:
                    existing.full_name = record.get('full_name') or existing.full_name
                    existing.name_kana = record.get('name_kana') or existing.name_kana
                    existing.gender = record.get('gender') or existing.gender
                    existing.nationality = record.get('nationality') or existing.nationality
                    existing.birth_date = record.get('birth_date') or existing.birth_date
                    existing.visa_expiry = record.get('visa_expiry') or existing.visa_expiry
                    existing.visa_type = record.get('visa_type') or existing.visa_type
                    existing.postal_code = record.get('postal_code') or existing.postal_code
                    existing.address = record.get('address') or existing.address
                    existing.status = record.get('status') or existing.status
                    existing.hire_date = record.get('start_date') or existing.hire_date
                    existing.termination_date = record.get('end_date') or existing.termination_date
                    existing.employment_type = employment_type

                    # Update assignment
                    if employment_type == EmploymentType.HAKEN:
                        update_haken_assignment(existing, record, session)
                    else:
                        update_ukeoi_assignment(existing, record, session)

                stats['updated'] += 1
            else:
                # Create new employee
                if not dry_run:
                    employee = Employee(
                        employee_number=emp_num,
                        full_name=record.get('full_name', ''),
                        name_kana=record.get('name_kana'),
                        gender=record.get('gender'),
                        nationality=record.get('nationality'),
                        birth_date=record.get('birth_date'),
                        visa_expiry=record.get('visa_expiry'),
                        visa_type=record.get('visa_type'),
                        postal_code=record.get('postal_code'),
                        address=record.get('address'),
                        status=record.get('status', '在職中'),
                        hire_date=record.get('start_date'),
                        termination_date=record.get('end_date'),
                        employment_type=employment_type,
                    )
                    session.add(employee)
                    session.flush()  # Get the ID

                    # Create assignment
                    if employment_type == EmploymentType.HAKEN:
                        create_haken_assignment(employee, record, session)
                    else:
                        create_ukeoi_assignment(employee, record, session)

                stats['inserted'] += 1

        except Exception as e:
            print(f"  Error importing {emp_num}: {e}")
            stats['errors'] += 1

    if not dry_run:
        session.commit()

    return stats


def create_haken_assignment(employee: Employee, record: Dict, session):
    """Create HakenAssignment for employee."""
    assignment = HakenAssignment(
        employee_id=employee.id,
        status=record.get('status', '在職中'),
        client_company=record.get('client_company'),
        assignment_location=record.get('assignment_location'),
        assignment_line=record.get('assignment_line'),
        job_description=record.get('job_description'),
        hourly_rate=record.get('hourly_rate'),
        hourly_rate_history=record.get('hourly_rate_history'),
        billing_rate=record.get('billing_rate'),
        billing_rate_history=record.get('billing_rate_history'),
        profit_margin=record.get('profit_margin'),
        standard_salary=record.get('standard_salary'),
        health_insurance=record.get('health_insurance'),
        nursing_insurance=record.get('nursing_insurance'),
        pension=record.get('pension'),
        social_insurance_enrolled=record.get('social_insurance_enrolled'),
        apartment_name=record.get('apartment_name'),
        move_in_date=record.get('move_in_date'),
        move_out_date=record.get('move_out_date'),
        start_date=record.get('start_date'),
        end_date=record.get('end_date'),
        current_hire_date=record.get('current_hire_date'),
        visa_alert=record.get('visa_alert'),
        license_type=record.get('license_type'),
        license_expiry=record.get('license_expiry'),
        commute_method=record.get('commute_method'),
        optional_insurance_expiry=record.get('optional_insurance_expiry'),
        japanese_certification=record.get('japanese_certification'),
        career_up_5th_year=record.get('career_up_5th_year'),
        entry_request=record.get('entry_request'),
        notes=record.get('notes'),
    )
    session.add(assignment)


def update_haken_assignment(employee: Employee, record: Dict, session):
    """Update or create HakenAssignment for employee."""
    assignment = employee.haken_assignment
    if not assignment:
        create_haken_assignment(employee, record, session)
        return

    # Update fields
    for field in ['client_company', 'assignment_location', 'assignment_line',
                  'job_description', 'hourly_rate', 'billing_rate', 'profit_margin',
                  'status', 'apartment_name', 'notes']:
        if record.get(field) is not None:
            setattr(assignment, field, record[field])


def create_ukeoi_assignment(employee: Employee, record: Dict, session):
    """Create UkeoiAssignment for employee."""
    assignment = UkeoiAssignment(
        employee_id=employee.id,
        status=record.get('status', '在職中'),
        job_type=record.get('job_type'),
        hourly_rate=record.get('hourly_rate'),
        hourly_rate_history=record.get('hourly_rate_history'),
        profit_margin=record.get('profit_margin'),
        standard_salary=record.get('standard_salary'),
        health_insurance=record.get('health_insurance'),
        nursing_insurance=record.get('nursing_insurance'),
        pension=record.get('pension'),
        social_insurance_enrolled=record.get('social_insurance_enrolled'),
        commute_distance=record.get('commute_distance'),
        transport_allowance=record.get('transport_allowance'),
        apartment_name=record.get('apartment_name'),
        move_in_date=record.get('move_in_date'),
        move_out_date=record.get('move_out_date'),
        start_date=record.get('start_date'),
        end_date=record.get('end_date'),
        visa_alert=record.get('visa_alert'),
        bank_account_name=record.get('bank_account_name'),
        bank_name=record.get('bank_name'),
        branch_number=record.get('branch_number'),
        branch_name=record.get('branch_name'),
        account_number=record.get('account_number'),
        entry_request=record.get('entry_request'),
        notes=record.get('notes'),
    )
    session.add(assignment)


def update_ukeoi_assignment(employee: Employee, record: Dict, session):
    """Update or create UkeoiAssignment for employee."""
    assignment = employee.ukeoi_assignment
    if not assignment:
        create_ukeoi_assignment(employee, record, session)
        return

    # Update fields
    for field in ['job_type', 'hourly_rate', 'profit_margin', 'status',
                  'apartment_name', 'bank_name', 'notes']:
        if record.get(field) is not None:
            setattr(assignment, field, record[field])


def main():
    parser = argparse.ArgumentParser(
        description="Import employees from 社員台帳 Excel to database"
    )
    parser.add_argument(
        "--excel",
        type=str,
        help="Path to 社員台帳.xlsm file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without importing"
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Only import active employees (在職中)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("EMPLOYEE IMPORT FROM 社員台帳")
    print("=" * 60)

    # Find Excel file
    if args.excel:
        excel_path = Path(args.excel)
    else:
        excel_path = find_excel_file()

    if not excel_path or not excel_path.exists():
        print(f"\nError: Excel file not found")
        print("Please specify the path with --excel option")
        print("Example: python import_employees.py --excel 'C:/path/to/社員台帳.xlsm'")
        return 1

    print(f"\nExcel file: {excel_path}")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'LIVE IMPORT'}")

    # Read data from Excel
    print("\n[1/3] Reading Excel data...")
    genzai_records = read_genzai_sheet(excel_path)
    ukeoi_records = read_ukeoi_sheet(excel_path)

    all_records = genzai_records + ukeoi_records

    if args.active_only:
        all_records = [r for r in all_records if r.get('status') == '在職中']
        print(f"\nFiltered to {len(all_records)} active employees")

    if not all_records:
        print("\nNo records to import!")
        return 1

    # Print sample data
    print(f"\nTotal records to import: {len(all_records)}")
    print(f"  - 派遣社員 (Haken): {len(genzai_records)}")
    print(f"  - 請負社員 (Ukeoi): {len(ukeoi_records)}")

    if all_records:
        print("\nSample record:")
        sample = all_records[0]
        for key in ['employee_number', 'full_name', 'nationality', 'status', 'employment_type']:
            print(f"  {key}: {sample.get(key)}")

    # Setup database connection
    print("\n[2/3] Connecting to database...")
    db_path = Path(__file__).parent.parent / "uns_rirekisho.db"

    if not db_path.exists():
        print(f"  Database not found at {db_path}")
        print("  Please run the backend server first to create the database")
        return 1

    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Import data
    print(f"\n[3/3] {'[DRY RUN] Would import' if args.dry_run else 'Importing'} to database...")
    stats = import_to_database(all_records, session, args.dry_run)

    # Summary
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE!")
    print("=" * 60)
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total processed: {len(all_records)}")

    if args.dry_run:
        print("\n[DRY RUN] No changes were made to the database")

    session.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
