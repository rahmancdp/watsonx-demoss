import streamlit as st
from code_editor import code_editor

from pptx import Presentation
from pptx.enum.lang import MSO_LANGUAGE_ID

from docx import Document

from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.model import Model

import tempfile
import pathlib
import re

import os
from dotenv import load_dotenv

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
    # stream=True,
    top_k=50,
    top_p=1
)

llmstarcoder = Model(model="bigcode/starcoder",credentials=creds, params=params)
llmllama = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

def buildpromptforconvert(code,sourcelang,targetlang):
    return f"""translate the following code from {sourcelang} to {targetlang}:
{sourcelang}:
{code}
{targetlang}:"""

def buildpromptfordocumentation(code,sourcelang):
    return f"""[INST]
please generate documentation for the {sourcelang} source code in backquoted
<<SYS>>
`{code}`
<<SYS>>
[/INST]
documentation:"""

def codeconvert(incode,sourcelang,targetlang):
    #chunking
    chunk_size = len(incode)//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptforconvert(chunk,sourcelang,targetlang)]
    code = ""
    for response in llmstarcoder.generate_async(prompts,ordered=True):
        code += response.generated_text
    return code

def codedocumentation(incode,sourcelang):
    #chunking
    chunk_size = len(incode)//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptfordocumentation(chunk,sourcelang)]
    documentation = ""
    for response in llmllama.generate_async(prompts,ordered=True):
        documentation += response.generated_text
    return documentation

temp_dir = tempfile.TemporaryDirectory()

st.set_page_config(layout="wide")
st.header("code helper powered by watsonx")

incode = ""
outcode = ""
outdocumenation = ""

colsource, colconvert, coldocumentation = st.columns(3)

with colsource:
    uploaded_file = st.file_uploader(label="upload a source code file",type=['cs','java','py','c','cpp'])
    if uploaded_file is not None:
        st.write("filename:", uploaded_file.name)
        with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
            incode = uploaded_file.read().decode()
    sourcelang = st.selectbox(
        'What program language you want to convert from?',
        ('csharp','java', 'python'))
    sourcecode = st.code(incode,language=sourcelang)
    # sourcecode = code_editor(incode, lang=sourcelang)

with colconvert:
    convertbutton = st.button("convert")
    targetlang = st.selectbox(
        'What program language you want to convert to?',
        ('java', 'csharp', 'python'))
    if convertbutton:
        # st.write(sourcecode['text'])
        with st.spinner(text="In progress...", cache=False):
            outcode = codeconvert(incode,sourcelang,targetlang)
        st.code(outcode,language=targetlang)

with coldocumentation:
    docbutton = st.button("generate documentation")
    if docbutton:
        with st.spinner(text="In progress...", cache=False):
            outdocumenation = codedocumentation(incode,sourcelang)
        st.write(outdocumenation)