import requests
import io
from PyPDF2 import PdfReader

def extract_pdf_text(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        return text[:5000]

    except Exception:
        return None