from pathlib import Path
from typing import Any

import PyPDF2
from docx import Document
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf


def parse_document(
    file_path: str, use_unstructured: bool = True
) -> str | list[dict[str, Any]]:
    """
    Parse a document and extract its text content.

    Args:
        file_path: Path to the document file
        use_unstructured: If True, use unstructured library for structure-aware parsing

    Returns:
        Extracted text content as string, or list of structured elements if use_unstructured=True
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension
    extension = file_path_obj.suffix.lower()

    # Use unstructured library for PDFs and DOCX for better structure preservation
    if use_unstructured and extension in [".pdf", ".docx"]:
        return _parse_with_unstructured(file_path)

    # Parse based on file type (legacy methods)
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


def _parse_with_unstructured(file_path: str) -> list[dict[str, Any]]:
    """
    Parse a document using unstructured library for structure-aware extraction.
    This method preserves document structure like titles, sections, tables, etc.
    Ideal for annual reports, quarterly reports, and structured documents.

    Args:
        file_path: Path to the document file

    Returns:
        List of structured elements with metadata
    """
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()

    # Use specialized PDF partitioner for better results
    if extension == ".pdf":
        try:
            # Try high-resolution strategy first (requires poppler/tesseract)
            elements = partition_pdf(
                filename=file_path,
                strategy="fasts",  # High resolution for better accuracy
                include_page_breaks=True,  # Preserve page structure
            )
        except Exception:
            # Fallback to fast strategy if system dependencies not available
            elements = partition_pdf(
                filename=file_path,
                strategy="fast",  # Uses PyPDF2, no extra dependencies needed
                include_page_breaks=True,
            )
    else:
        # Auto-detect for other formats
        elements = partition(filename=file_path)

    # Convert elements to structured format
    structured_elements = []
    for idx, element in enumerate(elements):
        structured_elements.append(
            {
                "element_id": idx,
                "type": element.category,
                "text": str(element),
                "metadata": element.metadata.to_dict()
                if hasattr(element.metadata, "to_dict")
                else {},
            }
        )

    return structured_elements
