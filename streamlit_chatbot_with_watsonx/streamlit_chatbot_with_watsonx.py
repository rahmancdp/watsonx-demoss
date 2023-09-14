import os
from dotenv import load_dotenv
import streamlit as st

from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.model import Model

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=200,
    min_new_tokens=1,
    stream=False,
    temperature=0.7,
    top_k=50,
    top_p=1,
    stop_sequences= ["Human:","AI:"],
)

with st.sidebar:
    st.title("watsonx Streamlit")
    st.write("call watsonx.ai")
    st.write("call watsonx Assistant")

st.title("it is a demo chatbot with watsonx")

with st.chat_message("system"):
    st.write("Hello 👋, lets chat with watsonx")

if "messages" not in st.session_state:
    st.session_state.messages = []

llm = Model(model="meta-llama/llama-2-7b-chat",credentials=creds, params=params)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response_text = llm.generate([prompt])
    answer = ""
    for response in response_text:
        answer += response.generated_text

    st.session_state.messages.append({"role": "agent", "content": answer}) 

    with st.chat_message("agent"):
        st.markdown(answer)
