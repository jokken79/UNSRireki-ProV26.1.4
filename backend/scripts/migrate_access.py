#!/usr/bin/env python3
"""
Migration script for Access T_履歴書 table to PostgreSQL candidates table.

This script extracts data from the legacy Access database and imports it
into the new PostgreSQL database.

Usage:
    python migrate_access.py --access-db "path/to/database.accdb" --output-dir "./exports"
"""
import os
import sys
import json
import argparse
from datetime import datetime, date
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Migrate Access T_履歴書 table to PostgreSQL"
    )
    parser.add_argument(
        "--access-db",
        required=True,
        help="Path to Access database file (.accdb or .mdb)"
    )
    parser.add_argument(
        "--output-dir",
        default="./exports",
        help="Directory to export extracted data"
    )
    parser.add_argument(
        "--extract-attachments",
        action="store_true",
        help="Extract attachment files (photos, documents)"
    )
    return parser.parse_args()


def connect_access(db_path: str):
    """Connect to Access database using pyodbc."""
    try:
        import pyodbc
    except ImportError:
        print("Error: pyodbc is required. Install with: pip install pyodbc")
        sys.exit(1)

    # Connection string for Access
    if db_path.endswith('.accdb'):
        driver = '{Microsoft Access Driver (*.mdb, *.accdb)}'
    else:
        driver = '{Microsoft Access Driver (*.mdb)}'

    conn_str = f"DRIVER={driver};DBQ={db_path};"

    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error connecting to Access database: {e}")
        sys.exit(1)


def extract_candidates(conn) -> list:
    """Extract all candidates from T_履歴書 table."""
    cursor = conn.cursor()

    # Query all columns from T_履歴書
    query = """
    SELECT
        [履歴書ID],
        [氏名],
        [カナ],
        [性別],
        [国籍],
        [生年月日],
        [備考]
    FROM [T_履歴書]
    """

    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    candidates = []
    for row in rows:
        candidate = dict(zip(columns, row))

        # Convert dates
        if candidate.get('生年月日'):
            birth_date = candidate['生年月日']
            if isinstance(birth_date, datetime):
                candidate['birth_date'] = birth_date.strftime('%Y-%m-%d')
            elif isinstance(birth_date, date):
                candidate['birth_date'] = birth_date.strftime('%Y-%m-%d')

        # Map to new schema
        mapped = {
            'legacy_id': candidate.get('履歴書ID'),
            'full_name': candidate.get('氏名', ''),
            'name_kana': candidate.get('カナ'),
            'gender': candidate.get('性別'),
            'nationality': candidate.get('国籍'),
            'birth_date': candidate.get('birth_date'),
            'notes': candidate.get('備考'),
            'status': 'registered',
        }

        candidates.append(mapped)

    return candidates


def extract_attachments(conn, output_dir: str):
    """
    Extract attachments from 写真 field.

    Access attachments are stored as binary data and require special handling.
    This function creates a VBA script that can be run in Access to export files.
    """
    vba_script = '''
' VBA Script to export attachments from T_履歴書
' Run this in Access VBA editor

Public Sub ExportAttachments()
    Dim db As DAO.Database
    Dim rs As DAO.Recordset
    Dim rsAtt As DAO.Recordset2
    Dim fld As DAO.Field2
    Dim strPath As String
    Dim id As Variant

    strPath = "C:\\ExportedFiles\\"

    If Dir(strPath, vbDirectory) = "" Then
        MkDir strPath
    End If

    Set db = CurrentDb
    Set rs = db.OpenRecordset("SELECT [履歴書ID], [写真] FROM T_履歴書 WHERE [写真] Is Not Null;")

    Do While Not rs.EOF
        id = rs.Fields("履歴書ID").Value
        Set fld = rs.Fields("写真")

        If Not IsNull(fld.Value) Then
            Set rsAtt = fld.Value

            Do While Not rsAtt.EOF
                rsAtt.Fields("FileData").SaveToFile strPath & id & "_" & rsAtt.Fields("FileName").Value
                rsAtt.MoveNext
            Loop
        End If

        rs.MoveNext
    Loop

    rs.Close
    MsgBox "Export completed to " & strPath
End Sub
'''

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    vba_path = output_path / "export_attachments.vba"
    with open(vba_path, 'w', encoding='utf-8') as f:
        f.write(vba_script)

    print(f"VBA script saved to: {vba_path}")
    print("Run this script in Access VBA editor to export attachments.")


def save_json(data: list, output_path: str):
    """Save extracted data to JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    print(f"Saved {len(data)} candidates to: {output_path}")


def main():
    args = parse_args()

    print(f"Connecting to Access database: {args.access_db}")
    conn = connect_access(args.access_db)

    print("Extracting candidates from T_履歴書...")
    candidates = extract_candidates(conn)
    print(f"Found {len(candidates)} candidates")

    # Save to JSON
    output_path = Path(args.output_dir) / "candidates.json"
    save_json(candidates, str(output_path))

    # Extract attachments if requested
    if args.extract_attachments:
        print("Generating VBA script for attachment extraction...")
        extract_attachments(conn, args.output_dir)

    conn.close()
    print("Migration completed successfully!")


if __name__ == "__main__":
    main()
