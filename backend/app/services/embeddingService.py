import asyncio

import numpy as np


class EmbeddingService:
    """Service for generating embeddings from text chunks."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        # TODO: Initialize actual embedding model (OpenAI, Sentence Transformers, etc.)

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector
        """
        # TODO: Replace with actual embedding model
        # For now, return a dummy embedding
        await asyncio.sleep(0.1)  # Simulate API call
        return np.random.rand(1536).tolist()

    async def embed_texts_parallel(
        self, texts: list[str], batch_size: int = 10
    ) -> list[list[float]]:
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


def get_embedding_service(
    model_name: str = "text-embedding-3-small",
) -> EmbeddingService:
    """
    Factory function to get an embedding service instance.

    Args:
        model_name: Name of the embedding model to use

    Returns:
        EmbeddingService instance
    """
    return EmbeddingService(model_name=model_name)
