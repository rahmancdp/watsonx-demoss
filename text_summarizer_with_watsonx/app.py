import os
from dotenv import load_dotenv
import streamlit as st

from langchain.llms.openai import OpenAI

from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain

st.title('LangChain Text Summariser with Watsonx')

from genai.credentials import Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="sample",
    max_new_tokens=100,
    min_new_tokens=1,
    stream=False,
    temperature=0.5,
    top_k=50,
    top_p=1
).dict()

source_text = st.text_area("Source Text",height=200)

if st.button("Summarize"):
    if not source_text.strip():
        st.write(f"Please complete the missing fields")
    else:
        text_splitter = CharacterTextSplitter()
        texts = text_splitter.split_text(source_text)

        docs = [Document(page_content=t) for t in texts[:3]]

        llm = LangChainInterface(model="google/flan-ul2",credentials=creds, params=params)
        chain = load_summarize_chain(llm,chain_type="map_reduce")
        summary = chain.run(docs)
        st.write(summary)