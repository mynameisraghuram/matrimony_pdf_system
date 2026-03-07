import os
from weasyprint import HTML


def generate_pdf_from_html(html_string, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    HTML(string=html_string).write_pdf(output_path)
    return output_path