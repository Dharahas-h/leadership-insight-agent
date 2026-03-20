from pathlib import Path

import PyPDF2
from docx import Document


def parse_document(file_path: str) -> str:
    """
    Parse a document and extract its text content.

    Args:
        file_path: Path to the document file

    Returns:
        Extracted text content
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension
    extension = file_path_obj.suffix.lower()

    # Parse based on file type
    if extension == ".txt":
        return _parse_text(file_path)
    if extension == ".pdf":
        return _parse_pdf(file_path)
    if extension in [".doc", ".docx"]:
        return _parse_docx(file_path)
    # Try reading as plain text
    return _parse_text(file_path)


def _parse_text(file_path: str) -> str:
    """Parse a plain text file."""
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def _parse_pdf(file_path: str) -> str:
    """
    Parse a PDF file.
    Note: Requires PyPDF2 or pdfplumber library.
    """
    try:
        text = []
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return "\n\n".join(text)
    except ImportError:
        raise ImportError from ImportError(
            "PyPDF2 is required for PDF parsing. Install it with: pip install PyPDF2"
        )


def _parse_docx(file_path: str) -> str:
    """
    Parse a DOCX file.
    Note: Requires python-docx library.
    """
    try:
        doc = Document(file_path)
        return "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
    except ImportError:
        raise ImportError from ImportError(
            "python-docx is required for DOCX parsing. Install it with: pip install python-docx"
        )
