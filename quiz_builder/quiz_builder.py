import sys
import logging
import os
import tempfile
import pathlib

import streamlit as st
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer

from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.model import Model

from typing import Literal, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np
# Most GENAI logs are at Debug level.
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

st.set_page_config(
    page_title="quiz builder",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


st.header("quiz builder")
# chunk_size=1500
# chunk_overlap = 200

load_dotenv()

api_key = st.secrets["GENAI_KEY"]
api_endpoint = st.secrets["GENAI_API"]

api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

# handler = StdOutCallbackHandler()

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=1000,
    min_new_tokens=1,
    # stream=True,
    top_k=50,
    top_p=1
)

# Sidebar contents
with st.sidebar:
    st.title("quiz builder")
    uploaded_files = st.file_uploader("upload PDF documents", accept_multiple_files=True)

@st.cache_data
def read_pdf(uploaded_files,chunk_size =250,chunk_overlap=20):
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        # Write content to the temporary file
            temp_file.write(bytes_data)
            filepath = temp_file.name
            with st.spinner('uploading PDF documents'):
                loader = PyPDFLoader(filepath)
                data = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap=chunk_overlap)
                docs = text_splitter.split_documents(data)
                return docs

def read_push_embeddings(docs):
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    # embeddings = HuggingFaceEmbeddings()
    temp_dir = tempfile.TemporaryDirectory()
    db = Chroma.from_documents(docs, embeddings)
    return db

def buildquiz(informations, topic):
    prompt = f"""[INST]base on the topic and informations provided, 
    generate a question along with multiple choice quiz
    mark the answer and provide explaination.
    - create newline for each question and option.
    - please follow the layout provided in backquoted.
    - question should be scenario bases, descriptive, detail enough.
    - answer should be specific, descriptive, detail enough.
    - ensure the answer options be different, but similar enough that the user hard to determine.
    - ensure only one answer option be correct.
    - explain the correct answer as well as the incorrect answer options.
    - output in markdown.
    <<SYS>>
    topic:{topic}
    informations:
    {informations}
    layout: `question?

    a) answer option.
    b) answer option.
    c) answer option.
    d) answer option.

    correct answer (option), explaination.`
    <<SYS>>
    [/INST]
    markdown quiz:"""

    prompts = [prompt]
    answer = ""
    for response in model.generate_async(prompts,ordered=True):
        answer += response.generated_text
    return answer

docs = read_pdf(uploaded_files)
if docs is not None:
    db = read_push_embeddings(docs)

model = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

history = []

with st.chat_message("system"):
    st.write("input your question")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if topic := st.chat_input("your topic"):
    with st.chat_message("user"):
        st.markdown(topic)

    history += [topic]

    st.session_state.messages.append({"role": "user", "content": topic})
    with st.spinner(text="building...", cache=False):
        docs = db.similarity_search(topic)
        answer = buildquiz(docs, topic)

    st.session_state.messages.append({"role": "agent", "content": answer}) 

    with st.chat_message("agent"):
        st.markdown(answer)