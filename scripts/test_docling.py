from pathlib import Path

from docling.document_converter import DocumentConverter


def main() -> None:
    pdf_path = Path("data/documents/sample.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(
            "Put a PDF at data/documents/sample.pdf before running this script."
        )

    converter = DocumentConverter()
    result = converter.convert(pdf_path)

    markdown = result.document.export_to_markdown()

    print("\n--- DOCUMENT PREVIEW ---\n")
    print(markdown[:3000])
    print("\n--- END PREVIEW ---")


if __name__ == "__main__":
    main()
