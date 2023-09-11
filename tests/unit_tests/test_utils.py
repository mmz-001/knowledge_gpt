from knowledge_gpt.core.utils import pop_docs_upto_limit
from langchain.docstore.document import Document
from knowledge_gpt.core.debug import FakeChatModel
from langchain.chains.qa_with_sources.loading import _load_stuff_chain
from knowledge_gpt.core.prompts import STUFF_PROMPT


def test_single_doc_popped():
    """Test that a single document is popped when it exceeds the max length."""

    docs = [Document(page_content="Hello " * 500, metadata={"source": "1"})] * 2
    chain = _load_stuff_chain(llm=FakeChatModel(), prompt=STUFF_PROMPT)
    filtered_docs = pop_docs_upto_limit(
        query="test", chain=chain, docs=docs, max_len=1024
    )

    assert len(filtered_docs) == 1


def test_no_docs_popped():
    """Test that no documents are popped when they are below the max length."""

    docs = [Document(page_content="Hello " * 500, metadata={"source": "1"})] * 2
    chain = _load_stuff_chain(llm=FakeChatModel(), prompt=STUFF_PROMPT)
    filtered_docs = pop_docs_upto_limit(
        query="test", chain=chain, docs=docs, max_len=2048
    )

    assert len(filtered_docs) == 2


def test_all_docs_popped():
    """Test that all documents are popped when they exceed the max length."""

    docs = [Document(page_content="Hello " * 500, metadata={"source": "1"})] * 2
    chain = _load_stuff_chain(llm=FakeChatModel(), prompt=STUFF_PROMPT)
    filtered_docs = pop_docs_upto_limit(
        query="test", chain=chain, docs=docs, max_len=500
    )

    assert len(filtered_docs) == 0
