import streamlit as st
from openai.error import OpenAIError

from knowledge_gpt.components.sidebar import sidebar
from knowledge_gpt.utils import (
    embed_docs,
    get_answer_by_chat,
    get_answer_by_source,
    get_sources,
    parse_docx,
    parse_pdf,
    parse_txt,
    search_docs,
    text_to_docs,
    wrap_text_in_html,
)



def clear_submit():
    st.session_state["submit"] = False


def file_updated(uploaded_file):
    clear_submit()
    # uploaded_file = st.session_state.get("uploaded_file", None)
    if not uploaded_file:
        st.error("No file uploaded!")
    index = None
    doc = None
    if uploaded_file:
        st.info("File changed to: " + uploaded_file.name)
        if uploaded_file.name.endswith(".pdf"):
            doc = parse_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".docx"):
            doc = parse_docx(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            doc = parse_txt(uploaded_file)
        else:
            st.error("File type not supported!")
            raise ValueError("File type not supported!")
        st.session_state["doc"] = doc
        st.info("Uploaded file parsed!")
        text = text_to_docs(doc)
        try:
            with st.spinner("Indexing document... This may take a while⏳"):
                index = embed_docs(text)
                st.session_state["index"] = index
                # print(f'text: {text[0]}')
                # print(f'index: {index}')
                st.info("Uploaded file indexed! ")
            st.session_state["api_key_configured"] = True
        except OpenAIError as e:
            st.error(e._message)
    else:
        st.info("No file uploaded! ")


st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")

sidebar()

uploaded_file = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
)
st.button(
    "Parse Document",
    on_click=file_updated,
    args=(uploaded_file,),
)

st.session_state["query"] = st.text_area("Ask a question about the document", on_change=clear_submit)
with st.expander("Advanced Options"):
    show_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
    show_full_doc = st.checkbox("Show parsed contents of the document")

if show_full_doc and 'doc' in st.session_state:
    with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_text_in_html(st.session_state['doc'])}</p>", unsafe_allow_html=True)

button = st.button("Submit")
if button or st.session_state.get("submit"):
    if not st.session_state.get("OPENAI_API_KEY"):
        st.error("Please configure your OpenAI API key!")
    elif "query" not in st.session_state or st.session_state["query"] == "":
        st.error("Please enter a question!")
    elif 'index' not in st.session_state:
        st.error("Please upload a document!")
        # answer_col, sources_col = st.columns(2)
        # try:
        #     answer = get_answer_by_chat(query=query)
        # except OpenAIError as e:
        #     st.error(e._message)
        
        # with answer_col:
        #     st.markdown("#### Answer")
        #     st.markdown(answer)
    else:
        st.session_state["submit"] = True
        # Output Columns
        answer_col, sources_col = st.columns(2)
        query = st.session_state["query"]
        # print(f'doc: {st.session_state["doc"]}')
        # print(f'index: {st.session_state["index"]}')
        sources = search_docs(st.session_state["index"], query)
        # print(f'query: {query}')
        # print(f'sources: {sources}')
        try:
            answer = get_answer_by_source(sources, query)
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
