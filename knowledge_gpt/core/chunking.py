from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from knowledge_gpt.core.parsing import File


def chunk_file(
    file: File, chunk_size: int, chunk_overlap: int = 0, model_name="gpt-3.5-turbo"
) -> File:
    """Chunks each document in a file into smaller documents
    according to the specified chunk size and overlap
    where the size is determined by the number of token for the specified model.
    """

    # split each document into chunks
    chunked_docs = []
    for doc in file.docs:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name=model_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        chunks = text_splitter.split_text(doc.page_content)

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "page": doc.metadata.get("page", 1),
                    "chunk": i + 1,
                    "source": f"{doc.metadata.get('page', 1)}-{i + 1}",
                },
            )
            chunked_docs.append(doc)

    file.docs = chunked_docs
    return file
