from typing import List
import streamlit as st
from langchain.docstore.document import Document


def wrap_doc_in_html(docs: List[Document]) -> str:
    """Wraps each page in document separated by newlines in <p> tags"""
    text = [doc.page_content for doc in docs]
    if isinstance(text, list):
        # Add horizontal rules between pages
        text = "\n<hr/>\n".join(text)
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])


def is_valid(index, query):
    if not index:
        st.error("Please upload a document!")
        return False
    if not query:
        st.error("Please enter a question!")
        return False
    return True
