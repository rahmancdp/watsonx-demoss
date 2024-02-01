import streamlit as st
# from code_editor import code_editor

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
    max_new_tokens=4000,
    min_new_tokens=1,
    # stream=True,
    top_k=50,
    top_p=1,
    stop_sequences=['```'],
)

llmstarcoder = Model(model="bigcode/starcoder",credentials=creds, params=params)
llmllama = Model(model="mistralai/mistral-7b-instruct-v0-2",credentials=creds, params=params)
# llmllama = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

def buildpromptforconvert(code,sourcelang,targetlang):
    return f"""Assume you are an expert both in {sourcelang} and {targetlang}. The code below is in {sourcelang}. Please re-write in the {targetlang} language, keeping the same logic. Replace functions from {sourcelang} with the equivalent in {targetlang} that makes the most sense. 

### {sourcelang} Code:
```{code}```

Please re-write the code above in {targetlang} language. 

Here are the requirements:

1. Indicate the parent class when you define a public class.
2. The original code can be a snippet from complete code base. 
3. If some classes are not provided in the given code snippet, import them from external packages. 
4. Mark with comments if things may not be correct through direct conversion or things can be missing.
5. Make sure the code concise, brief and elegant.
6. Import {targetlang} classes as few as possible. If necessary use ".*" to represent multiple classes.

### {targetlang} code:
```java"""

def buildpromptfordocumentation(code,sourcelang):
    return f"""[INST]you are java expert that help to write comprehensive documentation.
please generate documentation for the {sourcelang} source code in backquoted.
1. describe the class and properties
2. describe the constructors
3. describe the methods
<<SYS>>
`{code}`
<<SYS>>
[/INST]
documentation in markdown:"""

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
    for response in llmllama.generate_async(prompts,ordered=True):
        if response is not None:
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
        if response is not None:
            documentation += response.generated_text
    return documentation

temp_dir = tempfile.TemporaryDirectory()

st.set_page_config(layout="wide")

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

st.header("code assistant demo by watsonx")

if "incode" not in st.session_state:
    st.session_state.incode = ""
if "outcode" not in st.session_state:
    st.session_state.outcode = ""
if "outdoc" not in st.session_state:
    st.session_state.outdoc = ""

with st.sidebar:
    st.title("code assistant demo by watsonx")
    uploaded_file = st.file_uploader(label="upload a source code file",type=['cs','java','py','c','cpp'])
    if uploaded_file is not None:
        st.write("filename:", uploaded_file.name)
        with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
            st.session_state.incode = uploaded_file.read().decode()
    sourcelang = st.selectbox(
        'What program language you want to convert from?',
        ('csharp','java', 'python'))
    convertbutton = st.button("convert")
    targetlang = st.selectbox(
        'What program language you want to convert to?',
        ('java', 'c#', 'python'))
    docbutton = st.button("generate documentation")

st.code(st.session_state.incode,language=sourcelang)
# code_editor(st.session_state.incode, lang=sourcelang)

if convertbutton:
    # st.write(sourcecode['text'])
    with st.spinner(text="In progress...", cache=False):
        st.session_state.outcode = codeconvert(st.session_state.incode,sourcelang,targetlang)
st.code(st.session_state.outcode,language=targetlang)

if docbutton:
    with st.spinner(text="In progress...", cache=False):
        st.session_state.outdoc = codedocumentation(st.session_state.incode,'c#')
st.markdown(st.session_state.outdoc)