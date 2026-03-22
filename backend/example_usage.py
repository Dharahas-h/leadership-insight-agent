"""
Example usage of structure-aware parsing and chunking for annual/quarterly reports.

This demonstrates how to use the unstructured library for parsing PDFs and DOCX files
with structure preservation (titles, sections, tables, etc.) and intelligent chunking.
"""

from pathlib import Path

from app.services.chunkingService import Metadata, get_chunking_strategy
from app.services.parsingService import parse_document


def example_structure_aware_parsing(pdf_path: str):
    """
    Example: Parse a PDF document with structure awareness.

    Args:
        pdf_path: Path to a PDF file (e.g., annual report, quarterly report)
    """
    print("=" * 80)
    print("EXAMPLE 1: Structure-Aware Parsing")
    print("=" * 80)

    # Parse with unstructured library (structure-aware)
    print(f"\nParsing document: {pdf_path}")
    structured_elements = parse_document(pdf_path)

    if isinstance(structured_elements, list):
        print(f"\n✓ Extracted {len(structured_elements)} structured elements")

        # Show first few elements with their types
        print("\nFirst 10 elements:")
        for i, element in enumerate(structured_elements[:10]):
            element_type = element.get("type", "Unknown")
            text_preview = element.get("text", "")[:80]
            print(f"  {i + 1}. [{element_type}] {text_preview}...")

        # Count element types
        element_types = {}
        for element in structured_elements:
            elem_type = element.get("type", "Unknown")
            element_types[elem_type] = element_types.get(elem_type, 0) + 1

        print("\nElement type distribution:")
        for elem_type, count in sorted(element_types.items()):
            print(f"  - {elem_type}: {count}")

        return structured_elements
    print("✗ Returned plain text instead of structured elements")
    return None


def example_structure_aware_chunking(structured_elements: list):
    """
    Example: Create chunks from structured elements.

    Args:
        structured_elements: List of elements from parse_document
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Structure-Aware Chunking")
    print("=" * 80)

    # Create metadata
    metadata = Metadata(
        document_name="Annual_Report_2024.pdf",
        document_path="/path/to/report.pdf",
    )

    # Create structure-aware chunking strategy
    chunking_strategy = get_chunking_strategy(
        strategy="structure",
        target_size=1500,  # Target chunk size in characters
        max_size=2000,  # Maximum size before forced split
        combine_titles=True,  # Combine section titles with content
        preserve_tables=True,  # Keep tables as separate chunks
    )

    # Generate chunks
    print("\nGenerating chunks...")
    chunks = chunking_strategy.chunk(structured_elements, metadata=metadata)

    print(f"✓ Created {len(chunks)} chunks")

    # Display chunk statistics
    chunk_sizes = [len(chunk.text) for chunk in chunks]
    avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
    min_size = min(chunk_sizes) if chunk_sizes else 0
    max_size = max(chunk_sizes) if chunk_sizes else 0

    print("\nChunk statistics:")
    print(f"  - Average size: {avg_size:.0f} characters")
    print(f"  - Min size: {min_size} characters")
    print(f"  - Max size: {max_size} characters")

    # Show first 3 chunks
    print("\nFirst 3 chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Type: {chunk.metadata.element_type}")
        print(f"Page: {chunk.metadata.page_number}")
        print(f"Size: {len(chunk.text)} characters")
        print(f"Preview: {chunk.text[:150]}...")

    return chunks


def example_comparison():
    """
    Example: Compare structure-aware vs traditional chunking.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Comparison of Chunking Methods")
    print("=" * 80)

    # Sample text (simulating parsed content)
    sample_text = """
    Executive Summary

    This annual report presents our company's performance for fiscal year 2024.
    We achieved significant growth across all business segments.

    Financial Highlights

    Revenue increased by 25% year-over-year, reaching $500 million.
    Operating margin improved to 18%, up from 15% in the previous year.
    Net income grew to $90 million, representing a 30% increase.
    """

    # Traditional sentence-based chunking
    print("\n1. Sentence-based chunking (traditional):")
    sentence_strategy = get_chunking_strategy(strategy="sentence", target_size=100)
    sentence_chunks = sentence_strategy.chunk(
        sample_text,
        Metadata(document_name="report.pdf", document_path="/path/to/report.pdf"),
    )
    print(f"   Created {len(sentence_chunks)} chunks")
    for i, chunk in enumerate(sentence_chunks[:2]):
        print(f"   Chunk {i + 1}: {chunk.text[:80]}...")

    print("\n2. Structure-aware chunking:")
    print("   (Requires structured elements from unstructured library)")
    print("   Benefits:")
    print("   - Preserves section context (titles stay with content)")
    print("   - Keeps tables intact")
    print("   - Maintains document hierarchy")
    print("   - Better for Q&A and RAG applications")


def main():
    """
    Main function to run all examples.
    """
    print("\n" + "=" * 80)
    print("STRUCTURE-AWARE DOCUMENT PROCESSING EXAMPLES")
    print("=" * 80)

    # Example PDF path (replace with your actual file)
    pdf_path = "uploads/sample_report.pdf"

    if Path(pdf_path).exists():
        # Run full examples with actual file
        structured_elements = example_structure_aware_parsing(pdf_path)
        if structured_elements:
            example_structure_aware_chunking(structured_elements)
    else:
        print(f"\nNote: Sample file not found at {pdf_path}")
        print("Skipping file-based examples. Showing comparison only.\n")

    # Always run comparison
    example_comparison()

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETED")
    print("=" * 80)

    print("\n💡 Key Benefits for Annual/Quarterly Reports:")
    print("   ✓ Preserves document structure (sections, subsections)")
    print("   ✓ Keeps tables intact and separate")
    print("   ✓ Maintains title-content relationships")
    print("   ✓ Better context for embeddings and retrieval")
    print("   ✓ Improved accuracy for Q&A systems")


if __name__ == "__main__":
    main()
