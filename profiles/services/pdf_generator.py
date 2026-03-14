import os

from django.conf import settings
from xhtml2pdf import pisa


def _link_callback(uri, rel):
    """Resolve file:/// URIs and relative paths to absolute filesystem paths."""
    if uri.startswith("file:///"):
        path = uri[8:]  # strip file:///
        return path
    # Fall back: treat as relative to project root
    path = os.path.join(str(settings.BASE_DIR), uri.replace("/", os.sep))
    if os.path.isfile(path):
        return path
    return uri


def generate_pdf_from_html(html_string, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        status = pisa.CreatePDF(html_string, dest=f, link_callback=_link_callback)
    if status.err:
        raise RuntimeError(f"xhtml2pdf failed with {status.err} error(s)")
    return output_path
