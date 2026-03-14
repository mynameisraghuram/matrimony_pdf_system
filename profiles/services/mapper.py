"""
mapper.py

Maps Google Sheet / Google Form row data into the internal profile schema.

Aligned with:
D:\\rr_projects\\matrimony_pdf_system\\profiles\\models.py

This version is updated against your actual Google Sheet headers.
"""

from __future__ import annotations

import re


INTERNAL_FIELDS = [
    "profile_id",
    "email",
    "contact_number",
    "second_contact_number",

    "looking_for",
    "marital_status",

    "first_name",
    "last_name",
    "full_name",

    "date_of_birth",
    "time_of_birth",
    "place_of_birth",

    "star",
    "rasi",
    "sub_caste",
    "gothram",
    "height",

    "schooling",
    "graduation",
    "masters",
    "designation",
    "company_name",
    "salary",
    "years_of_exp",
    "job_location",
    "visa_status",

    "father_name",
    "father_occupation",
    "father_native",

    "mother_name",
    "mother_occupation",
    "mother_native",

    "siblings",
    "parents_staying",

    "actual_property",
    "shared_property",
    "expected_property",

    "preferred_height",
    "age_gap",
    "preferred_sub_caste",
    "astrology",
    "looking_country",
    "looking_state",
    "education_preference",
    "career_preferences",
    "special_conditions",

    "story_summary",

    # compatibility keys used elsewhere in pipeline
    "phone",
    "dob",
    "education",
    "profession",
    "company",
    "income",
    "city",
    "state",
    "country",
    "about_me",
    "gender",
    "age",
    "religion",
    "caste",
    "mother_tongue",
]


COLUMN_MAP = {
    "Timestamp": "profile_id",
    "Profile ID": "profile_id",

    "Email": "email",
    "Email Address": "email",
    "Email address": "email",

    "Contact Number": "contact_number",
    "Phone": "contact_number",
    "Mobile Number": "contact_number",

    "Second Contact Number": "second_contact_number",
    "WhatsApp Number": "second_contact_number",

    "Looking For": "looking_for",
    "Marital Status": "marital_status",

    "First Name": "first_name",
    "Last Name": "last_name",
    "Full Name": "full_name",
    "Name": "full_name",

    "Date of Birth": "date_of_birth",
    "DOB": "date_of_birth",
    "Time of Birth": "time_of_birth",
    "Place of Birth": "place_of_birth",

    "Star": "star",
    "Nakshatram": "star",
    "Rasi": "rasi",
    "Sub Caste": "sub_caste",
    "Gothram": "gothram",

    "Height": "height",
    "Height (Feet & Inches)": "height",

    "Schooling": "schooling",
    "Graduation": "graduation",
    "Masters": "masters",
    "Master's": "masters",

    "Designation": "designation",
    "Profession": "designation",

    "Company Name": "company_name",
    "Company": "company_name",

    "Salary": "salary",
    "Annual Income": "salary",
    "Years of Exp": "years_of_exp",
    "Years of Experience": "years_of_exp",
    "Job Location": "job_location",
    "Visa Status (if applicable)": "visa_status",
    "Visa Status": "visa_status",

    "Father Name": "father_name",
    "Occupation": "father_occupation",
    "Father Occupation": "father_occupation",
    "Father Native": "father_native",

    "Mother Name": "mother_name",
    "Occupation__2": "mother_occupation",
    "Mother Occupation": "mother_occupation",
    "Mother Native": "mother_native",

    "Sibling's": "siblings",
    "Siblings": "siblings",
    "Parents Staying": "parents_staying",

    "Actual Property (In Cr)": "actual_property",
    "Shared Property  (In Cr)": "shared_property",
    "Expected Property  (In Cr)": "expected_property",

    "Height (feet & Inches)": "preferred_height",
    "Preferred Height": "preferred_height",
    "Age Gap": "age_gap",
    "Sub - Caste": "preferred_sub_caste",
    "Preferred Sub Caste": "preferred_sub_caste",

    "Astrology": "astrology",
    "Looking Country": "looking_country",
    "Looking State": "looking_state",
    "Education Preferences": "education_preference",
    "Education Preference": "education_preference",
    "Career Preferences": "career_preferences",
    "Special Conditions": "special_conditions",

    "Story Summary": "story_summary",
    "About Me": "story_summary",
}


