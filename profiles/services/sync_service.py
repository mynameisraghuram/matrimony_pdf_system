from profiles.models import Profile
from profiles.services.sheet_reader import fetch_sheet_rows
from profiles.services.mapper import map_record
from profiles.services.normalizer import normalize_record
from profiles.services.validator import validate_record


def _clean_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value


def _get_first_non_empty(record, *keys):
    for key in keys:
        value = _clean_value(record.get(key))
        if value is not None:
            return value
    return None


def _build_profile_id(record, raw_row=None):
    profile_id = _clean_value(record.get("profile_id"))
    if profile_id:
        return str(profile_id)

    email = _clean_value(record.get("email"))
    if email:
        return f"EMAIL_{email}"

    phone = _clean_value(record.get("phone")) or _clean_value(record.get("contact_number"))
    if phone:
        return f"PHONE_{phone}"

    full_name = _clean_value(record.get("full_name"))
    if full_name:
        return f"NAME_{str(full_name).replace(' ', '_')}"

    raw_size = len(raw_row) if isinstance(raw_row, dict) else 0
    return f"ROW_{raw_size}"


def _build_profile_defaults(record):
    first_name = _get_first_non_empty(record, "first_name")
    last_name = _get_first_non_empty(record, "last_name")
    full_name = _get_first_non_empty(record, "full_name")

    if not full_name:
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name

    return {
        "email": _get_first_non_empty(record, "email"),
        "contact_number": _get_first_non_empty(record, "phone", "contact_number"),
        "second_contact_number": _get_first_non_empty(record, "second_contact_number"),
        "looking_for": _get_first_non_empty(record, "looking_for"),
        "marital_status": _get_first_non_empty(record, "marital_status"),
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "date_of_birth": _get_first_non_empty(record, "dob", "date_of_birth"),
        "time_of_birth": _get_first_non_empty(record, "time_of_birth"),
        "place_of_birth": _get_first_non_empty(record, "place_of_birth"),
        "star": _get_first_non_empty(record, "star"),
        "rasi": _get_first_non_empty(record, "rasi"),
        "sub_caste": _get_first_non_empty(record, "sub_caste"),
        "gothram": _get_first_non_empty(record, "gothram"),
        "height": _get_first_non_empty(record, "height"),
        "schooling": _get_first_non_empty(record, "schooling"),
        "graduation": _get_first_non_empty(record, "graduation", "education"),
        "masters": _get_first_non_empty(record, "masters"),
        "designation": _get_first_non_empty(record, "designation", "profession"),
        "company_name": _get_first_non_empty(record, "company_name", "company"),
        "salary": _get_first_non_empty(record, "salary", "income"),
        "years_of_exp": _get_first_non_empty(record, "years_of_exp"),
        "job_location": _get_first_non_empty(record, "job_location", "city"),
        "visa_status": _get_first_non_empty(record, "visa_status"),
        "father_name": _get_first_non_empty(record, "father_name"),
        "father_occupation": _get_first_non_empty(record, "father_occupation"),
        "father_native": _get_first_non_empty(record, "father_native"),
        "mother_name": _get_first_non_empty(record, "mother_name"),
        "mother_occupation": _get_first_non_empty(record, "mother_occupation"),
        "mother_native": _get_first_non_empty(record, "mother_native"),
        "siblings": _get_first_non_empty(record, "siblings"),
        "parents_staying": _get_first_non_empty(record, "parents_staying"),
        "actual_property": _get_first_non_empty(record, "actual_property"),
        "shared_property": _get_first_non_empty(record, "shared_property"),
        "expected_property": _get_first_non_empty(record, "expected_property"),
        "preferred_height": _get_first_non_empty(record, "preferred_height"),
        "age_gap": _get_first_non_empty(record, "age_gap"),
        "preferred_sub_caste": _get_first_non_empty(record, "preferred_sub_caste"),
        "astrology": _get_first_non_empty(record, "astrology"),
        "looking_country": _get_first_non_empty(record, "looking_country"),
        "looking_state": _get_first_non_empty(record, "looking_state"),
        "education_preference": _get_first_non_empty(record, "education_preference"),
        "career_preferences": _get_first_non_empty(record, "career_preferences"),
        "special_conditions": _get_first_non_empty(record, "special_conditions"),
        "story_summary": _get_first_non_empty(record, "story_summary", "about_me"),
    }


def sync_profiles_from_sheet():
    """
    Sync all rows from Google Sheet into the database.
    Returns a dict with counts: total, created, updated, invalid, errors.
    """
    rows = fetch_sheet_rows()

    result = {"total": 0, "created": 0, "updated": 0, "invalid": 0, "errors": 0}

    if not rows:
        return result

    result["total"] = len(rows)

    for raw_row in rows:
        try:
            mapped = map_record(raw_row)
            normalized = normalize_record(mapped)
            validation = validate_record(normalized)
            profile_id = _build_profile_id(normalized, raw_row)

            if not validation["is_valid"]:
                result["invalid"] += 1
                continue

            cleaned = validation["cleaned_data"]
            defaults = _build_profile_defaults(cleaned)

            _, created = Profile.objects.update_or_create(
                profile_id=profile_id,
                defaults=defaults,
            )

            if created:
                result["created"] += 1
            else:
                result["updated"] += 1

        except Exception:
            result["errors"] += 1

    return result
