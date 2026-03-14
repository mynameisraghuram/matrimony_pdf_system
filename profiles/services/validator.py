"""
validator.py

Responsible for validating normalized profile data before saving to DB
or using it for PDF generation.

This version is aligned with:
D:\\rr_projects\\matrimony_pdf_system\\profiles\\models.py
"""

from __future__ import annotations

import re
from datetime import datetime


REQUIRED_FIELDS = [
    "profile_id",
    "first_name",
]


def _clean(value):
    """
    Normalize empty values.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


def is_valid_email(email) -> bool:
    """
    Validate email format.
    Empty email is allowed.
    """
    email = _clean(email)
    if not email:
        return True

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_phone(phone) -> bool:
    """
    Validate phone number.
    Accepts:
    - +919876543210
    - 919876543210
    - 9876543210
    """
    phone = _clean(phone)
    if not phone:
        return False

    digits = re.sub(r"\D", "", str(phone))

    if len(digits) == 10:
        return True

    if len(digits) == 12 and digits.startswith("91"):
        return True

    return False


def is_valid_date(date_value) -> bool:
    """
    Validate date in YYYY-MM-DD format.
    Empty value is allowed.
    """
    date_value = _clean(date_value)
    if not date_value:
        return True

    try:
        datetime.strptime(str(date_value), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_height(height) -> bool:
    """
    Validate height in normalized format:
    X ft Y in
    Empty value is allowed.
    """
    height = _clean(height)
    if not height:
        return True

    pattern = r"^\d+\s*ft\s*\d{1,2}\s*in$"
    return re.match(pattern, str(height).strip().lower()) is not None


def is_valid_profile_id(profile_id) -> bool:
    """
    Validate profile_id presence and basic size.
    """
    profile_id = _clean(profile_id)
    if not profile_id:
        return False

    profile_id = str(profile_id)
    return 1 <= len(profile_id) <= 50


def validate_required_fields(data: dict) -> list[str]:
    """
    Check required fields.
    """
    errors = []

    for field in REQUIRED_FIELDS:
        value = _clean(data.get(field))
        if value is None:
            errors.append(f"{field} is required")

    return errors


def validate_record(data: dict) -> dict:
    """
    Validate a normalized profile record.

    Returns:
        {
            "is_valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "cleaned_data": dict
        }
    """
    errors = []
    warnings = []

    cleaned_data = {key: _clean(value) for key, value in data.items()}

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------
    errors.extend(validate_required_fields(cleaned_data))

    # ---------------------------------------------------------
    # Profile ID
    # ---------------------------------------------------------
    if cleaned_data.get("profile_id") and not is_valid_profile_id(cleaned_data.get("profile_id")):
        errors.append("profile_id is invalid")

    # ---------------------------------------------------------
    # Email
    # ---------------------------------------------------------
    if not is_valid_email(cleaned_data.get("email")):
        errors.append("email format is invalid")

    # ---------------------------------------------------------
    # Contact numbers
    # ---------------------------------------------------------
    contact_number = cleaned_data.get("contact_number") or cleaned_data.get("phone")
    if not contact_number:
        errors.append("contact_number is required")
    elif not is_valid_phone(contact_number):
        warnings.append("contact_number format is not a standard 10-digit Indian number")

    second_contact_number = cleaned_data.get("second_contact_number")
    if second_contact_number and not is_valid_phone(second_contact_number):
        warnings.append("second_contact_number format is not a standard 10-digit Indian number")

    # keep compatibility key synchronized
    cleaned_data["contact_number"] = contact_number
    cleaned_data["phone"] = contact_number

    # ---------------------------------------------------------
    # Date of birth
    # ---------------------------------------------------------
    date_of_birth = cleaned_data.get("date_of_birth") or cleaned_data.get("dob")
    if not is_valid_date(date_of_birth):
        errors.append("date_of_birth must be in YYYY-MM-DD format")

    cleaned_data["date_of_birth"] = date_of_birth
    cleaned_data["dob"] = date_of_birth

    # ---------------------------------------------------------
    # Heights
    # ---------------------------------------------------------
    if not is_valid_height(cleaned_data.get("height")):
        warnings.append("height is not in normalized format like '5 ft 8 in'")

    pref_h = cleaned_data.get("preferred_height") or ""
    is_range = " to " in pref_h
    if not is_range and not is_valid_height(pref_h or None):
        warnings.append("preferred_height is not in normalized format like '5 ft 4 in'")

    # ---------------------------------------------------------
    # Name warnings
    # ---------------------------------------------------------
    if not cleaned_data.get("full_name"):
        warnings.append("full_name is missing")

    if not cleaned_data.get("last_name"):
        warnings.append("last_name is missing")

    # ---------------------------------------------------------
    # Optional informational warnings
    # ---------------------------------------------------------
    if not cleaned_data.get("graduation") and not cleaned_data.get("education"):
        warnings.append("education details are missing")

    if not cleaned_data.get("designation") and not cleaned_data.get("profession"):
        warnings.append("designation/profession is missing")

    if not cleaned_data.get("company_name") and not cleaned_data.get("company"):
        warnings.append("company details are missing")

    if not cleaned_data.get("salary") and not cleaned_data.get("income"):
        warnings.append("salary/income is missing")

    if not cleaned_data.get("story_summary") and not cleaned_data.get("about_me"):
        warnings.append("story summary/about me is missing")

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "cleaned_data": cleaned_data,
    }