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
    max_new_tokens=1000,
    min_new_tokens=1,
    temperature=0.05,
    repetition_penalty=1.1,
    # stream=True,
    top_k=50,
    top_p=1,
    stop_sequences=['end_of_form','<>','<EOS>'],
)

def buildjson(requirement):
    prompt = f"""[INST]
    <<SYS>>
    build a json structure for customer to input data for following requirement.
    - flatten the json structure.
    - end with <EOS>
    <</SYS>>
    requirements: {requirement}
    [/INST]json:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("end_of_form","")

def buildform(requirement, jsonform):
    prompt = f"""[INST]
    <<SYS>>
    build a html form that for customer to input value for following json base on the requirement.
    - for option, add a empty item if no value.
    - dont show JSON.
    - end with <EOS>
    <</SYS>>
    requirement: {requirement}
    json: `{jsonform}`
    [/INST]html form:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<end_of_form>","")

def buildquestions(answerjson, requirement, lastmessage):
    prompt = f"""[INST]
    <<SYS>>you are customer service agent, generate message to guiding the user to fill the form with following steps:
    1. understand the answer and requriement provided in backquoted.
    2. check the answer json, gather a list the answer fields with empty value.
    3. if no field shortlisted in step 2, then just say thank you and skip step 4.
    4. for all field shortlisted in step 2, generate a concise question to request the answer.
    5. generate message with style similar to the last message provided in backquoted.
    note: 
    - empty value means empty string or zero or false or none.
    - dont repeat.
    - dont show (empty)
    - dont show json.
    <</SYS>>
    requirements: `{requirement}`
    answer: {answerjson}
    last message: `{lastmessage}`
    [/INST]response:"""

    # print("prompt:"+prompt)

    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    # print(output)
    return output.replace("<EOS>","")

def buildanswer(answer, existinganswer, jsonform):
    prompt = f"""[INST]
    <<SYS>>
    extract the answer in json from the answer to response to the json form.
    notes:
    - merge the answer with existing answer.
    - dont guess.
    - show the merged answer only.
    - end with <EOS>
    <</SYS>>
    answers: {answer}
    existing answers: {existinganswer}
    json form: {jsonform}
    [/INST]merged answer:"""
    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

def fillform(answer, form):
    prompt = f"""[INST]
    <<SYS>>
    fill the html form with the answer value in json.
    - for option, add a empty item if no value. select empty item if the field has empty value.
    - dont show json.
    - end with <EOS>
    <</SYS>>
    answer: `{answer}`
    html form: {form}
    [/INST]html form with answer:"""

    print(prompt)

    output = ""
    for response in model.generate([prompt]):
        output = response.generated_text
    return output.replace("<EOS>","")

# model = Model(model="mistralai/mistral-7b-instruct-v0-2",credentials=creds, params=params)
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

if "lastmessage" not in st.session_state:
    st.session_state.lastmessage = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar contents
with st.sidebar:
    st.title("form assistant")

    btBuildForm = st.button("build form and guide me to fill")
    # btBuildQuestions = st.button("guide form filling with questions")
    # btFillForm = st.button("fill form")

st.session_state.requirement = st.text_area("requirement",height=10)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if btBuildForm:
    with st.spinner(text="building the form...", cache=False):
        jsonform = buildjson(st.session_state.requirement)
        form = buildform(st.session_state.requirement, st.session_state.jsonform)
        st.session_state.jsonform = jsonform
        st.session_state.form = form
        st.session_state.filledform = form
        st.session_state.answer = jsonform

    with st.chat_message("system"):
        with st.spinner(text="building the questions...", cache=False):
            questions = buildquestions("{}",st.session_state.requirement,"").replace('\\n', '\n').replace('\\t', '\t')
            st.session_state.lastmessage = questions
            st.markdown(questions)
            st.session_state.messages.append({"role": "agent", "content": questions})


# if btFillForm:
#     with st.spinner(text="building the form...", cache=False):
#         st.session_state.filledform = fillform(st.session_state.answer, st.session_state.form)

# if btBuildQuestions:
#     with st.chat_message("system"):
#         with st.spinner(text="building the questions...", cache=False):
#             questions = buildquestions("{}",st.session_state.requirement).replace('\\n', '\n').replace('\\t', '\t')
#             st.markdown(questions)
#             st.session_state.messages.append({"role": "agent", "content": questions})

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
            questions = buildquestions(st.session_state.answer,st.session_state.requirement,st.session_state.lastmessage).replace('\\n', '\n').replace('\\t', '\t')
            st.markdown(questions)
            st.session_state.messages.append({"role": "agent", "content": questions})

with st.sidebar:
    with st.container(border=True):
        st.components.v1.html(st.session_state.filledform,height=300)
    st.code(st.session_state.answer,language="json")