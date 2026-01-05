"""
Import all data from Microsoft Access database to SQLite.

Source: ユニバーサル企画㈱データベースv25.3.24_be.accdb
Target: uns_rirekisho.db (SQLite)

Tables to import:
- T_履歴書 (1,156) → candidates + photos
- DBStaffX (22) → employees (direct staff)
- DBGenzaiX (1,044) → employees + haken_assignments
- DBUkeoiX (99) → employees + ukeoi_assignments
"""

import os
import sys
import sqlite3
from datetime import datetime, date
from decimal import Decimal
import re

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyodbc
except ImportError:
    print("ERROR: pyodbc not installed. Run: pip install pyodbc")
    sys.exit(1)

# Configuration
ACCDB_PATH = r"C:\Users\Jpkken\Downloads\ユニバーサル企画㈱データベースv25.3.24_be.accdb"
SQLITE_PATH = r"C:\Users\Jpkken\UNSRireki-Prov26.1.4\backend\uns_rirekisho.db"
PHOTOS_DIR = r"C:\Users\Jpkken\UNSRireki-Prov26.1.4\backend\uploads\photos"

# Ensure photos directory exists
os.makedirs(PHOTOS_DIR, exist_ok=True)


def connect_access():
    """Connect to Access database."""
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={ACCDB_PATH};"
    )
    return pyodbc.connect(conn_str)


def connect_sqlite():
    """Connect to SQLite database."""
    return sqlite3.connect(SQLITE_PATH)


def clear_sqlite_data(sqlite_conn):
    """Clear all existing data from SQLite (except users)."""
    print("\n" + "="*60)
    print("CLEARING EXISTING DATA")
    print("="*60)

    cursor = sqlite_conn.cursor()

    # Order matters due to foreign keys
    tables_to_clear = [
        "ukeoi_assignments",
        "haken_assignments",
        "employees",
        "joining_notices",
        "applications",
        "candidate_documents",
        "candidates",
        "client_companies",
        "company_apartments",
        "audit_logs",
        "refresh_tokens",
    ]

    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table}")
            deleted = cursor.rowcount
            print(f"  Cleared {table}: {deleted} rows")
        except Exception as e:
            print(f"  Warning: Could not clear {table}: {e}")

    # Reset auto-increment counters
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name != 'users'")
    except:
        pass

    sqlite_conn.commit()
    print("Data cleared successfully.")


def safe_str(val, max_len=None):
    """Safely convert value to string."""
    if val is None:
        return None
    s = str(val).strip()
    if max_len and len(s) > max_len:
        s = s[:max_len]
    return s if s else None


