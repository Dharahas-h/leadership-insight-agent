import json
from typing import Annotated

from agent_framework import tool
from pydantic import Field

from app.services.embeddingService import get_embedding_service


@tool(description="Tool to get information over contextual context")
async def get_relevant_information(
    text: Annotated[
        str, Field(description="text the returned content should be similar to")
    ],
):
    embedding_service = get_embedding_service()
    embedding = await embedding_service.embed_text(text)

    similarity_array = []
    with open("./uploads/embeddings.json") as f:
        embeddings_index: list = json.load(f)

    for chunk in embeddings_index:
        similarity_array.append(
            {
                "score": embedding_service.get_similarity_score(
                    embedding, chunk["embedding"]
                ),
                "text": chunk["chunk"],
            }
        )

    similarity_array = sorted(similarity_array, key=lambda x: x["score"], reverse=True)

    return similarity_array[:5]
