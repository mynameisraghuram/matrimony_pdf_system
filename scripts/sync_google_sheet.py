import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from profiles.models import Profile
from profiles.services.sheet_reader import get_sheet_records
from profiles.services.mapper import COLUMN_MAP
from profiles.services.normalizer import normalize_record
from profiles.services.validator import validate_record


def map_record(raw_row):
    mapped = {}
    for sheet_col, internal_key in COLUMN_MAP.items():
        mapped[internal_key] = raw_row.get(sheet_col, "")
    return mapped


def generate_profile_id(index):
    return f"PRF{index:04d}"


def run():
    rows = get_sheet_records()

    for idx, raw_row in enumerate(rows, start=1):
        mapped = map_record(raw_row)
        normalized = normalize_record(mapped)
        normalized["profile_id"] = generate_profile_id(idx)

        result = validate_record(normalized)
        if not result["is_valid"]:
            print(f"Skipping {normalized['profile_id']} بسبب errors: {result['errors']}")
            continue

        Profile.objects.update_or_create(
            profile_id=normalized["profile_id"],
            defaults=normalized
        )

    print("Sheet sync completed.")


if __name__ == "__main__":
    run()