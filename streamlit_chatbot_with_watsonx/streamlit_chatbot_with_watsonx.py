import os
from dotenv import load_dotenv
import streamlit as st

from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=200,
    min_new_tokens=30,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1
).dict()

with st.sidebar:
    st.title("watsonx Streamlit")
    st.write("call watsonx.ai")
    st.write("call watsonx Assistant")

st.title("it is a demo chatbot with watsonx")

with st.chat_message("system"):
    st.write("Hello 👋, lets chat with watsonx")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    docs = [Document(page_content=prompt)]

    llm = LangChainInterface(model="meta-llama/Llama-2-7b",credentials=creds, params=params)
    chain = load_summarize_chain(llm,chain_type="map_reduce")
    response_text = chain.run(docs)

    st.session_state.messages.append({"role": "system", "content": response_text})

    with st.chat_message("system"):
        st.markdown(response_text)
