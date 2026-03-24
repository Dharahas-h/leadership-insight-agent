import json
from pathlib import Path
from uuid import uuid4

from app.services.chunkingService import Metadata, get_chunking_strategy
from app.services.documentService import parse_document


if __name__ == "__main__":
    # elements = partition_pdf(
    #     "./uploads/sample_annual_report.pdf",
    #     languages=["eng"],
    # )

    # print(f"Total elements extracted: {len(elements)}\n")
    # print("=" * 80)

    # # Count element types
    # element_types = {}
    # for element in elements:
    #     elem_type = element.category
    #     element_types[elem_type] = element_types.get(elem_type, 0) + 1

    # print("Element type distribution:")
    # for elem_type, count in sorted(element_types.items()):
    #     print(f"  - {elem_type}: {count}")

    # print("\n" + "=" * 80)
    # print("First 10 elements:")
    # print("=" * 80)

    # for i, element in enumerate(elements[:10]):
    #     print(f"\nElement {i + 1}:")
    #     print(f"  Type: {element.category}")
    #     print(f"  Text: {str(element)[:150]}...")
    #     if hasattr(element, "metadata"):
    #         print(f"  Metadata: {element.metadata}")

    # # Prepare JSON data
    # json_data = []
    # for i, element in enumerate(elements):
    #     element_dict = {
    #         "index": i,
    #         "type": element.category,
    #         "text": str(element),
    #         "metadata": element.metadata.to_dict()
    #         if hasattr(element, "metadata")
    #         else {},
    #     }
    #     json_data.append(element_dict)

    # # Save to uploads/parsed folder
    # parsed_folder = Path("./uploads/parsed")
    # parsed_folder.mkdir(parents=True, exist_ok=True)

    # output_file = parsed_folder / "sample_annual_report_parsed.json"
    # with open(output_file, "w", encoding="utf-8") as f:
    #     json.dump(json_data, f, indent=2, ensure_ascii=False)

    # print("\n" + "=" * 80)
    # print(f"JSON output saved to: {output_file}")
    # print(f"Total elements saved: {len(json_data)}")
    # print("=" * 80)
    parsed_content = parse_document("./uploads/sample_annual_report.pdf")
    chunk_metadata = Metadata(
        document_name="sample_annual_report.pdf",
        document_path="./uploads/sample_annual_report.pdf",
    )

    chunking_strategy = get_chunking_strategy(strategy="structure")
    chunks = chunking_strategy.chunk(parsed_content, metadata=chunk_metadata)
    chunks_path = Path("uploads/chunks/test2_chunks.json")
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
