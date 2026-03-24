from pathlib import Path

from pydantic import BaseModel, RootModel


Path("./uploads/chunks").mkdir(exist_ok=True, parents=True)
Path("./uploads/parsed").mkdir(exist_ok=True, parents=True)

DOCUMENT_INDEX_PATH = Path("uploads/document.json")
EMBEDDINGS_INDEX_PATH = Path("uploads/embeddings.json")


def chunks_path(document_id):
    return Path(f"uploads/chunks/{document_id}_chunks.json")


def embeddings_path(document_id):
    return Path(f"uploads/parsed/{document_id}_parsed.json")


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
