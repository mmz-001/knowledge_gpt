from typing import Any, List

# from langchain.chains.qa_with_sources import load_qa_with_sources_chain
# from knowledge_gpt.core.prompts import STUFF_PROMPT
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI
from knowledge_gpt.core.embedding import FolderIndex
from knowledge_gpt.core.debug import FakeChatModel
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage


class AnswerWithSources(BaseModel):
    answer: str
    sources: List[Document]


def query_folder(
    query: str,
    instructions: str,
    folder_index: FolderIndex,
    return_all: bool = False,
    model: str = "openai",
    **model_kwargs: Any,
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
    supported_models = {
        "openai": ChatOpenAI,
        "debug": FakeChatModel,
    }

    if model in supported_models:
        llm = supported_models[model](model="gpt-3.5-turbo-16k-0613", **model_kwargs)
    else:
        raise ValueError(f"Model {model} not supported.")

    messages = [
        SystemMessage(content="# Instructions\n\n" + instructions),
        AIMessage(content="# Context\n\n" + folder_index.files[0].docs[0].page_content),
        HumanMessage(content="# Question\n\n" + query),
    ]

    result = llm.predict_messages(messages)

    return AnswerWithSources(answer=result.content, sources=[])


def get_sources(answer: str, folder_index: FolderIndex) -> List[Document]:
    """Retrieves the docs that were used to answer the question the generated answer."""

    source_keys = [s for s in answer.split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for file in folder_index.files:
        for doc in file.docs:
            if doc.metadata["source"] in source_keys:
                source_docs.append(doc)

    return source_docs
