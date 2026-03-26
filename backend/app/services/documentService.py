import json
from collections.abc import AsyncGenerator

from app.constants import (
    DOCUMENT_INDEX_PATH,
    DocumentIndex,
)
from app.services.chunkingService import (
    chunk_parsed_document,
)
from app.services.embeddingService import embed_document
from app.services.parsingService import parse_doc


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
        with open(DOCUMENT_INDEX_PATH) as f:
            document_index = DocumentIndex.model_validate_json(f.read())

        if document_id not in document_index.root:
            yield f"data: {json.dumps({'status': 'error', 'message': 'Document not found'})}\n\n"
            return

        if document_index.root[document_id].status == "completed":
            yield f"data: {json.dumps({'status': 'completed', 'message': 'Document already Embedded'})}\n\n"
            return

        document_index.root[document_id].status = "parsing"
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))

        # Parse the document with unstructured library for structure awareness
        async for progress_1 in parse_doc(document_id):
            yield progress_1

        # Chunk the parsed content
        async for progress_2 in chunk_parsed_document(document_id):
            yield progress_2

        # Embed the chunks
        async for progress_3 in embed_document(document_id):
            yield progress_3

        yield f"data: {json.dumps({'status': 'completed', 'message': 'Document processing complete'})}\n\n"
    except Exception as e:
        with open(DOCUMENT_INDEX_PATH) as f:
            document_index = DocumentIndex.model_validate_json(f.read())
        document_index.root[document_id].status = "failed"
        document_index.root[document_id].error = f"Parsing error: {e!s}"
        print(f"Parsing error: {e}")
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))
        yield f"data: {json.dumps({'status': 'error', 'message': f'Parsing failed: {e!s}'})}\n\n"