FIELD_ALIASES = {
    "profile_id": [
        "profile id",
        "timestamp",
        "submission id",
        "entry id",
    ],
    "email": [
        "email",
        "email address",
    ],
    "contact_number": [
        "contact number",
        "mobile",
        "mobile number",
        "phone",
        "phone number",
        "contact",
    ],
    "second_contact_number": [
        "second contact number",
        "alternate number",
        "secondary contact",
        "whatsapp number",
    ],
    "looking_for": [
        "looking for",
    ],
    "marital_status": [
        "marital status",
    ],
    "first_name": [
        "first name",
    ],
    "last_name": [
        "last name",
        "surname",
    ],
    "full_name": [
        "full name",
        "name",
    ],
    "date_of_birth": [
        "date of birth",
        "dob",
        "birth date",
    ],
    "time_of_birth": [
        "time of birth",
        "birth time",
    ],
    "place_of_birth": [
        "place of birth",
        "birth place",
    ],
    "star": [
        "star",
        "nakshatra",
    ],
    "rasi": [
        "rasi",
        "raasi",
    ],
    "sub_caste": [
        "sub caste",
        "subcaste",
    ],
    "gothram": [
        "gothram",
        "gotram",
        "gotra",
    ],
    "height": [
        "height",
        "height feet inches",
    ],
    "schooling": [
        "schooling",
        "school education",
    ],
    "graduation": [
        "graduation",
        "degree",
        "education",
    ],
    "masters": [
        "masters",
        "master's",
        "pg",
    ],
    "designation": [
        "designation",
        "profession",
        "occupation",
        "job title",
    ],
    "company_name": [
        "company name",
        "company",
        "employer",
    ],
    "salary": [
        "salary",
        "annual income",
        "income",
        "ctc",
    ],
    "years_of_exp": [
        "years of exp",
        "years of experience",
        "experience",
    ],
    "job_location": [
        "job location",
        "work location",
        "current location",
    ],
    "visa_status": [
        "visa status",
        "visa status if applicable",
    ],
    "father_name": [
        "father name",
        "father's name",
    ],
    "father_occupation": [
        "father occupation",
        "father's occupation",
    ],
    "father_native": [
        "father native",
        "father native place",
    ],
    "mother_name": [
        "mother name",
        "mother's name",
    ],
    "mother_occupation": [
        "mother occupation",
        "mother's occupation",
    ],
    "mother_native": [
        "mother native",
        "mother native place",
    ],
    "siblings": [
        "siblings",
        "sibling",
        "sibling's",
    ],
    "parents_staying": [
        "parents staying",
    ],
    "actual_property": [
        "actual property",
        "actual property in cr",
    ],
    "shared_property": [
        "shared property",
        "shared property in cr",
    ],
    "expected_property": [
        "expected property",
        "expected property in cr",
    ],
    "preferred_height": [
        "preferred height",
        "height feet inches 2",
    ],
    "age_gap": [
        "age gap",
    ],
    "preferred_sub_caste": [
        "preferred sub caste",
        "sub caste preference",
    ],
    "astrology": [
        "astrology",
    ],
    "looking_country": [
        "looking country",
    ],
    "looking_state": [
        "looking state",
    ],
    "education_preference": [
        "education preference",
        "education preferences",
        "preferred education",
    ],
    "career_preferences": [
        "career preference",
        "career preferences",
    ],
    "special_conditions": [
        "special conditions",
        "special condition",
    ],
    "story_summary": [
        "story summary",
        "about me",
        "bio",
    ],
}


def normalize_header(text) -> str:
    if text is None:
        return ""

    text = str(text).strip().lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("\\", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_value(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


def _build_normalized_alias_index() -> dict:
    alias_index = {}

    for internal_field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            alias_index[normalize_header(alias)] = internal_field

    for column_name, internal_field in COLUMN_MAP.items():
        alias_index[normalize_header(column_name)] = internal_field

    return alias_index


ALIAS_INDEX = _build_normalized_alias_index()


def _map_exact_columns(raw_row: dict, mapped: dict) -> None:
    for sheet_col, internal_field in COLUMN_MAP.items():
        if sheet_col in raw_row:
            mapped[internal_field] = clean_value(raw_row.get(sheet_col))


def _map_alias_columns(raw_row: dict, mapped: dict) -> None:
    for raw_key, raw_value in raw_row.items():
        normalized_key = normalize_header(raw_key)
        if not normalized_key:
            continue

        internal_field = ALIAS_INDEX.get(normalized_key)
        if not internal_field:
            continue

        current_value = mapped.get(internal_field)
        incoming_value = clean_value(raw_value)

        if current_value in (None, "") and incoming_value not in (None, ""):
            mapped[internal_field] = incoming_value


def _fill_compatibility_fields(mapped: dict) -> None:
    if not mapped.get("phone") and mapped.get("contact_number"):
        mapped["phone"] = mapped["contact_number"]

    if not mapped.get("dob") and mapped.get("date_of_birth"):
        mapped["dob"] = mapped["date_of_birth"]

    if not mapped.get("education"):
        mapped["education"] = (
            mapped.get("graduation")
            or mapped.get("masters")
            or mapped.get("schooling")
        )

    if not mapped.get("profession") and mapped.get("designation"):
        mapped["profession"] = mapped["designation"]

    if not mapped.get("company") and mapped.get("company_name"):
        mapped["company"] = mapped["company_name"]

    if not mapped.get("income") and mapped.get("salary"):
        mapped["income"] = mapped["salary"]

    if not mapped.get("city") and mapped.get("job_location"):
        mapped["city"] = mapped["job_location"]

    if not mapped.get("about_me") and mapped.get("story_summary"):
        mapped["about_me"] = mapped["story_summary"]


def _generate_full_name(mapped: dict) -> None:
    if mapped.get("full_name"):
        return

    first_name = mapped.get("first_name")
    last_name = mapped.get("last_name")

    if first_name and last_name:
        mapped["full_name"] = f"{first_name} {last_name}"
    elif first_name:
        mapped["full_name"] = first_name


def map_record(raw_row: dict) -> dict:
    mapped = {field: None for field in INTERNAL_FIELDS}

    if not isinstance(raw_row, dict):
        return mapped

    _map_exact_columns(raw_row, mapped)
    _map_alias_columns(raw_row, mapped)
    _fill_compatibility_fields(mapped)
    _generate_full_name(mapped)

    return mapped