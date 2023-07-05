from langchain.vectorstores import VectorStore
from typing import Iterable, List, Any
from langchain.docstore.document import Document


class FakeVectorStore(VectorStore):
    """Fake vector store for testing purposes."""

    def add_texts(
        self, texts: Iterable[str], metadatas: List[dict] | None = None, **kwargs: Any
    ) -> List[str]:
        raise NotImplementedError

    def from_texts(
        self, texts: Iterable[str], metadatas: List[dict] | None = None, **kwargs: Any
    ) -> List[str]:
        raise NotImplementedError

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> List[Document]:
        raise NotImplementedError
