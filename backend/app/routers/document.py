import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from app.services.documentService import DocumentEntry, process_document


router = APIRouter(prefix="/document")

DOCUMENT_INDEX_PATH = Path("uploads/document.json")


@router.post("/upload")
async def upload_document(file: UploadFile):
    # Generate unique document ID
    document_id = str(uuid.uuid4())

    # Save file to uploads
    file_path = f"./uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Load existing document index
    if DOCUMENT_INDEX_PATH.exists():
        with open(DOCUMENT_INDEX_PATH) as f:
            document_index = json.load(f)
    else:
        document_index = {}

    # Create document status entry
    document_entry = DocumentEntry(
        document_id=document_id,
        filename=file.filename,
        file_path=file_path,
        status="uploaded",
        uploaded_at=datetime.now(UTC).isoformat(),
        total_chunks=0,
        embedded_chunks=0,
        size=file.size,
    )

    # Add to index
    document_index[document_id] = document_entry.model_dump()

    # Save updated index
    with open(DOCUMENT_INDEX_PATH, "w") as f:
        json.dump(document_index, f, indent=2)

    # TODO: process/parse the document
    # TODO: chunk the document
    # TODO: embed each chunk
    # TODO: store the embeddings and chunks
    # TODO: update document_entry with total_chunks and embedded_chunks
    # TODO: update status to "completed" or "failed"

    return {
        "document_id": document_id,
        "filename": file.filename,
        "status": "uploaded",
    }


@router.get("/embed/{document_id}")
async def embed_document(document_id: str):
    return StreamingResponse(process_document(document_id))


@router.get("/embedded-docs")
async def get_embedded_documents():
    # Read files from uploads/document.json
    if not DOCUMENT_INDEX_PATH.exists():
        return {}

    with open(DOCUMENT_INDEX_PATH) as f:
        document_index = json.load(f)

    # Output filenames and file-ids
    return json.dumps(document_index)
