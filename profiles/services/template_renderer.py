import os
import re
from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string


TEMPLATES = {
    "standard": "pdf/profile_standard.html",
    "premium": "pdf/profile_premium.html",
}


def _calculate_age_display(dob_str):
    """Convert DOB string to 'Month - YYYY' format for standard tier."""
    if not dob_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            dt = datetime.strptime(dob_str.strip(), fmt)
            return f"{dt.strftime('%B')} - {dt.year}"
        except ValueError:
            continue
    return dob_str


def _mask_contact(contact_str):
    """Mask a phone number: show first 2 and last 4 digits, e.g. 98XXXX4321."""
    if not contact_str:
        return None
    digits = re.sub(r"[^\d]", "", contact_str)
    if len(digits) <= 6:
        return "XXXX"
    return digits[:2] + "X" * (len(digits) - 6) + digits[-4:]


def _get_highest_education(profile):
    """Return highest education: masters > graduation > schooling."""
    for field in ("masters", "graduation", "schooling"):
        val = getattr(profile, field, None)
        if val:
            return val
    return None


def _get_ancestral_origin(profile):
    """Return ancestral origin from father_native."""
    return getattr(profile, "father_native", None)


def render_profile_html(profile, tier="premium"):
    logo_path = os.path.join(settings.BASE_DIR, "static", "logos", "logo.png")
    logo_uri = "file:///" + logo_path.replace("\\", "/")

    template_name = TEMPLATES.get(tier, TEMPLATES["premium"])

    context = {
        "profile": profile,
        "tier": tier,
        "tier_label": "Standard Profile" if tier == "standard" else "Premium Profile",
        "company_name": os.environ.get("COMPANY_NAME", "Matrimony Services"),
        "company_contact": os.environ.get("COMPANY_CONTACT", "Contact us for more details"),
        "company_tagline": os.environ.get("COMPANY_TAGLINE", ""),
        "logo_uri": logo_uri,
        "whatsapp_url": "https://wa.me/9368111222",
    }

    if tier == "standard":
        context["age_display"] = _calculate_age_display(
            getattr(profile, "date_of_birth", None)
        )
        context["masked_contact"] = _mask_contact(
            getattr(profile, "contact_number", None)
        )
        context["highest_education"] = _get_highest_education(profile)
        context["ancestral_origin"] = _get_ancestral_origin(profile)

    return render_to_string(template_name, context)
