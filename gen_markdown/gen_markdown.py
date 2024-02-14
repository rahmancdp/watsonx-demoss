import streamlit as st

from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

import os
from dotenv import load_dotenv

load_dotenv()

api_key = st.secrets["API_KEY"]
project_id = st.secrets["PROJECT_ID"]

api_key = os.getenv("API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

creds = {
    "url"    : "https://us-south.ml.cloud.ibm.com",
    "apikey" : api_key
}

params = {
    GenParams.DECODING_METHOD:"greedy",
    GenParams.MAX_NEW_TOKENS:1000,
    GenParams.MIN_NEW_TOKENS:1,
    GenParams.TOP_K:50,
    GenParams.TOP_P:1,
    # GenParams.STOP_SEQUENCES:['"}','\n\n'],
}

llmllama = Model("meta-llama/llama-2-70b-chat",creds, params, project_id)

def buildprompt(query):
    return f"""[INST]generate a table with {query}
    -generate 5 role of random data.
    -output in markdown table.
[/INST]
markdown table:"""

def gentable(query):
    prompts = [buildprompt(query)]
    print(prompts)
    answer = ""
    for response in llmllama.generate_text(prompts):
        answer += response
    print(answer)
    return answer

st.header("Generate Markdown table by watsonx")

with st.sidebar:
    st.title("Generate Markdown table")

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
    with st.spinner(text="In progress...", cache=False):
        answer = gentable(query)

    st.session_state.messages.append({"role": "agent", "content": answer}) 
    with st.chat_message("agent"):
        st.markdown(answer)