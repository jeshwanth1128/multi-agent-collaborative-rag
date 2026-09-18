from docling.chunking import HybridChunker

_chunker = HybridChunker()


def chunk_document(document) -> list[str]:
    chunks: list[str] = []

    for chunk in _chunker.chunk(dl_doc=document):
        text = _chunker.contextualize(chunk).strip()

        if text:
            chunks.append(text)

    return chunks
