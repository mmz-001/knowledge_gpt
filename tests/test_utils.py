from langchain.docstore.document import Document

from knowledge_gpt.utils import get_sources


def test_get_sources():
    """Test getting sources from an answer"""
    docs = [
        Document(page_content="This is a test document.", metadata={"source": "1-5"}),
        Document(page_content="This is a test document.", metadata={"source": "2-6"}),
    ]
    answer = {"output_text": "This is a test answer. SOURCES: 1-5, 3-8"}
    sources = get_sources(answer, docs)
    assert sources == [docs[0]]
