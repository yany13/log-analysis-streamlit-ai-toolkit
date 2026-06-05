"""PDF report generation."""
from fpdf import FPDF


def clean_unicode(text):
    """Convert unicode characters to ASCII equivalents."""
    replacements = {
        '–': '-',
        '—': '-',
        '‘': "'",
        '’': "'",
        '“': '"',
        '”': '"',
        '•': '*',
        '…': '...'
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    return text.encode('latin-1', 'replace').decode('latin-1')


def create_pdf_report(rca_text, query):
    """
    Generate PDF report for RCA analysis.

    Args:
        rca_text: Root cause analysis text
        query: Original incident query

    Returns:
        PDF bytes
    """
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, clean_unicode("Expert Root Cause Analysis"), ln=True, align='C')

    # Query
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, clean_unicode(f"Incident Query: {query}"))

    # Body
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    body_text = str(rca_text).replace("**", "").replace("__", "").replace("###", "")
    pdf.multi_cell(0, 10, clean_unicode(body_text))

    return bytes(pdf.output(dest='S'))
