from langchain.vectorstores import VectorStore
from knowledge_gpt.core.parsing import File
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from typing import List, Type
from langchain.docstore.document import Document


class FolderIndex:
    """Index for a collection of files (a folder)"""

    def __init__(self, files: List[File], index: VectorStore):
        self.name: str = "default"
        self.files = files
        self.index: VectorStore = index

    @staticmethod
    def _combine_files(files: List[File]) -> List[Document]:
        """Combines all the documents in a list of files into a single list."""

        all_texts = []
        for file in files:
            for doc in file.docs:
                doc.metadata["file_name"] = file.name
                doc.metadata["file_id"] = file.id
                all_texts.append(doc)

        return all_texts

    @classmethod
    def from_files(
        cls, files: List[File], embeddings: Embeddings, vector_store: Type[VectorStore]
    ) -> "FolderIndex":
        """Creates an index from files."""

        all_docs = cls._combine_files(files)

        index = vector_store.from_documents(
            documents=all_docs,
            embedding=embeddings,
        )

        return cls(files=files, index=index)


def embed_files(
    files: List[File], embedding: str, vector_store: str, **kwargs
) -> FolderIndex:
    """Embeds a collection of files and stores them in a FolderIndex."""

    supported_embeddings: dict[str, Type[Embeddings]] = {
        "openai": OpenAIEmbeddings,
    }
    supported_vector_stores: dict[str, Type[VectorStore]] = {
        "faiss": FAISS,
    }

    if embedding in supported_embeddings:
        _embeddings = supported_embeddings[embedding](**kwargs)
    else:
        raise NotImplementedError(f"Embedding {embedding} not supported.")

    if vector_store in supported_vector_stores:
        _vector_store = supported_vector_stores[vector_store]
    else:
        raise NotImplementedError(f"Vector store {vector_store} not supported.")

    return FolderIndex.from_files(
        files=files, embeddings=_embeddings, vector_store=_vector_store
    )
