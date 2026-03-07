from profiles.services.story_generator import generate_story
from profiles.services.template_renderer import render_profile_html
from profiles.services.pdf_generator import generate_pdf_from_html
from profiles.services.storage_service import build_pdf_path


def generate_profile_pdf(profile):
    profile.story_summary = generate_story(profile.__dict__)
    profile.save()

    html = render_profile_html(profile)
    pdf_path = build_pdf_path(profile.__dict__)
    generate_pdf_from_html(html, pdf_path)

    return pdf_path