from typing import Any, Dict, List, Tuple
from knowledge_gpt.core.parsing import File
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from knowledge_gpt.core.prompts import STUFF_PROMPT
from langchain.docstore.document import Document
from typing import Literal
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import VectorStore


def get_answer(
    query: str, model: Literal["openai"], index: VectorStore
) -> Tuple[Dict[str, Any], List[Document]]:
    """Gets an answer to a question from a file."""

    if model == "openai":
        _model = ChatOpenAI(temperature=0)  # type: ignore
    else:
        raise NotImplementedError

    # Get the answer
    chain = load_qa_with_sources_chain(
        llm=_model,
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )

    relevant_docs = index.similarity_search(query, k=5)

    answer = chain(
        {"input_documents": relevant_docs, "question": query}, return_only_outputs=True
    )
    return answer, relevant_docs


def get_sources(answer: Dict[str, Any], file: File) -> List[Document]:
    """Gets the source documents for an answer."""

    # Get sources for the answer
    source_keys = [s for s in answer["output_text"].split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for doc in file.docs:
        if doc.metadata["source"] in source_keys:
            source_docs.append(doc)

    return source_docs
