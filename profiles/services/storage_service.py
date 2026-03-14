import os
from datetime import datetime


def build_pdf_path(profile, tier="premium"):
    safe_name = (profile.get("full_name") or "PROFILE").replace(" ", "_").upper()
    tier_tag = tier.upper()
    filename = f"{safe_name}_{tier_tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return os.path.join("media", "generated_pdfs", filename)