from __future__ import annotations

from io import BytesIO
from typing import Optional, Tuple

from docx import Document
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Read text from a PDF file using pypdf."""

    reader = PdfReader(BytesIO(file_bytes))
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text.strip())

    return "\n\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Read text from a DOCX file using python-docx."""

    document = Document(BytesIO(file_bytes))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_upload(uploaded_file) -> Tuple[str, Optional[str]]:
    """
    Extract text from a Streamlit uploaded file.

    Returns:
        tuple: (text, error_message)
    """

    if uploaded_file is None:
        return "", "No file was uploaded."

    try:
        file_name = uploaded_file.name.lower()
        file_bytes = uploaded_file.getvalue()

        if file_name.endswith(".pdf"):
            return extract_text_from_pdf(file_bytes), None

        if file_name.endswith(".docx"):
            return extract_text_from_docx(file_bytes), None

        return "", "Unsupported file type. Please upload a PDF or DOCX resume."

    except Exception as exc:  # pragma: no cover - defensive error handling
        return "", f"Unable to read the uploaded file. Details: {exc}"
