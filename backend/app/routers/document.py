import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from app.services.documentService import DocumentEntry, process_document


router = APIRouter(prefix="/document", tags=["Document"])

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
        type=file.content_type,
    )

    # Add to index
    document_index[document_id] = document_entry.model_dump()

    # Save updated index
    with open(DOCUMENT_INDEX_PATH, "w") as f:
        json.dump(document_index, f, indent=2)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "status": "uploaded",
    }


@router.get("/embed/{document_id}")
async def embed_document(document_id: str):
    return StreamingResponse(
        process_document(document_id), media_type="text/event-stream"
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

    with open("./uploads/embeddings.json") as f:
        embeddings_index: list = json.load(f)

    new_embeddings_index = [
        index
        for index in embeddings_index
        if (index["metadata"]["document_id"] != document_id)
    ]

    with open("./uploads/embeddings.json", "w") as f:
        json.dump(new_embeddings_index, f, indent=2)

    del document_index[document_id]

    with open(DOCUMENT_INDEX_PATH, "w") as f:
        json.dump(document_index, f, indent=2)

    return {"ok"}
