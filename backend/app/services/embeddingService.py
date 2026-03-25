import asyncio
import json
from collections.abc import AsyncGenerator
from pathlib import Path

import numpy as np

from app.clients import get_embedding_client
from app.constants import (
    DOCUMENT_INDEX_PATH,
    EMBEDDINGS_INDEX_PATH,
    DocumentIndex,
    EmbeddingsEntry,
    EmbeddingsIndex,
)


class EmbeddingService:
    """Service for generating embeddings from text chunks."""

    def __init__(self):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the embedding model to use
        """
        self.embedding_client = get_embedding_client()

    async def embed_text(self, text: str) -> list[float] | None:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = await self.embedding_client.get_embeddings([text])
            return embedding[0].vector
        except Exception as e:
            print(f"Warning unable to Embed Text: {text}")
            print(f"Exception: {e}")
            return None

    async def embed_texts_parallel(
        self, texts: list[str], batch_size: int = 10
    ) -> list[list[float] | None]:
        """
        Generate embeddings for multiple texts in parallel batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in parallel

        Returns:
            List of embedding vectors
        """
        embeddings = []

        # Process texts in batches to avoid overwhelming the API
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Create embedding tasks for the batch
            tasks = [self.embed_text(text) for text in batch]

            # Execute all tasks in parallel
            batch_embeddings = await asyncio.gather(*tasks)
            embeddings.extend(batch_embeddings)

        return embeddings

    def get_similarity_score(
        self, embedding1: list[float], embedding2: list[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between -1 and 1 (1 means identical, 0 means orthogonal, -1 means opposite)
        """
        # Convert to numpy arrays for efficient computation
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)


embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    """
    Factory function to get an embedding service instance.

    Returns:
        EmbeddingService instance
    """
    return embedding_service


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
            yield f"data: {json.dumps({'status': 'error', 'message': 'Document index not found'})}\n\n"
            return

        with open(DOCUMENT_INDEX_PATH) as f:
            document_index = DocumentIndex.model_validate_json(f.read())

        if document_id not in document_index.root:
            yield f"data: {json.dumps({'status': 'error', 'message': 'Document not found'})}\n\n"
            return

        chunks_path = document_index.root[document_id].chunks_path

        if not chunks_path or not Path(chunks_path).exists():
            yield f"data: {json.dumps({'status': 'error', 'message': 'Chunks file not found. Please process the document first.'})}\n\n"
            return

        # Update status to embedding
        document_index.root[document_id].status = "embedding"
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))

        # Load chunks
        with open(chunks_path) as f:
            chunks_data: list[dict] = json.load(f)

        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks_data]

        yield f"data: {json.dumps({'status': 'embedding', 'message': f'Generating embeddings for {len(chunks_data)} chunks'})}\n\n"

        # Generate embeddings in parallel
        embedding_service = get_embedding_service()
        embeddings = await embedding_service.embed_texts_parallel(texts, batch_size=10)

        yield f"data: {json.dumps({'status': 'embedded', 'message': f'Generated {len(embeddings)} embeddings'})}\n\n"

        # Add embeddings to chunks data
        if EMBEDDINGS_INDEX_PATH.exists():
            with open(EMBEDDINGS_INDEX_PATH) as f:
                embeddings_index = EmbeddingsIndex.model_validate_json(f.read())
        else:
            embeddings_index = EmbeddingsIndex(root=[])

        for chunk, embedding in zip(chunks_data, embeddings, strict=True):
            if embedding is None:
                continue
            embeddings_entry = EmbeddingsEntry(
                chunk_id=chunk["chunk_id"],
                chunk=chunk["text"],
                metadata=chunk["metadata"],
                embedding=embedding,
            )
            embeddings_index.root.append(embeddings_entry)
        with open(EMBEDDINGS_INDEX_PATH, "w") as f:
            f.write(embeddings_index.model_dump_json(indent=2))

        # Update document entry
        document_index.root[document_id].status = "completed"
        document_index.root[document_id].embedded_chunks = len(chunks_data)

        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))

    except Exception as e:
        document_index.root[document_id].status = "failed"
        document_index.root[document_id].error = f"Embedding error: {e!s}\n"
        print(f"Embedding error: {e}")
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))

        yield f"data: {json.dumps({'status': 'error', 'message': f'Embedding failed: {e!s}'})}\n\n"
