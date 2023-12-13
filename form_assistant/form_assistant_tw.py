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
    page_title="稅務表格助手",
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

st.header("稅務表格助手 with watsonx.ai 💬")

load_dotenv()

api_key = st.secrets["GENAI_KEY"]
api_endpoint = st.secrets["GENAI_API"]

api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=1500,
    min_new_tokens=1,
    # stream=True,
    top_k=50,
    top_p=1,
    stop_sequences=['<EOS>']
)

def buildform(requirement):
    prompt = f"""[INST]
    build a html form that for customer to input data for following requirement.
    end with <EOS>
    <<SYS>>需求: {requirement}
    <<SYS>>
    [/INST]html 表格:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def buildquestions(requirement):
    prompt = f"""[INST]
    build a few question to ask input for following requirements.
    end with <EOS>
    <<SYS>>需求: {requirement}
    <<SYS>>
    [/INST]提问:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def buildanswer(answer, requirement):
    prompt = f"""[INST]
    extract the answer in json from the answer to response to following requirements.
    end with <EOS>
    <<SYS>>
    回答: {answer}
    需求: {requirement}
    <<SYS>>
    [/INST]answer in json:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def fillform(answer, form):
    prompt = f"""[INST]
    populate the answer value in json to the html form.
    end with <EOS>
    <<SYS>>
    answer: {answer}
    form: {form}
    <<SYS>>
    [/INST]output:"""

    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

model = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

# Sidebar contents
with st.sidebar:
    st.title("稅務表格助手")

    btBuildForm = st.button("生成稅務表格")
    btBuildQuestions = st.button("生成引導提問")
    btFillForm = st.button("填寫稅務表格")

if "requirement" not in st.session_state:
    st.session_state.requirement = ""

if "form" not in st.session_state:
    st.session_state.form = ""

if "filledform" not in st.session_state:
    st.session_state.filledform = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.requirement = st.text_area("requirement",height=10)

if btBuildForm:
    with st.spinner(text="稍等哈...", cache=False):
        form = buildform(st.session_state.requirement)
        st.session_state.form = form
        st.session_state.filledform = form

if btFillForm:
    with st.spinner(text="稍等哈...", cache=False):
        st.session_state.filledform = fillform(st.session_state.answer, st.session_state.form)
        # st.components.v1.html(filledform)

if st.session_state.filledform != "":
    st.components.v1.html(st.session_state.filledform)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if btBuildQuestions:
    with st.chat_message("system"):
        with st.spinner(text="稍等哈...", cache=False):
            questions = buildquestions(st.session_state.requirement)
            st.markdown(questions)
            st.session_state.messages.append({"role": "agent", "content": questions})

if answer := st.chat_input("your answer"):
    with st.chat_message("user"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "user", "content": answer})
    with st.spinner(text="稍等哈...", cache=False):
        answerjson = buildanswer(answer, st.session_state.requirement)

    st.session_state.messages.append({"role": "agent", "content": answerjson}) 
    st.session_state.answer = answerjson
    with st.spinner(text="稍等哈...", cache=False):
        filledform = fillform(st.session_state.answer, st.session_state.form)
        st.session_state.filledform = filledform

    with st.chat_message("agent"):
        st.markdown(answerjson)