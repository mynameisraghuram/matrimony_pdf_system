"""
test_sheet_pipeline.py

Tests the complete Google Sheet pipeline without saving to DB.

Flow:
Google Sheet -> mapper -> normalizer -> validator

Useful for checking:
- raw sheet data
- mapped output
- normalized output
- validation result
before running actual DB sync
"""

import sys
from pathlib import Path


# -------------------------------------------------------------------
# Project path setup
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


from profiles.services.sheet_reader import fetch_sheet_rows
from profiles.services.mapper import map_record
from profiles.services.normalizer import normalize_record
from profiles.services.validator import validate_record


def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_dict(title: str, data: dict):
    print(f"\n{title}")
    print("-" * 80)

    if not data:
        print("No data")
        return

    for key, value in data.items():
        print(f"{key}: {value}")


def run_pipeline_test(max_rows: int = 5):
    print_section("Testing Google Sheet Pipeline")

    rows = fetch_sheet_rows()

    if not rows:
        print("No rows returned from Google Sheet.")
        return

    print(f"Rows fetched from sheet: {len(rows)}")
    print(f"Testing first {min(len(rows), max_rows)} row(s) only.")

    valid_count = 0
    invalid_count = 0

    for index, raw_row in enumerate(rows[:max_rows], start=1):
        print_section(f"ROW {index}")

        # -------------------------------------------------------------
        # Raw row
        # -------------------------------------------------------------
        print_dict("RAW SHEET DATA", raw_row)

        # -------------------------------------------------------------
        # Mapper
        # -------------------------------------------------------------
        mapped = map_record(raw_row)
        print_dict("MAPPED DATA", mapped)

        # -------------------------------------------------------------
        # Normalizer
        # -------------------------------------------------------------
        normalized = normalize_record(mapped)
        print_dict("NORMALIZED DATA", normalized)

        # -------------------------------------------------------------
        # Validator
        # -------------------------------------------------------------
        result = validate_record(normalized)

        print("\nVALIDATION RESULT")
        print("-" * 80)
        print(f"is_valid: {result['is_valid']}")

        print("\nErrors:")
        if result["errors"]:
            for err in result["errors"]:
                print(f" - {err}")
        else:
            print(" - None")

        print("\nWarnings:")
        if result["warnings"]:
            for warn in result["warnings"]:
                print(f" - {warn}")
        else:
            print(" - None")

        print_dict("CLEANED DATA", result["cleaned_data"])

        if result["is_valid"]:
            valid_count += 1
        else:
            invalid_count += 1

    print_section("PIPELINE TEST SUMMARY")
    print(f"Rows tested : {min(len(rows), max_rows)}")
    print(f"Valid rows  : {valid_count}")
    print(f"Invalid rows: {invalid_count}")
    print("Pipeline test finished successfully.")


if __name__ == "__main__":
    run_pipeline_test(max_rows=5)