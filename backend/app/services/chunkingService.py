import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel

from app.constants import DOCUMENT_INDEX_PATH, DocumentIndex


class Metadata(BaseModel):
    document_name: str
    document_path: str
    document_id: str
    element_type: str | None = None
    page_number: int | None = None


@dataclass
class Chunk:
    """Represents a chunk of text from a document."""

    chunk_id: str
    text: str
    chunk_index: int
    metadata: dict


class ChunkingStrategy:
    """Base class for chunking strategies."""

    def chunk(
        self, content: str | list[dict[str, Any]], metadata: Metadata = None
    ) -> list[Chunk]:
        raise NotImplementedError


class FixedSizeChunking(ChunkingStrategy):
    """Chunks text into fixed-size pieces with optional overlap."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self, content: str | list[dict[str, Any]], metadata: Metadata = None
    ) -> list[Chunk]:
        if isinstance(content, list):
            # If list, join texts
            text = " ".join([elem.get("text", "") for elem in content])
        else:
            text = content

        if metadata is None:
            metadata = {}

        chunks = []
        chunk_index = 0
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    metadata=metadata.model_dump(),
                )
            )

            chunk_index += 1
            start = end - self.overlap

        return chunks


class SentenceChunking(ChunkingStrategy):
    """Chunks text by sentences, grouping them up to a target size."""

    def __init__(self, target_size: int = 1000, min_size: int = 100):
        self.target_size = target_size
        self.min_size = min_size

    def chunk(
        self, content: str | list[dict[str, Any]], metadata: Metadata = None
    ) -> list[Chunk]:
        if isinstance(content, list):
            # If list, join texts
            text = " ".join([elem.get("text", "") for elem in content])
        else:
            text = content

        if metadata is None:
            metadata = {}

        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = self._split_sentences(text)

        chunks = []
        chunk_index = 0
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            if (
                current_size + sentence_len > self.target_size
                and current_size >= self.min_size
            ):
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk)
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                        metadata=metadata,
                    )
                )

                chunk_index += 1
                current_chunk = [sentence]
                current_size = sentence_len
            else:
                current_chunk.append(sentence)
                current_size += sentence_len

        # Add remaining sentences as final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    metadata=metadata,
                )
            )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Simple sentence splitter. Can be enhanced with spaCy or NLTK."""

        # Split on periods, exclamation marks, and question marks followed by space
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


class ParagraphChunking(ChunkingStrategy):
    """Chunks text by paragraphs, combining small ones."""

    def __init__(self, target_size: int = 1000):
        self.target_size = target_size

    def chunk(
        self, content: str | list[dict[str, Any]], metadata: Metadata = None
    ) -> list[Chunk]:
        if isinstance(content, list):
            # If list, join texts
            text = " ".join([elem.get("text", "") for elem in content])
        else:
            text = content

        if metadata is None:
            metadata = {}

        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        chunk_index = 0
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_len = len(para)

            if current_size + para_len > self.target_size and current_chunk:
                # Create chunk from accumulated paragraphs
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                        metadata=metadata,
                    )
                )

                chunk_index += 1
                current_chunk = [para]
                current_size = para_len
            else:
                current_chunk.append(para)
                current_size += para_len + 2  # Account for \n\n

        # Add remaining paragraphs as final chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    metadata=metadata,
                )
            )

        return chunks

    def _create_chunk(
        self,
        elements: list[dict[str, Any]],
        chunk_index: int,
        base_metadata: Metadata,
        title: str | None = None,
    ) -> Chunk:
        """Create a chunk from a list of elements."""
        # Combine element texts
        texts = [elem.get("text", "") for elem in elements]
        chunk_text = "\n\n".join(texts)

        # Extract metadata from first element
        first_elem_meta = elements[0].get("metadata", {})
        page_number = first_elem_meta.get("page_number")
        element_types = [elem.get("type", "Text") for elem in elements]

        # Create enriched metadata
        chunk_metadata = Metadata(
            document_name=base_metadata.document_name,
            document_path=base_metadata.document_path,
            element_type=", ".join(set(element_types)),
            page_number=page_number,
        )

        # Prepend title if available
        if title and not chunk_text.startswith(title):
            chunk_text = f"{title}\n\n{chunk_text}"

        return Chunk(
            text=chunk_text,
            chunk_index=chunk_index,
            metadata=chunk_metadata,
        )


