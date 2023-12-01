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

with st.sidebar:
    st.title("API Migrator")
    st.markdown('- use case#1: extract information from mulesoft XML')
    st.markdown('- Use case#2: build SAP CPI package scaffolder from fact sheet')
    st.markdown('- Use case#3 - Generate Technical Spec from SAP CPI')



jsonstring = ''
csvstring = ''
mmapstring = ''
iflwstring = ''
    
uploaded_file = st.file_uploader(label="upload a xml file",type=['xml'])
if uploaded_file is not None:
    st.write("filename:", uploaded_file.name)
    with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
        f.write(uploaded_file.getbuffer())

        xmlstring = uploaded_file.read().decode()
        
        colxml, coljson = st.columns(2)
        with colxml:
            sourcesystem = st.selectbox(
                'What source system you want to migrate?',
                ('mulesoft',))
            st.code(xmlstring,language='xml') 
        
        with coljson:
            genjsonbutton = st.button('generate JSON')
            if genjsonbutton:
                with st.spinner(text="In progress...", cache=False):
                    jsonstring = convert_xml_to_json(xmlstring[0:4000])
            st.code(jsonstring,language='json')
 
            gencsvbutton = st.button('generate CSV')
            if gencsvbutton:
                with st.spinner(text="In progress...", cache=False):
                    csvstring = convert_xml_to_name_value_pair(xmlstring[0:4000])
            st.code(csvstring,language='csv')

            genmmapbutton = st.button('generate MMAP')
            if genmmapbutton:
                with st.spinner(text="In progress...", cache=False):
                    mmapstring = generate_mmap(xmlstring[0:4000],"")
            st.code(mmapstring,language='xml')

            geniflwbutton = st.button('generate iflow')
            if geniflwbutton:
                with st.spinner(text="In progress...", cache=False):
                    iflwstring = generate_iflw(jsonstring[0:4000])
            st.code(iflwstring,language='xml')