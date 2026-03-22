import json
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

from app.services.chunkingService import Metadata, get_chunking_strategy
from app.services.embeddingService import get_embedding_service
from app.services.parsingService import parse_document


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


async def process_document(document_id: str) -> AsyncGenerator[str]:
    """
    Process a document: parse, chunk, and prepare for embedding.
    Yields progress updates as Server-Sent Events.

    Args:
        document_id: The unique identifier for the document

    Yields:
        Progress updates in JSON format
    """
    try:
        # Load document metadata
        if not DOCUMENT_INDEX_PATH.exists():
            yield f"data: {json.dumps({'error': 'Document index not found'})}\n\n"
            return

        with open(DOCUMENT_INDEX_PATH) as f:
            document_index: dict[str, dict] = json.load(f)

        if document_id not in document_index:
            yield f"data: {json.dumps({'error': 'Document not found'})}\n\n"
            return

        document_entry = document_index[document_id]
        status = document_entry["status"]

        if status == "embedded":
            yield f"data {json.dumps({'status': 'completed', 'message': 'Document already Embedded', 'total_chunks': document_entry['total_chunks']})}"
            return

        file_path = document_entry["file_path"]

        document_entry["status"] = "processing"
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            json.dump(document_index, f, indent=2)

        # Parse the document with unstructured library for structure awareness
        try:
            parsed_content = parse_document(file_path)
        except Exception as e:
            document_entry["status"] = "failed"
            document_entry["error"] = f"Parsing error: {e!s}"
            with open(DOCUMENT_INDEX_PATH, "w") as f:
                json.dump(document_index, f, indent=2)
            yield f"data: {json.dumps({'error': f'Parsing failed: {e!s}'})}\n\n"
            return

        # Chunk the document
        yield f"data: {json.dumps({'status': 'chunking', 'message': 'Creating chunks...'})}\n\n"

        try:
            # Create metadata for chunks
            chunk_metadata = Metadata(
                document_name=document_entry["filename"],
                document_path=file_path,
            )

            chunking_strategy = get_chunking_strategy(
                strategy="fixed", target_size=1000, min_size=100
            )
            chunks = chunking_strategy.chunk(parsed_content, metadata=chunk_metadata)

            document_entry["total_chunks"] = len(chunks)
            yield f"data: {json.dumps({'status': 'chunked', 'message': f'Created {len(chunks)} chunks'})}\n\n"

        except Exception as e:
            document_entry["status"] = "failed"
            document_entry["error"] = f"Chunking error: {e!s}"
            with open(DOCUMENT_INDEX_PATH, "w") as f:
                json.dump(document_index, f, indent=2)
            yield f"data: {json.dumps({'error': f'Chunking failed: {e!s}'})}\n\n"
            return

        # Save chunks to a file for later embedding
        chunks_path = Path(f"uploads/chunks/{document_id}_chunks.json")
        chunks_data = [
            {
                "chunk_id": str(uuid4()),
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "metadata": chunk.metadata,
            }
            for chunk in chunks
        ]

        with open(chunks_path, "w") as f:
            json.dump(chunks_data, f, indent=2)

        document_entry["chunks_path"] = str(chunks_path)

        # TODO: Embed each chunk
        # TODO: Store embeddings in vector database
        # For now, mark as ready for embedding
        document_entry["status"] = "chunked"
        document_entry["embedded_chunks"] = 0

        with open(DOCUMENT_INDEX_PATH, "w") as f:
            json.dump(document_index, f, indent=2)

        async for progress in embed_document(document_id):
            yield progress

        yield f"data: {json.dumps({'status': 'completed', 'message': 'Document processing complete', 'total_chunks': len(chunks)})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': f'Unexpected error: {e!s}'})}\n\n"


async def embed_document(document_id: str) -> AsyncGenerator[str]:
    """
    Embed all chunks of a document in parallel batches.
    Yields progress updates as Server-Sent Events.

    Args:
        document_id: The unique identifier for the document

    Yields:
        Progress updates in JSON format
    """
    try:
        # Load document metadata
        if not DOCUMENT_INDEX_PATH.exists():
            yield f"data: {json.dumps({'error': 'Document index not found'})}\n\n"
            return

        with open(DOCUMENT_INDEX_PATH) as f:
            document_index: dict[str, dict] = json.load(f)

        if document_id not in document_index:
            yield f"data: {json.dumps({'error': 'Document not found'})}\n\n"
            return

        document_entry = document_index[document_id]
        chunks_path = document_entry["chunks_path"]

        if not chunks_path or not Path(chunks_path).exists():
            yield f"data: {json.dumps({'error': 'Chunks file not found. Please process the document first.'})}\n\n"
            return

        # Update status to embedding
        document_entry["status"] = "embedding"
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            json.dump(document_index, f, indent=2)

        yield f"data: {json.dumps({'status': 'loading', 'message': 'Loading chunks...'})}\n\n"

        # Load chunks
        with open(chunks_path) as f:
            chunks_data = json.load(f)

        total_chunks = len(chunks_data)
        yield f"data: {json.dumps({'status': 'loaded', 'message': f'Loaded {total_chunks} chunks'})}\n\n"

        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks_data]

        yield f"data: {json.dumps({'status': 'embedding', 'message': 'Generating embeddings in parallel...'})}\n\n"

        # Generate embeddings in parallel
        embedding_service = get_embedding_service()
        embeddings = await embedding_service.embed_texts_parallel(texts, batch_size=10)

        yield f"data: {json.dumps({'status': 'embedded', 'message': f'Generated {len(embeddings)} embeddings'})}\n\n"

        # Add embeddings to chunks data
        with open("./uploads/embeddings.json") as embeddings_json:
            embeddings_index: list = json.load(embeddings_json)

        for chunk, embedding in zip(chunks_data, embeddings, strict=False):
            embeddings_index.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "chunk": chunk["text"],
                    "metadata": chunk["metadata"],
                    "embedding": embedding,
                }
            )
        with open("./uploads/embeddings.json", "w") as embeddings_json:
            json.dump(embeddings_index, embeddings_json, indent=2)

        # Save chunks with embeddings
        with open(chunks_path, "w") as f:
            json.dump(chunks_data, f, indent=2)

        # Update document entry
        document_entry["status"] = "embedded"
        document_entry["embedding_chunks"] = total_chunks

        with open(DOCUMENT_INDEX_PATH, "w") as f:
            json.dump(document_index, f, indent=2)

        yield f"data: {json.dumps({'status': 'completed', 'message': 'Embedding complete', 'total_chunks': total_chunks})}\n\n"

    except Exception as e:
        # Update document entry with error
        try:
            with open(DOCUMENT_INDEX_PATH) as f:
                document_index = json.load(f)
            document_index[document_id]["status"] = "failed"
            document_index[document_id]["error"] = f"Embedding error: {e!s}"
            with open(DOCUMENT_INDEX_PATH, "w") as f:
                json.dump(document_index, f, indent=2)
        except Exception:
            pass

        yield f"data: {json.dumps({'error': f'Embedding failed: {e!s}'})}\n\n"