class StructureAwareChunking(ChunkingStrategy):
    """Chunks based on document structure: groups Titles with following NarrativeTexts."""

    def chunk(
        self, content: str | list[dict[str, Any]], metadata: Metadata = None
    ) -> list[Chunk]:
        if not isinstance(content, list):
            raise ValueError(
                "StructureAwareChunking requires a list of structured elements"
            )

        if metadata is None:
            metadata = Metadata(document_name="", document_path="")

        chunks: list[Chunk] = []
        chunk_index = 0
        current_elements = []
        current_title = None
        in_narrative_section = False

        for elem in content:
            elem_type = elem.get("type", "")
            elem_text = elem.get("text", "").strip()

            if elem_type == "Title":
                # If we were collecting narratives, end the chunk
                if in_narrative_section and current_elements:
                    chunk = self._create_chunk(
                        current_elements, chunk_index, metadata, current_title
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_elements = []
                    current_title = None

                # Add this title to current elements (combine titles)
                current_elements.append(elem)
                if current_title is None:
                    current_title = elem_text
                in_narrative_section = False

            elif elem_type == "NarrativeText":
                # If we just had titles, now switch to narrative section
                if not in_narrative_section:
                    in_narrative_section = True

                # Add this narrative text to current elements (combine narratives)
                current_elements.append(elem)

            # For other types, append to current chunk if one exists
            elif current_elements:
                current_elements.append(elem)

        # Add the last chunk if any elements remain
        if current_elements:
            chunk = self._create_chunk(
                current_elements, chunk_index, metadata, current_title
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        elements: list[dict[str, Any]],
        chunk_index: int,
        base_metadata: Metadata,
        title: str | None = None,
    ) -> Chunk:
        """Create a chunk from a list of elements."""
        # Combine element texts
        texts = [elem.get("text", "") for elem in elements]
        chunk_text = "\n\n".join(texts)

        # Extract metadata from first element
        first_elem_meta = elements[0].get("metadata", {})
        page_number = first_elem_meta.get("page_number")
        element_types = [elem.get("type", "Text") for elem in elements]

        # Create enriched metadata
        chunk_metadata = Metadata(
            document_name=base_metadata.document_name,
            document_path=base_metadata.document_path,
            document_id=base_metadata.document_id,
            element_type=", ".join(set(element_types)),
            page_number=page_number,
        )

        # Prepend title if available
        if title and not chunk_text.startswith(title):
            chunk_text = f"{title}\n\n{chunk_text}"

        return Chunk(
            chunk_id=str(uuid4()),
            text=chunk_text,
            chunk_index=chunk_index,
            metadata=chunk_metadata.model_dump(),
        )


def get_chunking_strategy(strategy: str = "fixed", **kwargs) -> ChunkingStrategy:
    """Factory function to get a chunking strategy."""
    strategies = {
        "fixed": FixedSizeChunking,
        "sentence": SentenceChunking,
        "paragraph": ParagraphChunking,
        "structure": StructureAwareChunking,
    }

    if strategy not in strategies:
        raise ValueError(
            f"Unknown chunking strategy: {strategy}. Available: {list(strategies.keys())}"
        )

    return strategies[strategy](**kwargs)


async def chunk_parsed_document(document_id: str, strategy: str = "structure"):
    try:
        yield f"data: {json.dumps({'status': 'chunking', 'message': 'Creating chunks...'})}\n\n"

        with open(DOCUMENT_INDEX_PATH) as f:
            document_index = DocumentIndex.model_validate_json(f.read())
        chunking_strategy = get_chunking_strategy(strategy=strategy)

        with open(f"./uploads/parsed/{document_id}_parsed.json") as f:
            parsed_content = json.load(f)

        chunk_metadata = Metadata(
            document_name=document_index.root[document_id].filename,
            document_path=document_index.root[document_id].file_path,
            document_id=document_id,
        )
        chunks = chunking_strategy.chunk(parsed_content, chunk_metadata)

        chunks_path = Path(f"uploads/chunks/{document_id}_chunks.json")

        with open(chunks_path, "w") as f:
            json.dump(
                [
                    {
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "metadata": chunk.metadata,
                    }
                    for chunk in chunks
                ],
                f,
                indent=2,
            )

        document_index.root[document_id].total_chunks = len(chunks)
        document_index.root[document_id].chunks_path = str(chunks_path)
        document_index.root[document_id].embedded_chunks = 0
        document_index.root[document_id].status = "chunked"

        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))
        yield f"data: {json.dumps({'status': 'chunked', 'message': f'Document chunked into {len(chunks)} chunks'})}\n\n"

    except Exception as e:
        document_index.root[document_id].error = f"Chunking error: {e!s}"
        with open(DOCUMENT_INDEX_PATH, "w") as f:
            f.write(document_index.model_dump_json(indent=2))
        yield f"data: {json.dumps({'status': 'error', 'message': f'Chunking failed: {e!s}'})}\n\n"
        return
