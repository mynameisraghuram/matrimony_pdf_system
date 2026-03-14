import os

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from profiles.models import GeneratedPDF, Profile
from profiles.utils.helpers import generate_profile_pdf
from profiles.services.sync_service import sync_profiles_from_sheet


def profile_list(request):
    profiles = Profile.objects.all().order_by("-updated_at")
    return render(request, "profiles/profile_list.html", {"profiles": profiles})


def sync_sheet(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        result = sync_profiles_from_sheet()
        parts = []
        if result["created"]:
            parts.append(f"{result['created']} new")
        if result["updated"]:
            parts.append(f"{result['updated']} updated")
        if result["invalid"]:
            parts.append(f"{result['invalid']} invalid")
        if result["errors"]:
            parts.append(f"{result['errors']} errors")

        summary = ", ".join(parts) if parts else "no rows found"
        messages.success(request, f"Sync complete — {result['total']} rows fetched: {summary}.")
    except Exception as e:
        messages.error(request, f"Sync failed: {str(e)}")

    return redirect("profiles:profile_list")


def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    pdfs = profile.pdfs.all().order_by("-generated_at")
    return render(request, "profiles/profile_detail.html", {"profile": profile, "pdfs": pdfs})


def generate_pdf(request, pk, tier="premium"):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if tier not in ("standard", "premium"):
        tier = "premium"

    profile = get_object_or_404(Profile, pk=pk)
    tier_label = tier.capitalize()

    try:
        file_path = generate_profile_pdf(profile, tier=tier)
        version = profile.pdfs.filter(tier=tier).count() + 1
        GeneratedPDF.objects.create(
            profile=profile,
            file_path=file_path,
            version=version,
            tier=tier,
            template_used=tier,
        )
        messages.success(request, f"{tier_label} PDF generated successfully (v{version}).")
    except Exception as e:
        messages.error(request, f"{tier_label} PDF generation failed: {str(e)}")

    return redirect("profiles:profile_detail", pk=pk)


def download_pdf(request, pk, pdf_id):
    pdf = get_object_or_404(GeneratedPDF, id=pdf_id, profile__pk=pk)
    abs_path = os.path.join(settings.BASE_DIR, pdf.file_path)

    if not os.path.exists(abs_path):
        raise Http404("PDF file not found on disk.")

    return FileResponse(
        open(abs_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(abs_path),
    )
