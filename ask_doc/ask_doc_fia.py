import sys
import logging
import os
import tempfile
import pathlib
import time

import streamlit as st
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer

# from genai.credentials import Credentials
# from genai.schemas import GenerateParams
# from genai.model import Model

from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM


from typing import Literal, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np
# Most GENAI logs are at Debug level.
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

st.set_page_config(
    page_title="技术支持",
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


st.header("稅法查詢")
# chunk_size=1500
# chunk_overlap = 200

load_dotenv()

api_key = os.getenv("API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

# handler = StdOutCallbackHandler()

creds = {
    "url"    : "https://us-south.ml.cloud.ibm.com",
    "apikey" : api_key
}

params = {
    GenParams.DECODING_METHOD:"greedy",
    GenParams.MAX_NEW_TOKENS:1000,
    GenParams.MIN_NEW_TOKENS:1,
    GenParams.TEMPERATURE:0.5,
    GenParams.TOP_K:50,
    GenParams.TOP_P:1
}

@st.cache_data
def read_pdf(uploaded_files,chunk_size =250,chunk_overlap=20):
    docs = []
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        # Write content to the temporary file
            temp_file.write(bytes_data)
            filepath = temp_file.name
            with st.spinner('正在上傳PDF'):
                loader = PyPDFLoader(filepath)
                data = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap=chunk_overlap)
                docs += text_splitter.split_documents(data)
    return docs

def read_push_embeddings(docs):
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    # embeddings = HuggingFaceEmbeddings()
    temp_dir = tempfile.TemporaryDirectory()
    db = FAISS.from_documents(docs, embeddings)
    return db

def querypdf(informations, history, question):
    # prompt = f"""
    # answer the question in 5 sentences base on the informations:
    # informations:
    # {informations}
    # question:
    # {question}
    # answer in point form:"""

    prompt = f"""[INST]作為一位稅法專家，請根據提供的稅法文件用中文回答。
    -請只根據提供的稅法文件回答，說明信息來源。
    -請只用中文回答，不要出現亂碼。
    -對於需要計算的內容，請小心一步步計算作答，否則只提供算式就好，不要幫助貴賓計算。
    -一步步解答。
    -如果不知道，不要猜測，就說不知道，並請貴賓查看網站信息。
    <<SYS>>
    稅法文件:
    {informations}
    前面的查詢:
    {history}
    <<SYS>>
    提問:
    {question}
    [/INST]
    解答:"""

    prompts = [prompt]
    answer = ""
    for response in model.generate_text(prompts):
        answer += response.replace("\\n\\n","\n")
    return answer

model = Model("meta-llama/llama-2-13b-chat",creds, params, project_id)

history = []

if "db" not in st.session_state:
    st.session_state.db = None

# Sidebar contents
with st.sidebar:
    st.title("稅法查詢")
    uploaded_files = st.file_uploader("上传一个PDF文档", accept_multiple_files=True)
    if st.session_state.db is None:
        starttime = time.time()

        docs = read_pdf(uploaded_files)
        if docs is not None and len(docs) > 0:
            st.session_state.db = read_push_embeddings(docs)

        endtime = time.time()
        print(f"take {endtime-starttime} to ingest the doc to vectordb")

with st.chat_message("system"):
    st.write("請輸入你的查詢")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("your query"):
    with st.chat_message("user"):
        st.markdown(query)

    history += [query]

    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner(text="正在查詢中...", cache=False):
        starttime = time.time()
        docs = st.session_state.db.similarity_search(query)
        endtime = time.time()
        print(f"take {endtime-starttime} to search similary")
        starttime = time.time()
        answer = querypdf(docs, history, query)
        endtime = time.time() 
        print(f"take {endtime-starttime} to build the answer")

    st.session_state.messages.append({"role": "agent", "content": answer}) 

    with st.chat_message("agent"):
        st.markdown(answer)