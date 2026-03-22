import json
from pathlib import Path
from typing import Any

# from docx import Document
from unstructured.partition.pdf import partition_pdf

from app.routers.document import DOCUMENT_INDEX_PATH
from app.services.documentService import DocumentIndex


async def parse_doc(document_id: str):
    with open(DOCUMENT_INDEX_PATH) as f:
        document_index = DocumentIndex.model_validate_json(f.read())

    document_entry = document_index.root[document_id]
    parsed_content = parse_document(Path(document_entry.file_path))

    parsed_content_path = Path(f"./uploads/parsed/{document_id}_parsed")

    if not parsed_content_path.exists():
        raise FileNotFoundError(f"File not found: {parsed_content_path}")

    extension = parsed_content_path.suffix.lower()

    if extension == ".pdf":
        yield f"data: {json.dumps({'status': 'parsing', 'message': 'parsing pdf...'})}"
        parsed_content = _parse_pdf(document_entry.file_path)
        yield f"data: {json.dumps({'status': 'parsed', 'message': f'extracted {len(parsed_content)} objects from pdf'})}"
    else:
        parsed_content = _parse_text(document_entry.file_path)

    with open(parsed_content_path, "w") as f:
        if isinstance(parsed_content, str):
            json.dump({"text": parsed_content}, f, indent=2)
        else:
            json.dump(parsed_content, f, indent=2)


def parse_document(file_path: Path) -> str | list[dict[str, Any]]:
    """
    Parse a document and extract its text content.

    Args:
        file_path: Path to the document file

    Returns:
        For PDFs: list of structured elements if unstructured is available
        For other files: extracted text content as string
    """

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get file extension
    extension = file_path.suffix.lower()

    # Parse based on file type
    if extension == ".pdf":
        return _parse_pdf(file_path)
    if extension == ".txt":
        return _parse_text(file_path)
    # if extension in [".doc", ".docx"]:
    #     return _parse_docx(file_path)
    # Try reading as plain text
    return _parse_text(file_path)


def _parse_text(file_path: str) -> str:
    """Parse a plain text file."""
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def _parse_pdf(file_path: str) -> list[dict[str, Any]]:
    """
    Parse a PDF file using unstructured library for structure awareness.
    """
    elements = partition_pdf(file_path, languages=["eng"])
    # Convert to dict format
    structured_elements = []
    for elem in elements:
        structured_elements.append(
            {
                "index": len(structured_elements),
                "type": elem.__class__.__name__,  # e.g., Title, NarrativeText
                "text": str(elem),
                "metadata": {
                    "page_number": getattr(
                        getattr(elem, "metadata", {}), "page_number", None
                    ),
                    "coordinates": getattr(
                        getattr(elem, "metadata", {}), "coordinates", {}
                    ),
                    "file_directory": str(Path(file_path).parent),
                    "filename": Path(file_path).name,
                    "languages": getattr(
                        getattr(elem, "metadata", {}), "languages", []
                    ),
                    "last_modified": getattr(
                        getattr(elem, "metadata", {}), "last_modified", None
                    ),
                    "filetype": "application/pdf",
                },
            }
        )
    return structured_elements


# def _parse_docx(file_path: str) -> str:
#     """
#     Parse a DOCX file.
#     Note: Requires python-docx library.
#     """
#     try:
#         doc = Document(file_path)
#         return "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
#     except ImportError:
#         raise ImportError from ImportError(
#             "python-docx is required for DOCX parsing. Install it with: pip install python-docx"
#         )
