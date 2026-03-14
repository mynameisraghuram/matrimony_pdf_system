"""
normalizer.py

Responsible for cleaning and normalizing mapped profile data.

Aligned with:
D:\\rr_projects\\matrimony_pdf_system\\profiles\\models.py

This version is updated for your real Google Form values, including:
- height values like: 5.3
- preferred height ranges like: 5.6 to 6.0
- visa status values like: NA / None
- multiline and free-text cleanup
"""

from __future__ import annotations

import re
from datetime import datetime


NULL_LIKE_VALUES = {
    "",
    "na",
    "n/a",
    "none",
    "null",
    "-",
    "--",
    "nil",
    "not applicable",
}


def clean_text(value):
    """
    Trim text and convert null-like values to None.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = re.sub(r"\s+", " ", value).strip()
        if not value:
            return None
        if value.lower() in NULL_LIKE_VALUES:
            return None
        return value

    return value


def normalize_email(email):
    """
    Normalize email to lowercase.
    """
    email = clean_text(email)
    if not email:
        return None
    return email.lower()


def normalize_phone(phone):
    """
    Normalize Indian phone numbers.

    Valid conversions:
    9876543210         -> +919876543210
    +91 9876543210     -> +919876543210
    0919876543210      -> +919876543210

    Invalid/short numbers are returned cleaned as-is so validator can flag them.
    """
    phone = clean_text(phone)
    if not phone:
        return None

    digits = re.sub(r"\D", "", str(phone))

    if digits.startswith("0091") and len(digits) == 14:
        digits = digits[4:]
    elif digits.startswith("091") and len(digits) == 13:
        digits = digits[3:]
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]

    if len(digits) == 10:
        return f"+91{digits}"

    return phone


def normalize_date(date_value):
    """
    Normalize date to YYYY-MM-DD when possible.
    """
    date_value = clean_text(date_value)
    if not date_value:
        return None

    value = str(date_value).strip()

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d.%m.%Y",
        "%d %m %Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return value


def normalize_name(name):
    """
    Normalize names with title casing.
    """
    name = clean_text(name)
    if not name:
        return None

    name = re.sub(r"\s+", " ", name)
    return name.title()


def normalize_sentence_text(value):
    """
    Cleanup normal text fields without forcing title case.
    """
    value = clean_text(value)
    if not value:
        return None
    return value


def normalize_multiline_text(value):
    """
    Normalize free text / notes / summaries.
    """
    value = clean_text(value)
    if not value:
        return None

    lines = str(value).splitlines()
    cleaned_lines = [re.sub(r"\s+", " ", line).strip() for line in lines if line.strip()]
    if cleaned_lines:
        return "\n".join(cleaned_lines)

    return re.sub(r"\s+", " ", str(value)).strip()


def _normalize_single_height_token(token):
    """
    Normalize a single height token.

    Supports:
    5.3   -> 5 ft 3 in
    5.10  -> 5 ft 10 in
    5'8   -> 5 ft 8 in
    5-8   -> 5 ft 8 in
    5 ft 8 in -> 5 ft 8 in
    5 8   -> 5 ft 8 in
    """
    token = clean_text(token)
    if not token:
        return None

    value = str(token).strip().lower()
    value = value.replace("feet", "ft").replace("foot", "ft").replace("inches", "in").replace("inch", "in")

    patterns = [
        r"^\s*(\d)\.(\d{1,2})\s*$",
        r"^\s*(\d)\s*'\s*(\d{1,2})\s*\"?\s*$",
        r"^\s*(\d)\s*-\s*(\d{1,2})\s*$",
        r"^\s*(\d)\s+(\d{1,2})\s*$",
        r"^\s*(\d)\s*ft\s*(\d{1,2})\s*in\s*$",
        r"^\s*(\d)\s*ft\s*(\d{1,2})\s*$",
    ]

    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            ft = int(match.group(1))
            inch = int(match.group(2))
            if 0 <= inch <= 11:
                return f"{ft} ft {inch} in"

    # already normalized
    match = re.match(r"^\s*(\d+)\s*ft\s*(\d{1,2})\s*in\s*$", value)
    if match:
        ft = int(match.group(1))
        inch = int(match.group(2))
        if 0 <= inch <= 11:
            return f"{ft} ft {inch} in"

    return token


def normalize_height(height):
    """
    Normalize profile height.

    Examples:
    5.3 -> 5 ft 3 in
    5.7 -> 5 ft 7 in
    5'8 -> 5 ft 8 in
    """
    return _normalize_single_height_token(height)


def normalize_height_range(height_value):
    """
    Normalize preferred height range.

    Examples:
    5.6 to 6.0        -> 5 ft 6 in to 6 ft 0 in
    5.4 - 5.8         -> 5 ft 4 in to 5 ft 8 in
    5.5               -> 5 ft 5 in
    """
    height_value = clean_text(height_value)
    if not height_value:
        return None

    value = str(height_value).strip()

    range_match = re.split(r"\s+(?:to)\s+|\s*-\s*", value, maxsplit=1)
    if len(range_match) == 2:
        left = _normalize_single_height_token(range_match[0])
        right = _normalize_single_height_token(range_match[1])

        if left and right:
            return f"{left} to {right}"

    return _normalize_single_height_token(value)


def generate_full_name(data):
    """
    Generate full_name if missing.
    """
    full_name = clean_text(data.get("full_name"))
    if full_name:
        return normalize_name(full_name)

    first_name = clean_text(data.get("first_name"))
    last_name = clean_text(data.get("last_name"))

    if first_name and last_name:
        return normalize_name(f"{first_name} {last_name}")

    if first_name:
        return normalize_name(first_name)

    return None


def normalize_record(data: dict) -> dict:
    """
    Normalize a mapped profile record.
    """
    normalized = {}

    for key, value in data.items():
        if isinstance(value, str):
            normalized[key] = clean_text(value)
        else:
            normalized[key] = value

    # ---------------------------------------------------------
    # Name fields
    # ---------------------------------------------------------
    normalized["first_name"] = normalize_name(normalized.get("first_name"))
    normalized["last_name"] = normalize_name(normalized.get("last_name"))
    normalized["full_name"] = generate_full_name(normalized)

    normalized["father_name"] = normalize_name(normalized.get("father_name"))
    normalized["mother_name"] = normalize_name(normalized.get("mother_name"))

    # ---------------------------------------------------------
    # Email and phone
    # ---------------------------------------------------------
    normalized["email"] = normalize_email(normalized.get("email"))

    normalized["contact_number"] = normalize_phone(
        normalized.get("contact_number") or normalized.get("phone")
    )
    normalized["second_contact_number"] = normalize_phone(
        normalized.get("second_contact_number")
    )

    normalized["phone"] = normalized.get("contact_number")

    # ---------------------------------------------------------
    # Date fields
    # ---------------------------------------------------------
    normalized["date_of_birth"] = normalize_date(
        normalized.get("date_of_birth") or normalized.get("dob")
    )
    normalized["dob"] = normalized.get("date_of_birth")

    # ---------------------------------------------------------
    # Height fields
    # ---------------------------------------------------------
    normalized["height"] = normalize_height(normalized.get("height"))
    normalized["preferred_height"] = normalize_height_range(normalized.get("preferred_height"))

    # ---------------------------------------------------------
    # Text cleanup
    # ---------------------------------------------------------
    sentence_fields = [
        "looking_for",
        "marital_status",
        "place_of_birth",
        "star",
        "rasi",
        "sub_caste",
        "gothram",
        "designation",
        "company_name",
        "salary",
        "years_of_exp",
        "job_location",
        "visa_status",
        "father_occupation",
        "father_native",
        "mother_occupation",
        "mother_native",
        "parents_staying",
        "actual_property",
        "shared_property",
        "expected_property",
        "age_gap",
        "preferred_sub_caste",
        "astrology",
        "looking_country",
        "looking_state",
        "education_preference",
        "career_preferences",
        "special_conditions",
        "education",
        "profession",
        "company",
        "income",
        "city",
        "state",
        "country",
        "gender",
        "age",
        "religion",
        "caste",
        "mother_tongue",
        "schooling",
        "graduation",
        "masters",
    ]

    for field in sentence_fields:
        normalized[field] = normalize_sentence_text(normalized.get(field))

    # ---------------------------------------------------------
    # Long text fields
    # ---------------------------------------------------------
    long_text_fields = [
        "siblings",
        "story_summary",
        "about_me",
    ]

    for field in long_text_fields:
        normalized[field] = normalize_multiline_text(normalized.get(field))

    # ---------------------------------------------------------
    # Compatibility fields
    # ---------------------------------------------------------
    normalized["designation"] = normalized.get("designation") or normalized.get("profession")
    normalized["company_name"] = normalized.get("company_name") or normalized.get("company")
    normalized["salary"] = normalized.get("salary") or normalized.get("income")
    normalized["job_location"] = normalized.get("job_location") or normalized.get("city")

    if not normalized.get("education"):
        normalized["education"] = (
            normalized.get("graduation")
            or normalized.get("masters")
            or normalized.get("schooling")
        )

    normalized["profession"] = normalized.get("designation")
    normalized["company"] = normalized.get("company_name")
    normalized["income"] = normalized.get("salary")
    normalized["city"] = normalized.get("job_location") or normalized.get("city")

    if not normalized.get("story_summary") and normalized.get("about_me"):
        normalized["story_summary"] = normalized.get("about_me")

    if not normalized.get("about_me") and normalized.get("story_summary"):
        normalized["about_me"] = normalized.get("story_summary")

    # ---------------------------------------------------------
    # Final cleanup
    # ---------------------------------------------------------
    for key, value in normalized.items():
        if isinstance(value, str):
            value = re.sub(r"[ \t]+", " ", value).strip()
            normalized[key] = value if value else None

    return normalized