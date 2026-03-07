import os
import sys
from pprint import pprint

# Add project root to Python path
PROJECT_ROOT = r"D:\rr_projects\matrimony_pdf_system"
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from profiles.services.sheet_reader import get_sheet_records
from profiles.services.mapper import map_record
from profiles.services.normalizer import normalize_record
from profiles.services.validator import validate_record


def main():
    rows = get_sheet_records()

    print(f"Total rows fetched: {len(rows)}")
    print("-" * 80)

    if not rows:
        print("No rows found in Google Sheet.")
        return

    first_row = rows[0]

    print("RAW ROW:")
    pprint(first_row)
    print("-" * 80)

    mapped = map_record(first_row)
    print("MAPPED ROW:")
    pprint(mapped)
    print("-" * 80)

    normalized = normalize_record(mapped)
    print("NORMALIZED ROW:")
    pprint(normalized)
    print("-" * 80)

    validation_result = validate_record(normalized)
    print("VALIDATION RESULT:")
    pprint(validation_result)
    print("-" * 80)


if __name__ == "__main__":
    main()