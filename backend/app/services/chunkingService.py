import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


class Metadata(BaseModel):
    document_name: str
    document_path: str
    element_type: str | None = None
    page_number: int | None = None


@dataclass
class Chunk:
    """Represents a chunk of text from a document."""

    text: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Metadata


class ChunkingStrategy:
    """Base class for chunking strategies."""

    def chunk(self, text: str, metadata: Metadata = None) -> list[Chunk]:
        raise NotImplementedError


class FixedSizeChunking(ChunkingStrategy):
    """Chunks text into fixed-size pieces with optional overlap."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: Metadata = None) -> list[Chunk]:
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
                    start_char=start,
                    end_char=end,
                    metadata=metadata,
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

    def chunk(self, text: str, metadata: Metadata = None) -> list[Chunk]:
        if metadata is None:
            metadata = {}

        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = self._split_sentences(text)

        chunks = []
        chunk_index = 0
        current_chunk = []
        current_size = 0
        start_char = 0

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
                        start_char=start_char,
                        end_char=start_char + len(chunk_text),
                        metadata=metadata,
                    )
                )

                chunk_index += 1
                start_char += len(chunk_text) + 1
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
                    start_char=start_char,
                    end_char=start_char + len(chunk_text),
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

    def chunk(self, text: str, metadata: Metadata = None) -> list[Chunk]:
        if metadata is None:
            metadata = {}

        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        chunk_index = 0
        current_chunk = []
        current_size = 0
        start_char = 0

        for para in paragraphs:
            para_len = len(para)

            if current_size + para_len > self.target_size and current_chunk:
                # Create chunk from accumulated paragraphs
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                        start_char=start_char,
                        end_char=start_char + len(chunk_text),
                        metadata=metadata,
                    )
                )

                chunk_index += 1
                start_char += len(chunk_text) + 2
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
                    start_char=start_char,
                    end_char=start_char + len(chunk_text),
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
            start_char=0,  # Not applicable for structure-aware chunking
            end_char=len(chunk_text),
            metadata=chunk_metadata,
        )


def get_chunking_strategy(strategy: str = "fixed", **kwargs) -> ChunkingStrategy:
    """Factory function to get a chunking strategy."""
    strategies = {
        "fixed": FixedSizeChunking,
        "sentence": SentenceChunking,
        "paragraph": ParagraphChunking,
    }

    if strategy not in strategies:
        raise ValueError(
            f"Unknown chunking strategy: {strategy}. Available: {list(strategies.keys())}"
        )

    return strategies[strategy](**kwargs)
