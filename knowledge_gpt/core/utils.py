from typing import List
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.docstore.document import Document


def pop_docs_upto_limit(
    query: str, chain: StuffDocumentsChain, docs: List[Document], max_len: int
) -> List[Document]:
    """Pops documents from a list until the final prompt length is less than the max length."""

    token_count: int = chain.prompt_length(docs, question=query)  # type: ignore

    while token_count > max_len and len(docs) > 0:
        docs.pop()
        token_count = chain.prompt_length(docs, question=query)  # type: ignore

    return docs
