from typing import List
import streamlit as st


def wrap_text_in_html(text: str | List[str]) -> str:
    """Wraps each text block separated by newlines in <p> tags"""
    if isinstance(text, list):
        # Add horizontal rules between pages
        text = "\n<hr/>\n".join(text)
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])


def is_valid(index, query):
    if not st.session_state.get("api_key_configured"):
        st.error("Please configure your OpenAI API key!")
        return False
    if not index:
        st.error("Please upload a document!")
        return False
    if not query:
        st.error("Please enter a question!")
        return False
    return True
