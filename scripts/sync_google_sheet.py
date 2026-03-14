"""
sync_google_sheet.py

Reads rows from Google Sheet, maps them into internal schema,
normalizes values, validates records, and saves valid profiles
into the Django database.

Model target:
D:\\rr_projects\\matrimony_pdf_system\\profiles\\models.py
"""

import os
import sys
from pathlib import Path

import django

# -------------------------------------------------------------------
# Django setup
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from profiles.models import Profile  # noqa: E402
from profiles.services.sheet_reader import fetch_sheet_rows  # noqa: E402
from profiles.services.mapper import map_record  # noqa: E402
from profiles.services.normalizer import normalize_record  # noqa: E402
from profiles.services.validator import validate_record  # noqa: E402


def clean_value(value):
    """
    Convert empty strings to None and strip string values.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


def build_profile_id(record: dict, raw_row: dict | None = None) -> str:
    """
    Build a stable profile_id.

    Priority:
    1. mapped profile_id
    2. email
    3. phone/contact number
    4. full_name
    5. fallback from raw row length
    """
    profile_id = clean_value(record.get("profile_id"))
    if profile_id:
        return str(profile_id)

    email = clean_value(record.get("email"))
    if email:
        return f"EMAIL_{email}"

    phone = clean_value(record.get("phone")) or clean_value(record.get("contact_number"))
    if phone:
        return f"PHONE_{phone}"

    full_name = clean_value(record.get("full_name"))
    if full_name:
        safe_name = str(full_name).replace(" ", "_")
        return f"NAME_{safe_name}"

    raw_size = len(raw_row) if isinstance(raw_row, dict) else 0
    return f"ROW_{raw_size}"


def get_first_non_empty(record: dict, *keys):
    """
    Return first non-empty value from the provided keys.
    """
    for key in keys:
        value = clean_value(record.get(key))
        if value is not None:
            return value
    return None


def build_profile_defaults(record: dict) -> dict:
    """
    Convert normalized pipeline record into the actual Profile model fields.
    This mapping is aligned to:

    D:\\rr_projects\\matrimony_pdf_system\\profiles\\models.py
    """
    first_name = get_first_non_empty(record, "first_name")
    last_name = get_first_non_empty(record, "last_name")
    full_name = get_first_non_empty(record, "full_name")

    if not full_name:
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name

    defaults = {
        "email": get_first_non_empty(record, "email"),
        "contact_number": get_first_non_empty(record, "phone", "contact_number"),
        "second_contact_number": get_first_non_empty(record, "second_contact_number"),

        "looking_for": get_first_non_empty(record, "looking_for"),
        "marital_status": get_first_non_empty(record, "marital_status"),

        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,

        "date_of_birth": get_first_non_empty(record, "dob", "date_of_birth"),
        "time_of_birth": get_first_non_empty(record, "time_of_birth"),
        "place_of_birth": get_first_non_empty(record, "place_of_birth"),

        "star": get_first_non_empty(record, "star"),
        "rasi": get_first_non_empty(record, "rasi"),
        "sub_caste": get_first_non_empty(record, "sub_caste"),
        "gothram": get_first_non_empty(record, "gothram"),
        "height": get_first_non_empty(record, "height"),

        "schooling": get_first_non_empty(record, "schooling"),
        "graduation": get_first_non_empty(record, "graduation", "education"),
        "masters": get_first_non_empty(record, "masters"),
        "designation": get_first_non_empty(record, "designation", "profession"),
        "company_name": get_first_non_empty(record, "company_name", "company"),
        "salary": get_first_non_empty(record, "salary", "income"),
        "years_of_exp": get_first_non_empty(record, "years_of_exp"),
        "job_location": get_first_non_empty(record, "job_location", "city"),
        "visa_status": get_first_non_empty(record, "visa_status"),

        "father_name": get_first_non_empty(record, "father_name"),
        "father_occupation": get_first_non_empty(record, "father_occupation"),
        "father_native": get_first_non_empty(record, "father_native"),

        "mother_name": get_first_non_empty(record, "mother_name"),
        "mother_occupation": get_first_non_empty(record, "mother_occupation"),
        "mother_native": get_first_non_empty(record, "mother_native"),

        "siblings": get_first_non_empty(record, "siblings"),
        "parents_staying": get_first_non_empty(record, "parents_staying"),

        "actual_property": get_first_non_empty(record, "actual_property"),
        "shared_property": get_first_non_empty(record, "shared_property"),
        "expected_property": get_first_non_empty(record, "expected_property"),

        "preferred_height": get_first_non_empty(record, "preferred_height"),
        "age_gap": get_first_non_empty(record, "age_gap"),
        "preferred_sub_caste": get_first_non_empty(record, "preferred_sub_caste"),
        "astrology": get_first_non_empty(record, "astrology"),
        "looking_country": get_first_non_empty(record, "looking_country"),
        "looking_state": get_first_non_empty(record, "looking_state"),
        "education_preference": get_first_non_empty(record, "education_preference"),
        "career_preferences": get_first_non_empty(record, "career_preferences"),
        "special_conditions": get_first_non_empty(record, "special_conditions"),

        "story_summary": get_first_non_empty(record, "story_summary", "about_me"),
    }

    return defaults


def sync_google_sheet():
    """
    Main sync function.
    """
    print("=" * 80)
    print("Starting Google Sheet sync")
    print("=" * 80)

    rows = fetch_sheet_rows()

    if not rows:
        print("No rows found in Google Sheet.")
        return

    total_rows = len(rows)
    created_count = 0
    updated_count = 0
    skipped_count = 0
    invalid_count = 0
    error_count = 0

    print(f"Total rows fetched: {total_rows}")
    print("-" * 80)

    for index, raw_row in enumerate(rows, start=1):
        print(f"[Row {index}/{total_rows}] Processing...")

        try:
            mapped = map_record(raw_row)
            normalized = normalize_record(mapped)
            validation = validate_record(normalized)

            profile_id = build_profile_id(normalized, raw_row)

            if not validation["is_valid"]:
                invalid_count += 1
                print("  Status    : INVALID")
                print(f"  Profile ID: {profile_id}")
                print(f"  Errors    : {validation['errors']}")
                if validation["warnings"]:
                    print(f"  Warnings  : {validation['warnings']}")
                print("-" * 80)
                continue

            cleaned = validation["cleaned_data"]
            defaults = build_profile_defaults(cleaned)

            obj, created = Profile.objects.update_or_create(
                profile_id=profile_id,
                defaults=defaults,
            )

            if created:
                created_count += 1
                status_text = "CREATED"
            else:
                updated_count += 1
                status_text = "UPDATED"

            print(f"  Status    : {status_text}")
            print(f"  Profile ID: {obj.profile_id}")
            print(f"  Name      : {obj.full_name or obj.first_name or 'N/A'}")
            print(f"  Email     : {obj.email or 'N/A'}")
            print(f"  Contact   : {obj.contact_number or 'N/A'}")

            if validation["warnings"]:
                print(f"  Warnings  : {validation['warnings']}")

        except Exception as exc:
            error_count += 1
            print("  Status    : ERROR")
            print(f"  Reason    : {exc}")

        print("-" * 80)

    skipped_count = total_rows - (created_count + updated_count + invalid_count + error_count)

    print("=" * 80)
    print("Google Sheet sync completed")
    print("=" * 80)
    print(f"Total rows : {total_rows}")
    print(f"Created    : {created_count}")
    print(f"Updated    : {updated_count}")
    print(f"Invalid    : {invalid_count}")
    print(f"Errors     : {error_count}")
    print(f"Skipped    : {skipped_count}")
    print("=" * 80)


if __name__ == "__main__":
    sync_google_sheet()