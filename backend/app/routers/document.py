import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from app.constants import (
    DOCUMENT_INDEX_PATH,
    EMBEDDINGS_INDEX_PATH,
    DocumentEntry,
    DocumentIndex,
)
from app.services.documentService import process_document


router = APIRouter(prefix="/document", tags=["Document"])


@router.post("/upload")
async def upload_document(file: UploadFile):
    # Generate unique document ID
    document_id = str(uuid.uuid4())

    # Save file to uploads
    file_path = f"./uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    if DOCUMENT_INDEX_PATH.exists():
        with open(DOCUMENT_INDEX_PATH) as f:
            document_index = DocumentIndex.model_validate_json(f.read())
    else:
        document_index = DocumentIndex(root={})

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
        type=file.content_type,
    )

    # Add to index
    document_index.root[document_id] = document_entry

    # Save updated index
    with open(DOCUMENT_INDEX_PATH, "w") as f:
        f.write(document_index.model_dump_json(indent=2))

    return {
        "document_id": document_id,
        "filename": file.filename,
        "status": "uploaded",
    }


@router.get("/embed/{document_id}")
async def embed_document(document_id: str):
    return StreamingResponse(
        process_document(document_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/embedded-docs")
async def get_embedded_documents():
    # Read files from uploads/document.json
    if not DOCUMENT_INDEX_PATH.exists():
        return {}

    with open(DOCUMENT_INDEX_PATH) as f:
        document_index = json.load(f)

    # Output filenames and file-ids
    return json.dumps(document_index)


@router.delete("/delete/{document_id}")
async def delete_document(document_id: str):
    with open(DOCUMENT_INDEX_PATH) as f:
        document_index = json.load(f)

    if document_id not in document_index:
        return {"deleted"}

    filename = document_index[document_id]["filename"]
    Path(f"./uploads/{filename}").unlink(missing_ok=True)
    Path(f"./uploads/chunks/{document_id}_chunks.json").unlink(missing_ok=True)
    Path(f"./uploads/parsed/{document_id}_parsed.json").unlink(missing_ok=True)

    with open(EMBEDDINGS_INDEX_PATH) as f:
        embeddings_index: list = json.load(f)

    new_embeddings_index = [
        index
        for index in embeddings_index
        if (index["metadata"]["document_id"] != document_id)
    ]

    with open(EMBEDDINGS_INDEX_PATH, "w") as f:
        json.dump(new_embeddings_index, f, indent=2)

    del document_index[document_id]

    with open(DOCUMENT_INDEX_PATH, "w") as f:
        json.dump(document_index, f, indent=2)

    return {"status": "ok"}
