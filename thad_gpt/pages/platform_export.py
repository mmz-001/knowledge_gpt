import streamlit as st
from thad_gpt.components.sidebar import sidebar

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Platform Export! 👋")


uploaded_files = st.session_state["uploaded_files"]

st.write(f"### There are {len(uploaded_files)} files uploaded.")

sidebar()
