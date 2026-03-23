from pathlib import Path
from pydantic import BaseModel, RootModel

DOCUMENT_INDEX_PATH = Path("uploads/document.json")

class DocumentEntry(BaseModel):
    document_id: str
    filename: str
    file_path: str
    status: str
    uploaded_at: str
    total_chunks: int
    embedded_chunks: int
    error: str | None = None
    size: int
    chunks_path: str | None = None
    type: str | None = None


class EmbeddingsEntry(BaseModel):
    chunk_id: str
    chunk: str
    metadata: dict
    embedding: list[float]


DocumentIndex = RootModel[dict[str, DocumentEntry]]

EmbeddingsIndex = RootModel[list[EmbeddingsEntry]]