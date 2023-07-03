"""Add caching decorators to expensive functions"""

import streamlit as st

from knowledge_gpt.core.parsing import to_file
from knowledge_gpt.core.chunking import chunk_file
from knowledge_gpt.core.embedding import embed_docs
from knowledge_gpt.core.qa import get_answer, get_sources
from knowledge_gpt.core.parsing import File


def file_hash_func(file: File) -> str:
    """Get a unique hash for a file"""
    return file.id


to_file = st.cache_data(show_spinner=False)(to_file)
chunk_file = st.cache_data(show_spinner=False, hash_funcs={File: file_hash_func})(
    chunk_file
)
embed_docs = st.cache_data(show_spinner=False, hash_funcs={File: file_hash_func})(
    embed_docs
)
get_answer = st.cache_data(show_spinner=False, hash_funcs={File: file_hash_func})(
    get_answer
)
get_sources = st.cache_data(show_spinner=False, hash_funcs={File: file_hash_func})(
    get_sources
)
