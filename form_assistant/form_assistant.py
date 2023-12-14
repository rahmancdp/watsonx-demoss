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
    page_title="form assistant",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 500px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
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

st.header("form assistant with watsonx.ai 💬")

load_dotenv()

api_key = st.secrets["GENAI_KEY"]
api_endpoint = st.secrets["GENAI_API"]

api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=3000,
    min_new_tokens=1,
    # stream=True,
    top_k=50,
    top_p=1,
    stop_sequences=['<EOS>']
)

def buildjson(requirement):
    prompt = f"""[INST]
    build a json structure for customer to input data for following requirement.
    end with <EOS>
    <<SYS>>requirements: {requirement}
    <<SYS>>
    [/INST]json:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def buildform(requirement, jsonform):
    prompt = f"""[INST]
    build a html form that for customer to input value for following json base on the requirement.
    dont show JSON.
    end with <EOS>
    <<SYS>>
    requirement: {requirement}
    json: `{jsonform}`
    <<SYS>>
    [/INST]html form:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def buildquestions(requirement,answerjson):
    prompt = f"""[INST]you are customer service agent that need to guide the user to fill the form with following steps:
    1. list all answer with no value.
    2. for those non-answer item, create a question, be aware of the requriements provided.
    3. say thank you if no questions.
    note: 
    the question be polite, precise, simple, and you can provide example hints if not yet hv value.
    dont show explaination.
    dont ask question if item value in answer value exist.
    end with <EOS>
    <<SYS>>requirements: {requirement}
    answer in json: `{answerjson}`
    <<SYS>>
    [/INST]output:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def buildanswer(answer, existinganswer, jsonform):
    prompt = f"""[INST]
    extract the answer in json from the answer to response to the json form.
    notes:
    merge the answer with existing answer.
    show the merged answer only.
    end with <EOS>
    <<SYS>>
    answers: {answer}
    existing answers: `{existinganswer}`
    json form: {jsonform}
    <<SYS>>
    [/INST]merged answer:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def fillform(answer, form):
    prompt = f"""[INST]
    fill the html form with the answer value in json.
    dont show json.
    end with <EOS>
    <<SYS>>
    answer: `{answer}`
    html form: {form}
    <<SYS>>
    [/INST]html form with answer:"""

    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

model = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)


if "requirement" not in st.session_state:
    st.session_state.requirement = ""

if "jsonform" not in st.session_state:
    st.session_state.jsonform = ""

if "form" not in st.session_state:
    st.session_state.form = ""

if "filledform" not in st.session_state:
    st.session_state.filledform = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar contents
with st.sidebar:
    st.title("form assistant")

    btBuildForm = st.button("build form")
    btBuildQuestions = st.button("guide form filling with questions")
    # btFillForm = st.button("fill form")

st.session_state.requirement = st.text_area("requirement",height=10)

if btBuildForm:
    with st.spinner(text="building the form...", cache=False):
        jsonform = buildjson(st.session_state.requirement)
        form = buildform(st.session_state.requirement, st.session_state.jsonform)
        st.session_state.jsonform = jsonform
        st.session_state.form = form
        st.session_state.filledform = form

# if btFillForm:
#     with st.spinner(text="building the form...", cache=False):
#         st.session_state.filledform = fillform(st.session_state.answer, st.session_state.form)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if btBuildQuestions:
    with st.chat_message("system"):
        with st.spinner(text="building the questions...", cache=False):
            questions = buildquestions(st.session_state.answer,st.session_state.requirement)
            st.markdown(questions)
            st.session_state.messages.append({"role": "agent", "content": questions})

if answer := st.chat_input("your answer"):
    with st.chat_message("user"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "user", "content": answer})
    with st.spinner(text="In progress...", cache=False):
        answerjson = buildanswer(answer, st.session_state.answer, st.session_state.jsonform)
        st.session_state.answer = answerjson
        filledform = fillform(st.session_state.answer, st.session_state.form)
        st.session_state.filledform = filledform

    with st.chat_message("system"):
        with st.spinner(text="building the questions...", cache=False):
            questions = buildquestions(st.session_state.answer,st.session_state.requirement)
            st.markdown(questions)
            st.session_state.messages.append({"role": "agent", "content": questions})

with st.sidebar:
    with st.container(border=True):
        st.components.v1.html(st.session_state.filledform,height=300)
    st.code(st.session_state.answer,language="json")