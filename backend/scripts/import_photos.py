"""
Photo Import Script for UNS Rirekisho Pro
Imports photos from legacy system and links them to candidates/employees.

Photos source: JpkkenRirekisho12.24v1.0/public/photos
JSON mapping: JpkkenRirekisho12.24v1.0/legacy_resumes.json

Usage:
    python scripts/import_photos.py --dry-run   # Preview only
    python scripts/import_photos.py             # Execute import
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select, func, and_
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import Candidate, Employee


# Paths
PHOTOS_DIR = Path("C:/Users/Jpkken/UNSRireki-Prov26.1.4/backend/uploads/photos")
LEGACY_JSON = Path("C:/Users/Jpkken/JpkkenRirekisho12.24v1.0/legacy_resumes.json")


def parse_date(date_str):
    """Parse date from various formats."""
    if not date_str or date_str == "NaT":
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def load_legacy_resumes():
    """Load legacy resumes JSON."""
    print(f"Loading legacy resumes from: {LEGACY_JSON}")
    with open(LEGACY_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  Loaded {len(data)} records")
    return data


def get_available_photos():
    """Get set of available photo filenames."""
    if not PHOTOS_DIR.exists():
        print(f"ERROR: Photos directory not found: {PHOTOS_DIR}")
        return set()

    photos = set()
    for f in PHOTOS_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            photos.add(f.name)

    print(f"  Found {len(photos)} photo files")
    return photos


def import_photos_to_candidates(session, dry_run=True):
    """Import photos to candidates based on legacy_resumes.json."""
    print("\n" + "="*60)
    print("PHASE 1: Import photos to CANDIDATES")
    print("="*60)

    # Load data
    resumes = load_legacy_resumes()
    available_photos = get_available_photos()

    stats = {
        'matched': 0,
        'no_photo': 0,
        'photo_not_found': 0,
        'candidate_not_found': 0,
        'already_has_photo': 0,
        'errors': 0
    }

    # Get all candidates for matching
    candidates = session.execute(select(Candidate)).scalars().all()
    print(f"  Found {len(candidates)} candidates in database")

    # Create lookup maps
    by_legacy_id = {c.legacy_id: c for c in candidates if c.legacy_id}
    by_name_dob = {}
    for c in candidates:
        if c.full_name and c.birth_date:
            key = (c.full_name.strip().upper(), str(c.birth_date))
            by_name_dob[key] = c

    print(f"  Lookup: {len(by_legacy_id)} by legacy_id, {len(by_name_dob)} by name+dob")

    # Process each resume
    for resume in resumes:
        legacy_id = resume.get('履歴書ID')
        photo_filename = resume.get('写真', '')
        name = resume.get('氏名', '')
        dob_str = resume.get('生年月日', '')

        # Skip if no photo
        if not photo_filename:
            stats['no_photo'] += 1
            continue

        # Check if photo exists
        if photo_filename not in available_photos:
            stats['photo_not_found'] += 1
            continue

        # Find candidate
        candidate = None

        # Try by legacy_id first
        if legacy_id and legacy_id in by_legacy_id:
            candidate = by_legacy_id[legacy_id]

        # Try by name + dob
        if not candidate and name and dob_str:
            dob = parse_date(dob_str)
            if dob:
                key = (name.strip().upper(), str(dob))
                candidate = by_name_dob.get(key)

        if not candidate:
            stats['candidate_not_found'] += 1
            continue

        # Skip if already has photo
        if candidate.photo_url:
            stats['already_has_photo'] += 1
            continue

        # Set photo URL
        photo_url = f"/uploads/photos/{photo_filename}"

        if not dry_run:
            candidate.photo_url = photo_url

        stats['matched'] += 1

        if stats['matched'] <= 5:
            print(f"  + {candidate.full_name} -> {photo_filename}")

    # Commit if not dry run
    if not dry_run:
        session.commit()
        print("\n  Changes committed to database.")

    print("\n  --- Candidate Photo Import Stats ---")
    print(f"  Matched & updated: {stats['matched']}")
    print(f"  Already has photo: {stats['already_has_photo']}")
    print(f"  No photo in JSON: {stats['no_photo']}")
    print(f"  Photo file not found: {stats['photo_not_found']}")
    print(f"  Candidate not found: {stats['candidate_not_found']}")

    return stats


def import_photos_to_employees_by_number(session, dry_run=True):
    """Import photos to employees based on employee number matching filename."""
    print("\n" + "="*60)
    print("PHASE 2: Import photos to EMPLOYEES (by employee number)")
    print("="*60)

    available_photos = get_available_photos()

    # Get all employees
    employees = session.execute(select(Employee)).scalars().all()
    print(f"  Found {len(employees)} employees in database")

    stats = {
        'matched': 0,
        'already_has_photo': 0,
        'no_matching_photo': 0
    }

    for emp in employees:
        if not emp.employee_number:
            continue

        # Skip if already has photo
        if emp.photo_url:
            stats['already_has_photo'] += 1
            continue

        # Look for photo matching employee number
        emp_num = str(emp.employee_number).strip()

        # Try various extensions
        photo_found = None
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            filename = f"{emp_num}{ext}"
            if filename in available_photos:
                photo_found = filename
                break

        if not photo_found:
            stats['no_matching_photo'] += 1
            continue

        # Set photo URL
        photo_url = f"/uploads/photos/{photo_found}"

        if not dry_run:
            emp.photo_url = photo_url

        stats['matched'] += 1

        if stats['matched'] <= 5:
            print(f"  + {emp.full_name} ({emp_num}) -> {photo_found}")

    if not dry_run:
        session.commit()
        print("\n  Changes committed to database.")

    print("\n  --- Employee Photo Import Stats ---")
    print(f"  Matched & updated: {stats['matched']}")
    print(f"  Already has photo: {stats['already_has_photo']}")
    print(f"  No matching photo: {stats['no_matching_photo']}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Import photos from legacy system')
    parser.add_argument('--dry-run', action='store_true', help='Preview only, no changes')
    args = parser.parse_args()

    print("="*60)
    print("UNS Rirekisho Pro - Photo Import Script")
    print("="*60)

    if args.dry_run:
        print("MODE: DRY RUN (no changes will be made)")
    else:
        print("MODE: LIVE (changes will be saved to database)")

    # Database connection (synchronous for script)
    db_url = str(settings.DATABASE_URL).replace('+aiosqlite', '')
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Phase 1: Import to candidates
        candidate_stats = import_photos_to_candidates(session, dry_run=args.dry_run)

        # Phase 2: Import to employees by number
        employee_stats = import_photos_to_employees_by_number(session, dry_run=args.dry_run)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Candidates with photos: {candidate_stats['matched']}")
    print(f"Employees with photos: {employee_stats['matched']}")

    if args.dry_run:
        print("\nThis was a DRY RUN. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
