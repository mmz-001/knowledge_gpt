from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from knowledge_gpt.core.parsing import File


def chunk_file(file: File, chunk_size: int, chunk_overlap: int = 0) -> File:
    """Chunks each document in a file into smaller documents"""

    # split each document into chunks
    chunked_docs = []
    for doc in file.docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=chunk_overlap,
        )

        chunks = text_splitter.split_text(doc.page_content)

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": doc.metadata.get("page", 1),
                    "chunk": i,
                    "source": f"{doc.metadata.get('page', 1)}-{i}",
                },
            )
            chunked_docs.append(doc)

    file.docs = chunked_docs
    return file
