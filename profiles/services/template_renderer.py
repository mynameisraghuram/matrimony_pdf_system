from django.template.loader import render_to_string


def render_profile_html(profile):
    return render_to_string("pdf/profile_template.html", {"profile": profile})