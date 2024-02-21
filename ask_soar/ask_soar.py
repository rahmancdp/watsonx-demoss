import sys
import logging
import os
import tempfile
import pathlib
import time

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from sentence_transformers import SentenceTransformer

from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.extensions.langchain import WatsonxLLM


from typing import Literal, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np
# Most GENAI logs are at Debug level.
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

st.set_page_config(
    page_title="ask SOAR",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("query security logs")
# chunk_size=1500
# chunk_overlap = 200

load_dotenv()

api_key = os.getenv("API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

creds = {
    "url"    : "https://us-south.ml.cloud.ibm.com",
    "apikey" : api_key
}

params = {
    GenParams.DECODING_METHOD:"greedy",
    GenParams.MAX_NEW_TOKENS:3000,
    GenParams.MIN_NEW_TOKENS:1,
    GenParams.TEMPERATURE:0.5,
    GenParams.TOP_K:50,
    GenParams.TOP_P:1
}

# @st.cache_data
def read_text(uploaded_files,chunk_size =250,chunk_overlap=20):
    docs = []
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        # Write content to the temporary file
            temp_file.write(bytes_data)
            filepath = temp_file.name
            print(filepath)
            # with st.spinner('upload cve'):
            loader = TextLoader(filepath)
            data = loader.load()
            # text_splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap=chunk_overlap)
            # chunks = text_splitter.split_documents(data)
            docs += data
    print(len(docs))
    return docs

def read_push_embeddings(docs):
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    # embeddings = HuggingFaceEmbeddings()
    temp_dir = tempfile.TemporaryDirectory()
    db = Chroma.from_documents(docs, embeddings)
    return db

def querycode(informations, question):
    prompt = f"""[INST]you are security expert,
please answer the question in cve information in backquoted.
<<SYS>>
cve information:`{informations}`
question:`{question}`
<<SYS>>
[/INST]
answer:"""

    prompts = [prompt]
    answer = ""
    for response in model.generate_text(prompts):
        answer += response
    return answer

model = Model("meta-llama/llama-2-70b-chat",creds, params, project_id)

if "db" not in st.session_state:
    st.session_state.db = None

# Sidebar contents
with st.sidebar:
    st.title("query security logs")
    uploaded_files = st.file_uploader("upload security logs", accept_multiple_files=True)
    docs = read_text(uploaded_files)
    if docs is not None and len(docs) > 0:
        print('here>>>>>>>>>>built vectordb')
        st.session_state.db = read_push_embeddings(docs)
        print('built vectordb')

with st.chat_message("system"):
    st.write("input your query")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("your query"):
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner(text="querying...", cache=False):
        docs = st.session_state.db.similarity_search(query)
        answer = querycode(docs, query)
        st.session_state.messages.append({"role": "agent", "content": answer}) 

        with st.chat_message("agent"):
            st.markdown(answer)