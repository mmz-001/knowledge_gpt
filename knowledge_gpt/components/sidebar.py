import streamlit as st
import requests

from knowledge_gpt.components.faq import faq
import os

from dotenv import load_dotenv

load_dotenv()


openai_api_key_env = os.environ.get('OPENAI_API_KEY')

def set_openai_api_key(api_key: str):
    st.session_state["OPENAI_API_KEY"] = api_key

def get_contributors_markdown(repo_url):
    # Extract the owner and repo name from the URL
    parts = repo_url.split('/')
    owner = parts[-2]
    repo = parts[-1]

    # Define the GitHub API URL
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contributors'

    # Send a request to the GitHub API
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        contributors = response.json()
        markdown_list = []

        # Iterate through the contributors and create the markdown strings
        for contributor in contributors:
            username = contributor['login']
            profile_url = contributor['html_url']
            markdown_list.append(f'[{username}]({profile_url})')

        # Concatenate the markdown strings into a single string
        markdown_string = "Made by " + ', '.join(markdown_list)
        return markdown_string
    else:
        # raise ValueError(f'Error {response.status_code}: Could not fetch contributors for the given repository.')
        return ""


def sidebar():
    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
            "2. Upload a pdf, docx, or txt file📄\n"
            "3. Ask a question about the document💬\n"
        )
        if openai_api_key_env:
        
            api_key_input = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="Paste your OpenAI API key here (sk-...)",
                help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
                value= openai_api_key_env,
                
            )

        else:

            api_key_input = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="Paste your OpenAI API key here (sk-...)",
                help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
                value=st.session_state.get("OPENAI_API_KEY", ""),
                
            )


        if api_key_input:
            set_openai_api_key(api_key_input)

        st.markdown("---")
        st.markdown("# About")
        st.markdown(
            "📖KnowledgeGPT allows you to ask questions about your "
            "documents and get accurate answers with instant citations. "
        )
        st.markdown(
            "This tool is a work in progress. "
            "You can contribute to the project on [GitHub](https://github.com/mmz-001/knowledge_gpt) "  # noqa: E501
            "with your feedback and suggestions💡"
        )
        st.markdown(get_contributors_markdown(repo_url="https://github.com/mmz-001/knowledge_gpt"))
        st.markdown("---")

        faq()