def safe_date(val):
    """Safely convert to date string (YYYY-MM-DD)."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, date):
        return val.strftime('%Y-%m-%d')
    return None


def safe_int(val):
    """Safely convert to integer."""
    if val is None:
        return None
    try:
        return int(val)
    except:
        return None


def safe_float(val):
    """Safely convert to float."""
    if val is None:
        return None
    try:
        return float(val)
    except:
        return None


def import_candidates(access_conn, sqlite_conn):
    """Import candidates from T_履歴書 with photos."""
    print("\n" + "="*60)
    print("IMPORTING CANDIDATES (T_履歴書)")
    print("="*60)

    access_cursor = access_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()

    # Get column names from T_履歴書
    access_cursor.execute("SELECT TOP 1 * FROM T_履歴書")
    columns = [desc[0] for desc in access_cursor.description]
    print(f"Available columns: {len(columns)}")

    # Build column index map
    col_idx = {col: i for i, col in enumerate(columns)}
    print(f"Column index built with {len(col_idx)} columns")

    # Query all candidates using SELECT *
    access_cursor.execute("SELECT * FROM T_履歴書 ORDER BY 履歴書ID")
    rows = access_cursor.fetchall()
    print(f"Found {len(rows)} candidates to import")

    imported = 0
    photos_imported = 0

    # Helper to get value by column name
    def get_col(row, col_name, default=None):
        if col_name in col_idx:
            return row[col_idx[col_name]]
        return default

    for row in rows:
        try:
            # Create dict from row using column names
            row_dict = dict(zip(columns, row))

            legacy_id = row_dict.get('履歴書ID')
            if not legacy_id:
                continue

            # Map fields to SQLite columns
            data = {
                'legacy_id': legacy_id,
                'full_name': safe_str(row_dict.get('氏名'), 100) or f"Unknown_{legacy_id}",
                'name_kana': safe_str(row_dict.get('フリガナ'), 100),
                'name_romanji': safe_str(row_dict.get('氏名（ローマ字）'), 100),
                'gender': safe_str(row_dict.get('性別'), 10),
                'nationality': safe_str(row_dict.get('国籍'), 50),
                'birth_date': safe_date(row_dict.get('生年月日')),
                'marital_status': safe_str(row_dict.get('配偶者'), 20),
                'postal_code': safe_str(row_dict.get('郵便番号'), 10),
                'address': safe_str(row_dict.get('現住所')),
                'building_name': safe_str(row_dict.get('建物名'), 100),
                'phone': safe_str(row_dict.get('電話番号'), 20),
                'mobile': safe_str(row_dict.get('携帯電話'), 20),
                'email': safe_str(row_dict.get('電子メール'), 100),
                'visa_type': safe_str(row_dict.get('在留資格'), 100),
                'visa_expiry': safe_date(row_dict.get('（在留カード記載）在留期限')),
                'residence_card_number': safe_str(row_dict.get('在留カード番号'), 50),
                'passport_number': safe_str(row_dict.get('パスポート番号'), 50),
                'passport_expiry': safe_date(row_dict.get('パスポート期限')),
                'height': safe_float(row_dict.get('身長')),
                'weight': safe_float(row_dict.get('体重')),
                'shoe_size': safe_float(row_dict.get('靴のサイズ')),
                'waist': safe_int(row_dict.get('ウエスト')),
                'uniform_size': safe_str(row_dict.get('服サイズ'), 10),
                'blood_type': safe_str(row_dict.get('血液型'), 5),
                'vision_right': safe_float(row_dict.get('視力　右')),
                'vision_left': safe_float(row_dict.get('視力　左')),
                'wears_glasses': bool(row_dict.get('眼鏡使用')) if row_dict.get('眼鏡使用') else None,
                'dominant_hand': safe_str(row_dict.get('利き腕'), 10),
                'emergency_contact_name': safe_str(row_dict.get('緊急連絡先　氏名'), 100),
                'emergency_contact_relation': safe_str(row_dict.get('緊急連絡先　続柄'), 50),
                'emergency_contact_phone': safe_str(row_dict.get('緊急連絡先　電話番号'), 20),
                'japanese_level': safe_str(row_dict.get('日本語能力試験Level'), 20),
                'listening_level': safe_str(row_dict.get('聞く'), 20),
                'speaking_level': safe_str(row_dict.get('話す'), 20),
                'reading_level': safe_str(row_dict.get('読む　カナ'), 20),
                'writing_level': safe_str(row_dict.get('書く　カナ'), 20),
                'education_level': safe_str(row_dict.get('最終学歴'), 50),
                'major': safe_str(row_dict.get('専攻'), 100),
                'reason_for_applying': safe_str(row_dict.get('志望動機')),
                'self_pr': safe_str(row_dict.get('趣味・特技')),
                'notes': safe_str(row_dict.get('備考')),
                'status': 'registered',
                'created_at': datetime.now().isoformat(),
            }

            # Insert candidate
            columns_str = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            sqlite_cursor.execute(
                f"INSERT INTO candidates ({columns_str}) VALUES ({placeholders})",
                list(data.values())
            )
            candidate_id = sqlite_cursor.lastrowid
            imported += 1

            if imported % 100 == 0:
                print(f"  Imported {imported} candidates...")
                sqlite_conn.commit()

        except Exception as e:
            print(f"  Error importing candidate {legacy_id}: {e}")
            continue

    sqlite_conn.commit()
    print(f"Imported {imported} candidates")

    # Now import photos separately using attachment subfield syntax
    print("\nImporting photos from attachment field...")

    photo_query = "SELECT 履歴書ID, 写真.FileData, 写真.FileName FROM T_履歴書 WHERE 写真.FileName IS NOT NULL"

    try:
        access_cursor.execute(photo_query)
        photo_rows = access_cursor.fetchall()
        print(f"Found {len(photo_rows)} photos to import")

        for photo_row in photo_rows:
            try:
                legacy_id = photo_row[0]
                file_data = photo_row[1]
                file_name = photo_row[2]

                if file_data and len(file_data) > 0:
                    # Determine extension
                    ext = '.jpg'
                    if file_name:
                        _, ext = os.path.splitext(file_name)
                        ext = ext.lower() or '.jpg'

                    # Save photo
                    photo_filename = f"{legacy_id}{ext}"
                    photo_path = os.path.join(PHOTOS_DIR, photo_filename)

                    with open(photo_path, 'wb') as f:
                        f.write(file_data)

                    # Update candidate with photo_url
                    photo_url = f"/uploads/photos/{photo_filename}"
                    sqlite_cursor.execute(
                        "UPDATE candidates SET photo_url = ? WHERE legacy_id = ?",
                        (photo_url, legacy_id)
                    )
                    photos_imported += 1

                    if photos_imported % 100 == 0:
                        print(f"  Imported {photos_imported} photos...")
                        sqlite_conn.commit()

            except Exception as e:
                print(f"  Error importing photo for {legacy_id}: {e}")
                continue

    except Exception as e:
        print(f"  Error querying photos: {e}")
        print("  Trying alternative photo query...")

        # Alternative: query one by one
        sqlite_cursor.execute("SELECT legacy_id FROM candidates")
        all_legacy_ids = [r[0] for r in sqlite_cursor.fetchall()]

        for legacy_id in all_legacy_ids:
            try:
                access_cursor.execute(
                    "SELECT 写真.FileData, 写真.FileName FROM T_履歴書 WHERE 履歴書ID = ?",
                    (legacy_id,)
                )
                photo_row = access_cursor.fetchone()

                if photo_row and photo_row[0]:
                    file_data = photo_row[0]
                    file_name = photo_row[1]

                    ext = '.jpg'
                    if file_name:
                        _, ext = os.path.splitext(file_name)
                        ext = ext.lower() or '.jpg'

                    photo_filename = f"{legacy_id}{ext}"
                    photo_path = os.path.join(PHOTOS_DIR, photo_filename)

                    with open(photo_path, 'wb') as f:
                        f.write(file_data)

                    photo_url = f"/uploads/photos/{photo_filename}"
                    sqlite_cursor.execute(
                        "UPDATE candidates SET photo_url = ? WHERE legacy_id = ?",
                        (photo_url, legacy_id)
                    )
                    photos_imported += 1

                    if photos_imported % 100 == 0:
                        print(f"  Imported {photos_imported} photos...")
                        sqlite_conn.commit()

            except Exception as e:
                # Skip silently for individual errors
                continue

    sqlite_conn.commit()
    print(f"Imported {photos_imported} photos")

    return imported, photos_imported


def import_employees_from_dbstaffx(access_conn, sqlite_conn, employee_number_start=1):
    """Import direct staff from DBStaffX."""
    print("\n" + "="*60)
    print("IMPORTING DIRECT STAFF (DBStaffX)")
    print("="*60)

    access_cursor = access_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()

    try:
        access_cursor.execute("SELECT * FROM DBStaffX")
        columns = [desc[0] for desc in access_cursor.description]
        print(f"DBStaffX columns: {columns}")
    except Exception as e:
        print(f"Error: Could not access DBStaffX: {e}")
        return 0, employee_number_start

    rows = access_cursor.fetchall()
    print(f"Found {len(rows)} direct staff records")

    imported = 0
    emp_num = employee_number_start

    for row in rows:
        try:
            # Map DBStaffX columns (adjust indices based on actual column order)
            row_dict = dict(zip(columns, row))

            employee_data = {
                'employee_number': emp_num,
                'status': safe_str(row_dict.get('現在', '在職中'), 20) or '在職中',
                'office': safe_str(row_dict.get('事務所'), 50),
                'full_name': safe_str(row_dict.get('氏名'), 100) or f"Staff_{emp_num}",
                'name_kana': safe_str(row_dict.get('カナ'), 100),
                'gender': safe_str(row_dict.get('性別'), 10),
                'nationality': safe_str(row_dict.get('国籍'), 50),
                'birth_date': safe_date(row_dict.get('生年月日')),
                'visa_expiry': safe_date(row_dict.get('ビザ期限')),
                'visa_type': safe_str(row_dict.get('ビザ種類'), 100),
                'has_spouse': bool(row_dict.get('配偶者')) if row_dict.get('配偶者') else None,
                'postal_code': safe_str(row_dict.get('〒'), 10),
                'address': safe_str(row_dict.get('住所')),
                'building_name': safe_str(row_dict.get('建物名'), 100),
                'hire_date': safe_date(row_dict.get('入社日')),
                'termination_date': safe_date(row_dict.get('退社日')),
                'employment_type': 'haken',  # Default for direct staff
                'created_at': datetime.now().isoformat(),
            }

            columns_str = ', '.join(employee_data.keys())
            placeholders = ', '.join(['?' for _ in employee_data])
            sqlite_cursor.execute(
                f"INSERT INTO employees ({columns_str}) VALUES ({placeholders})",
                list(employee_data.values())
            )

            imported += 1
            emp_num += 1

        except Exception as e:
            print(f"  Error importing staff: {e}")
            continue

    sqlite_conn.commit()
    print(f"Imported {imported} direct staff")
    return imported, emp_num


def import_employees_from_dbgenzaix(access_conn, sqlite_conn, employee_number_start=1):
    """Import 派遣社員 from DBGenzaiX."""
    print("\n" + "="*60)
    print("IMPORTING 派遣社員 (DBGenzaiX)")
    print("="*60)

    access_cursor = access_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()

    try:
        access_cursor.execute("SELECT * FROM DBGenzaiX")
        columns = [desc[0] for desc in access_cursor.description]
        print(f"DBGenzaiX columns ({len(columns)}): {columns[:10]}...")
    except Exception as e:
        print(f"Error: Could not access DBGenzaiX: {e}")
        return 0, employee_number_start

    rows = access_cursor.fetchall()
    print(f"Found {len(rows)} 派遣社員 records")

    imported = 0
    emp_num = employee_number_start

    for row in rows:
        try:
            row_dict = dict(zip(columns, row))

            # Create employee record
            employee_data = {
                'employee_number': emp_num,
                'status': safe_str(row_dict.get('現在', '在職中'), 20) or '在職中',
                'office': safe_str(row_dict.get('事務所'), 50),
                'full_name': safe_str(row_dict.get('氏名'), 100) or f"Haken_{emp_num}",
                'name_kana': safe_str(row_dict.get('カナ'), 100),
                'gender': safe_str(row_dict.get('性別'), 10),
                'nationality': safe_str(row_dict.get('国籍'), 50),
                'birth_date': safe_date(row_dict.get('生年月日')),
                'visa_expiry': safe_date(row_dict.get('ビザ期限')),
                'visa_type': safe_str(row_dict.get('ビザ種類'), 100),
                'has_spouse': bool(row_dict.get('配偶者')) if row_dict.get('配偶者') else None,
                'postal_code': safe_str(row_dict.get('〒'), 10),
                'address': safe_str(row_dict.get('住所')),
                'building_name': safe_str(row_dict.get('建物名'), 100),
                'hire_date': safe_date(row_dict.get('入社日')),
                'termination_date': safe_date(row_dict.get('退社日')),
                'employment_type': 'haken',
                'created_at': datetime.now().isoformat(),
            }

            columns_str = ', '.join(employee_data.keys())
            placeholders = ', '.join(['?' for _ in employee_data])
            sqlite_cursor.execute(
                f"INSERT INTO employees ({columns_str}) VALUES ({placeholders})",
                list(employee_data.values())
            )
            employee_id = sqlite_cursor.lastrowid

            # Create haken_assignment record
            assignment_data = {
                'employee_id': employee_id,
                'status': safe_str(row_dict.get('現在', '在職中'), 20) or '在職中',
                'client_company': safe_str(row_dict.get('派遣先'), 200),
                'assignment_location': safe_str(row_dict.get('配属先'), 200),
                'assignment_line': safe_str(row_dict.get('配属ライン'), 100),
                'job_description': safe_str(row_dict.get('仕事内容')),
                'hourly_rate': safe_int(row_dict.get('時給')),
                'hourly_rate_history': safe_str(row_dict.get('時給改定')),
                'billing_rate': safe_int(row_dict.get('請求単価')),
                'billing_rate_history': safe_str(row_dict.get('請求改定')),
                'profit_margin': safe_int(row_dict.get('差額利益')),
                'standard_salary': safe_int(row_dict.get('標準報酬')),
                'health_insurance': safe_int(row_dict.get('健康保険')),
                'nursing_insurance': safe_int(row_dict.get('介護保険')),
                'pension': safe_int(row_dict.get('厚生年金')),
                'social_insurance_enrolled': bool(row_dict.get('社保加入')) if row_dict.get('社保加入') else None,
                'apartment_name': safe_str(row_dict.get('ｱﾊﾟｰﾄ'), 100),
                'move_in_date': safe_date(row_dict.get('入居')),
                'move_out_date': safe_date(row_dict.get('退去')),
                'start_date': safe_date(row_dict.get('入社日')),
                'end_date': safe_date(row_dict.get('退社日')),
                'current_hire_date': safe_date(row_dict.get('現入社')),
                'visa_alert': safe_str(row_dict.get('ｱﾗｰﾄ(ﾋﾞｻﾞ更新)'), 50),
                'license_type': safe_str(row_dict.get('免許種類'), 100),
                'license_expiry': safe_date(row_dict.get('免許期限')),
                'commute_method': safe_str(row_dict.get('通勤方法'), 50),
                'optional_insurance_expiry': safe_date(row_dict.get('任意保険期限')),
                'japanese_certification': safe_str(row_dict.get('日本語検定'), 50),
                'career_up_5th_year': safe_date(row_dict.get('キャリアアップ5年目')),
                'entry_request': safe_str(row_dict.get('入社依頼'), 50),
                'notes': safe_str(row_dict.get('備考')),
                'created_at': datetime.now().isoformat(),
            }

            columns_str = ', '.join(assignment_data.keys())
            placeholders = ', '.join(['?' for _ in assignment_data])
            sqlite_cursor.execute(
                f"INSERT INTO haken_assignments ({columns_str}) VALUES ({placeholders})",
                list(assignment_data.values())
            )

            imported += 1
            emp_num += 1

            if imported % 100 == 0:
                print(f"  Imported {imported} 派遣社員...")
                sqlite_conn.commit()

        except Exception as e:
            print(f"  Error importing 派遣社員: {e}")
            continue

    sqlite_conn.commit()
    print(f"Imported {imported} 派遣社員")
    return imported, emp_num


def import_employees_from_dbukeoi(access_conn, sqlite_conn, employee_number_start=1):
    """Import 請負社員 from DBUkeoiX."""
    print("\n" + "="*60)
    print("IMPORTING 請負社員 (DBUkeoiX)")
    print("="*60)

    access_cursor = access_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()

    try:
        access_cursor.execute("SELECT * FROM DBUkeoiX")
        columns = [desc[0] for desc in access_cursor.description]
        print(f"DBUkeoiX columns ({len(columns)}): {columns[:10]}...")
    except Exception as e:
        print(f"Error: Could not access DBUkeoiX: {e}")
        return 0, employee_number_start

    rows = access_cursor.fetchall()
    print(f"Found {len(rows)} 請負社員 records")

    imported = 0
    emp_num = employee_number_start

    for row in rows:
        try:
            row_dict = dict(zip(columns, row))

            # Create employee record
            employee_data = {
                'employee_number': emp_num,
                'status': safe_str(row_dict.get('現在', '在職中'), 20) or '在職中',
                'office': safe_str(row_dict.get('事務所'), 50),
                'full_name': safe_str(row_dict.get('氏名'), 100) or f"Ukeoi_{emp_num}",
                'name_kana': safe_str(row_dict.get('カナ'), 100),
                'gender': safe_str(row_dict.get('性別'), 10),
                'nationality': safe_str(row_dict.get('国籍'), 50),
                'birth_date': safe_date(row_dict.get('生年月日')),
                'visa_expiry': safe_date(row_dict.get('ビザ期限')),
                'visa_type': safe_str(row_dict.get('ビザ種類'), 100),
                'has_spouse': bool(row_dict.get('配偶者')) if row_dict.get('配偶者') else None,
                'postal_code': safe_str(row_dict.get('〒'), 10),
                'address': safe_str(row_dict.get('住所')),
                'building_name': safe_str(row_dict.get('建物名'), 100),
                'hire_date': safe_date(row_dict.get('入社日')),
                'termination_date': safe_date(row_dict.get('退社日')),
                'employment_type': 'ukeoi',
                'created_at': datetime.now().isoformat(),
            }

            columns_str = ', '.join(employee_data.keys())
            placeholders = ', '.join(['?' for _ in employee_data])
            sqlite_cursor.execute(
                f"INSERT INTO employees ({columns_str}) VALUES ({placeholders})",
                list(employee_data.values())
            )
            employee_id = sqlite_cursor.lastrowid

            # Create ukeoi_assignment record
            assignment_data = {
                'employee_id': employee_id,
                'status': safe_str(row_dict.get('現在', '在職中'), 20) or '在職中',
                'job_type': safe_str(row_dict.get('請負業務'), 200),
                'hourly_rate': safe_int(row_dict.get('時給')),
                'hourly_rate_history': safe_str(row_dict.get('時給改定')),
                'profit_margin': safe_int(row_dict.get('差額利益')),
                'standard_salary': safe_int(row_dict.get('標準報酬')),
                'health_insurance': safe_int(row_dict.get('健康保険')),
                'nursing_insurance': safe_int(row_dict.get('介護保険')),
                'pension': safe_int(row_dict.get('厚生年金')),
                'social_insurance_enrolled': bool(row_dict.get('社保加入')) if row_dict.get('社保加入') else None,
                'commute_distance': safe_float(row_dict.get('通勤距離')),
                'transport_allowance': safe_int(row_dict.get('交通費')),
                'apartment_name': safe_str(row_dict.get('ｱﾊﾟｰﾄ'), 100),
                'move_in_date': safe_date(row_dict.get('入居')),
                'move_out_date': safe_date(row_dict.get('退去')),
                'start_date': safe_date(row_dict.get('入社日')),
                'end_date': safe_date(row_dict.get('退社日')),
                'visa_alert': safe_str(row_dict.get('ｱﾗｰﾄ(ﾋﾞｻﾞ更新)'), 50),
                'bank_account_name': safe_str(row_dict.get('口座名義'), 100),
                'bank_name': safe_str(row_dict.get('銀行名'), 100),
                'branch_number': safe_str(row_dict.get('支店番号'), 10),
                'branch_name': safe_str(row_dict.get('支店名'), 100),
                'account_number': safe_str(row_dict.get('口座番号'), 20),
                'entry_request': safe_str(row_dict.get('入社依頼'), 50),
                'notes': safe_str(row_dict.get('備考')),
                'created_at': datetime.now().isoformat(),
            }

            columns_str = ', '.join(assignment_data.keys())
            placeholders = ', '.join(['?' for _ in assignment_data])
            sqlite_cursor.execute(
                f"INSERT INTO ukeoi_assignments ({columns_str}) VALUES ({placeholders})",
                list(assignment_data.values())
            )

            imported += 1
            emp_num += 1

        except Exception as e:
            print(f"  Error importing 請負社員: {e}")
            continue

    sqlite_conn.commit()
    print(f"Imported {imported} 請負社員")
    return imported, emp_num


def sync_employee_photos(sqlite_conn):
    """Sync photos from candidates to employees based on name + birth_date."""
    print("\n" + "="*60)
    print("SYNCING EMPLOYEE PHOTOS")
    print("="*60)

    cursor = sqlite_conn.cursor()

    # Find matches by name and birth_date
    query = """
    UPDATE employees
    SET photo_url = (
        SELECT c.photo_url
        FROM candidates c
        WHERE c.full_name = employees.full_name
          AND c.birth_date = employees.birth_date
          AND c.photo_url IS NOT NULL
        LIMIT 1
    )
    WHERE photo_url IS NULL
      AND EXISTS (
        SELECT 1 FROM candidates c
        WHERE c.full_name = employees.full_name
          AND c.birth_date = employees.birth_date
          AND c.photo_url IS NOT NULL
      )
    """

    cursor.execute(query)
    synced = cursor.rowcount
    sqlite_conn.commit()

    # Count employees with photos
    cursor.execute("SELECT COUNT(*) FROM employees WHERE photo_url IS NOT NULL")
    with_photos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM employees")
    total = cursor.fetchone()[0]

    print(f"Synced {synced} employee photos")
    print(f"Employees with photos: {with_photos}/{total} ({100*with_photos//total if total else 0}%)")

    return synced


def main():
    """Main import function."""
    print("="*60)
    print("ACCESS TO SQLITE IMPORT")
    print(f"Source: {ACCDB_PATH}")
    print(f"Target: {SQLITE_PATH}")
    print("="*60)

    # Connect to databases
    print("\nConnecting to databases...")

    try:
        access_conn = connect_access()
        print("  Access: Connected")
    except Exception as e:
        print(f"  ERROR: Could not connect to Access: {e}")
        return

    try:
        sqlite_conn = connect_sqlite()
        print("  SQLite: Connected")
    except Exception as e:
        print(f"  ERROR: Could not connect to SQLite: {e}")
        return

    # Clear existing data
    clear_sqlite_data(sqlite_conn)

    # Import candidates with photos
    candidates_count, photos_count = import_candidates(access_conn, sqlite_conn)

    # Import employees
    emp_num = 1
    staff_count, emp_num = import_employees_from_dbstaffx(access_conn, sqlite_conn, emp_num)
    haken_count, emp_num = import_employees_from_dbgenzaix(access_conn, sqlite_conn, emp_num)
    ukeoi_count, emp_num = import_employees_from_dbukeoi(access_conn, sqlite_conn, emp_num)

    # Sync employee photos
    synced_photos = sync_employee_photos(sqlite_conn)

    # Summary
    print("\n" + "="*60)
    print("IMPORT COMPLETE")
    print("="*60)
    print(f"Candidates imported: {candidates_count}")
    print(f"Photos imported: {photos_count}")
    print(f"Direct staff imported: {staff_count}")
    print(f"派遣社員 imported: {haken_count}")
    print(f"請負社員 imported: {ukeoi_count}")
    print(f"Total employees: {staff_count + haken_count + ukeoi_count}")
    print(f"Employee photos synced: {synced_photos}")
    print("="*60)

    # Close connections
    access_conn.close()
    sqlite_conn.close()


if __name__ == "__main__":
    main()
