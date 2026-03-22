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


class StructureAwareChunking(ChunkingStrategy):
    """
    Structure-aware chunking for documents parsed with unstructured library.
    Groups elements by semantic structure (sections, subsections, etc.) while respecting size limits.
    Ideal for annual reports, quarterly reports, and structured business documents.
    """

    def __init__(
        self,
        target_size: int = 1500,
        max_size: int = 2000,
        combine_titles: bool = True,
        preserve_tables: bool = True,
    ):
        """
        Args:
            target_size: Target chunk size in characters
            max_size: Maximum chunk size before forced split
            combine_titles: If True, combine titles with following content
            preserve_tables: If True, keep tables as separate chunks
        """
        self.target_size = target_size
        self.max_size = max_size
        self.combine_titles = combine_titles
        self.preserve_tables = preserve_tables

    def chunk(
        self, structured_elements: list[dict[str, Any]], metadata: Metadata = None
    ) -> list[Chunk]:
        """
        Chunk structured elements from unstructured library.

        Args:
            structured_elements: List of elements from unstructured parser
            metadata: Document metadata

        Returns:
            List of chunks preserving document structure
        """
        if metadata is None:
            metadata = Metadata(document_name="Unknown", document_path="Unknown")

        chunks = []
        chunk_index = 0
        current_chunk_elements = []
        current_size = 0
        current_title = None

        for element in structured_elements:
            element_type = element.get("type", "Text")
            element_text = element.get("text", "").strip()

            if not element_text:
                continue

            element_len = len(element_text)

            # Handle titles - store for combining with next chunk
            if element_type == "Title" and self.combine_titles:
                if current_chunk_elements:
                    # Save current chunk before starting new section
                    chunks.append(
                        self._create_chunk(
                            current_chunk_elements,
                            chunk_index,
                            metadata,
                            current_title,
                        )
                    )
                    chunk_index += 1
                    current_chunk_elements = []
                    current_size = 0

                current_title = element_text
                current_chunk_elements.append(element)
                current_size += element_len
                continue

            # Handle tables - keep as separate chunks if preserve_tables is True
            if element_type == "Table" and self.preserve_tables:
                # Save current chunk if any
                if current_chunk_elements:
                    chunks.append(
                        self._create_chunk(
                            current_chunk_elements,
                            chunk_index,
                            metadata,
                            current_title,
                        )
                    )
                    chunk_index += 1
                    current_chunk_elements = []
                    current_size = 0
                    current_title = None

                # Create table chunk
                chunks.append(
                    self._create_chunk([element], chunk_index, metadata, "Table")
                )
                chunk_index += 1
                continue

            # Check if adding this element would exceed target size
            if current_size + element_len > self.target_size and current_chunk_elements:
                # Create chunk from accumulated elements
                chunks.append(
                    self._create_chunk(
                        current_chunk_elements, chunk_index, metadata, current_title
                    )
                )
                chunk_index += 1
                current_chunk_elements = [element]
                current_size = element_len
                current_title = None
            else:
                current_chunk_elements.append(element)
                current_size += element_len

                # Force split if max size exceeded
                if current_size > self.max_size:
                    chunks.append(
                        self._create_chunk(
                            current_chunk_elements,
                            chunk_index,
                            metadata,
                            current_title,
                        )
                    )
                    chunk_index += 1
                    current_chunk_elements = []
                    current_size = 0
                    current_title = None

        # Add remaining elements as final chunk
        if current_chunk_elements:
            chunks.append(
                self._create_chunk(
                    current_chunk_elements, chunk_index, metadata, current_title
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
        "structure": StructureAwareChunking,
    }

    if strategy not in strategies:
        raise ValueError(
            f"Unknown chunking strategy: {strategy}. Available: {list(strategies.keys())}"
        )

    return strategies[strategy](**kwargs)
