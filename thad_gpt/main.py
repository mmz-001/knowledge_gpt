import streamlit as st
from openai.error import OpenAIError
import os
from thad_gpt.components.sidebar import sidebar
from thad_gpt.utils import (
    embed_docs,
    get_answer,
    get_sources,
    parse_docx,
    parse_pdf,
    parse_txt,
    search_docs,
    text_to_docs,
    wrap_text_in_html,
)

print('st.secrets', st.secrets)
st.session_state["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", None)


def clear_submit():
    st.session_state["submit"] = False


st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("🧠 ThadGPT")

sidebar()

uploaded_files = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
    on_change=clear_submit,
    accept_multiple_files=True,
)
print('uploaded_files',uploaded_files)
index = None

if len(uploaded_files) == 0:
    doc = None
if len(uploaded_files) > 0:
    doc = []

    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            doc.extend(parse_pdf(uploaded_file))
        elif uploaded_file.name.endswith(".docx"):
            doc.extend(parse_docx(uploaded_file))
        elif uploaded_file.name.endswith(".txt"):
            doc.extend(parse_txt(uploaded_file))
        else:
            raise ValueError("File type not supported!")

    print("parsed docs", doc)    

    text = text_to_docs(doc)

    try:
        with st.spinner("Indexing document... This may take a while⏳"):
            index = embed_docs(text)
        st.session_state["api_key_configured"] = True
    except OpenAIError as e:
        st.error(e._message)

query = st.text_area("Ask a question about the document", on_change=clear_submit)
with st.expander("Advanced Options"):
    show_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
    show_full_doc = st.checkbox("Show parsed contents of the document")

if show_full_doc and doc:
    with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_text_in_html(doc)}</p>", unsafe_allow_html=True)

button = st.button("Submit")
if button or st.session_state.get("submit"):
    if not st.session_state.get("api_key_configured"):
        st.error("Please configure your OpenAI API key!")
    elif not index:
        st.error("Please upload a document!")
    elif not query:
        st.error("Please enter a question!")
    else:
        st.session_state["submit"] = True
        # Output Columns
        answer_col, sources_col = st.columns(2)
        sources = search_docs(index, query)

        try:
            answer = get_answer(sources, query)
            if not show_all_chunks:
                # Get the sources for the answer
                sources = get_sources(answer, sources)

            with answer_col:
                st.markdown("#### Answer")
                st.markdown(answer["output_text"].split("SOURCES: ")[0])

            with sources_col:
                st.markdown("#### Sources")
                for source in sources:
                    st.markdown(source.page_content)
                    st.markdown(source.metadata["source"])
                    st.markdown("---")

        except OpenAIError as e:
            st.error(e._message)
