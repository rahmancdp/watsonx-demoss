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
llmllama = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

context = '''table:
cs_customers (
 c_id int
 c_name varchar
)
cs_products (
 p_id int
 p_name varchar
 p_price float
 p_SKU varchar
)
cs_orders (
 o_id int
 c_id int
 p_id int
 o_date datetime)'''

def buildpromptforquery(query,context):
    return f"""[INST]
please generate SQL for following query in backquoted
<<SYS>>
query:`{query}`
context:`{context}`
<<SYS>>
[/INST]
SQL:"""

def querytosql(query,context):
    prompts = [buildpromptforquery(query,context)]
    SQL = ""
    for response in llmllama.generate_async(prompts,ordered=True):
        SQL += response.generated_text
    return SQL

temp_dir = tempfile.TemporaryDirectory()

# st.set_page_config(layout="wide")
st.header("SQL assistant powered by watsonx")

with st.sidebar:
    st.title("SQL assistant")
    st.write("SQL-to-SQL migration (TODO)")
    st.write("Text-to-SQL generation")
    st.write("SQL-to-Text understanding (TODO)")
    st.write(f"table context {context}")

with st.chat_message("system"):
    st.write("please input your query")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("your query"):
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({"role": "user", "content": query})

    answer = querytosql(query,context)

    st.session_state.messages.append({"role": "sql assistant", "content": answer}) 

    with st.chat_message("sql assistant"):
        st.markdown(answer)