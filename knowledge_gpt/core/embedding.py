from langchain.vectorstores import VectorStore
from knowledge_gpt.core.parsing import File
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from typing import Literal


def embed_docs(
    file: File, embeddings: Literal["openai"], vector_store: Literal["faiss"]
) -> VectorStore:
    """Embeds a File and returns the vector store"""
    if embeddings == "openai":
        embedding_model = OpenAIEmbeddings()  # type: ignore
    else:
        raise NotImplementedError

    if vector_store == "faiss":
        index = FAISS.from_documents(
            documents=file.docs,
            embedding=embedding_model,
        )
    else:
        raise NotImplementedError

    return index
