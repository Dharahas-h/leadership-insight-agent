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
