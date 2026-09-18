from pathlib import Path

from docling.document_converter import DocumentConverter

_converter = DocumentConverter()


def load_document(path: str | Path):
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    result = _converter.convert(file_path)

    return result.document
