import streamlit as st
# from code_editor import code_editor

# from pptx import Presentation
# from pptx.enum.lang import MSO_LANGUAGE_ID

# from docx import Document

from ibm_watsonx_ai.credentials import Credentials
from ibm_watsonx_ai.schemas import GenerateParams
from ibm_watsonx_ai.model import Model

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

# llmstarcoder = Model(model="bigcode/starcoder",credentials=creds, params=params)
model = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

# Convert the XML to json

def buildpromptforxmltojson(xml):
    return f"""[INST]<<SYS>>convert the xml provide in backquote to json format.
    notes:
    - dont show id attributes.
    - dont show doc:id attributes.
    - dont show Note at the end.
    - generate the json directly only.
    <<SYS>>
    xml:```{xml}```[/INST]
    json:"""

def convert_xml_to_json(xmlfile):
    xml = xmlfile

    prompt = buildpromptforxmltojson(xml)

    for response in model.generate([prompt]):
        return response.generated_text
    
def buildpromptforxmltonamevaluepair(xml):
    return f"""[INST]<<SYS>>convert the xml provide in backquote to name, value csv format.\n
    dont show id attributes.\n
    generate the csv directly only.\n
    <<SYS>>\n
    xml:```{xml}```[/INST]\n
    csv:"""

def convert_xml_to_name_value_pair(xmlfile):
    xml = xmlfile

    prompt = buildpromptforxmltonamevaluepair(xml)

    for response in model.generate([prompt]):
        return response.generated_text
    
def generate_mmap(xml,fact):
    prompt = f'''[INST]
    <<SYS>>
    base on the fact in backquote and mulesoft xml in backquote generate a mmap file:
    mulesoft:`{xml}`
    fact:`{fact}`
    <<SYS>>
    [/INST]
    mmap in xml:'''

    for response in model.generate([prompt]):
        return response.generated_text

def generate_iflw(fact):
    prompt = f'''[INST]
    <<SYS>>
    base on the fact in backquote, generate a iflw file:
    `{fact}`
    <<SYS>>
    [/INST]
    iflw in xml:'''

    for response in model.generate([prompt]):
        return response.generated_text

temp_dir = tempfile.TemporaryDirectory()

st.set_page_config(layout="wide")
st.header("api migrator powered by watsonx")

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

with st.sidebar:
    st.title("API Migrator")
    st.markdown('- use case#1: extract information from mulesoft XML')
    st.markdown('- Use case#2: build SAP CPI package scaffolder from fact sheet')
    st.markdown('- Use case#3 - Generate Technical Spec from SAP CPI')

if "xmlstring" not in st.session_state:
    st.session_state.xmlstring = ""
if "jsonstring" not in st.session_state:
    st.session_state.jsonstring = ""
if "csvstring" not in st.session_state:
    st.session_state.csvstring = ""
if "mmapstring" not in st.session_state:
    st.session_state.mmapstring = ""
if "iflwstring" not in st.session_state:
    st.session_state.iflwstring = ""
    
uploaded_file = st.file_uploader(label="upload a xml file",type=['xml'])
if uploaded_file is not None:
    st.write("filename:", uploaded_file.name)
    with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
        f.write(uploaded_file.getbuffer())

        st.session_state.xmlstring = uploaded_file.read().decode()
        
        colxml, coljson = st.columns(2)
        with colxml:
            sourcesystem = st.selectbox(
                'What source system you want to migrate?',
                ('mulesoft',))
            st.code(st.session_state.xmlstring,language='xml') 
        
        with coljson:
            genjsonbutton = st.button('generate JSON')
            if genjsonbutton:
                with st.spinner(text="In progress...", cache=False):
                    st.session_state.jsonstring = convert_xml_to_json(st.session_state.xmlstring[0:4000])
            st.code(st.session_state.jsonstring,language='json')
 
            gencsvbutton = st.button('generate CSV')
            if gencsvbutton:
                with st.spinner(text="In progress...", cache=False):
                    st.session_state.csvstring = convert_xml_to_name_value_pair(xmlstring[0:4000])
            st.code(st.session_state.csvstring,language='csv')

            genmmapbutton = st.button('generate MMAP')
            if genmmapbutton:
                with st.spinner(text="In progress...", cache=False):
                    st.session_state.mmapstring = generate_mmap(st.session_state.xmlstring[0:4000],"")
            st.code(st.session_state.mmapstring,language='xml')

            geniflwbutton = st.button('generate iflow')
            if geniflwbutton:
                with st.spinner(text="In progress...", cache=False):
                    st.session_state.iflwstring = generate_iflw(st.session_state.jsonstring[0:4000])
            st.code(st.session_state.iflwstring,language='xml')