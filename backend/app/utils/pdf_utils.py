from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file and returns it as a string.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF: {str(e)}")
