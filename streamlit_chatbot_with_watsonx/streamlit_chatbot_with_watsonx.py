import os
from dotenv import load_dotenv
import streamlit as st

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=200,
    min_new_tokens=1,
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

memory = ConversationBufferMemory()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    llm = LangChainInterface(model="meta-llama/llama-2-7b-chat",credentials=creds, params=params)
    conversation = ConversationChain(llm=llm, memory=memory)
    response_text = conversation.run(prompt)

    st.session_state.messages.append({"role": "agent", "content": response_text})

    memory.chat_memory.add_user_message(prompt)
    memory.chat_memory.add_ai_message(response_text)

    with st.chat_message("agent"):
        st.markdown(response_text)
