from typing import List
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from knowledge_gpt.core.prompts import STUFF_PROMPT
from langchain.docstore.document import Document
from knowledge_gpt.core.embedding import FolderIndex
from pydantic import BaseModel
from langchain.chat_models.base import BaseChatModel


class AnswerWithSources(BaseModel):
    answer: str
    sources: List[Document]


def query_folder(
    query: str,
    folder_index: FolderIndex,
    llm: BaseChatModel,
    return_all: bool = False,
) -> AnswerWithSources:
    """Queries a folder index for an answer.

    Args:
        query (str): The query to search for.
        folder_index (FolderIndex): The folder index to search.
        return_all (bool): Whether to return all the documents from the embedding or
        just the sources for the answer.
        model (str): The model to use for the answer generation.
        **model_kwargs (Any): Keyword arguments for the model.

    Returns:
        AnswerWithSources: The answer and the source documents.
    """

    chain = load_qa_with_sources_chain(
        llm=llm,
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )

    relevant_docs = folder_index.index.similarity_search(query, k=5)
    result = chain(
        {"input_documents": relevant_docs, "question": query}, return_only_outputs=True
    )
    sources = relevant_docs

    if not return_all:
        sources = get_sources(result["output_text"], folder_index)

    answer = result["output_text"].split("SOURCES: ")[0]

    return AnswerWithSources(answer=answer, sources=sources)


def get_sources(answer: str, folder_index: FolderIndex) -> List[Document]:
    """Retrieves the docs that were used to answer the question the generated answer."""

    source_keys = [s for s in answer.split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for file in folder_index.files:
        for doc in file.docs:
            if doc.metadata["source"] in source_keys:
                source_docs.append(doc)
    return source_docs
