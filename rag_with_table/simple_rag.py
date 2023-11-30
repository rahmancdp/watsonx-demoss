import logging
import os
import pickle
import tempfile

import streamlit as st
from dotenv import load_dotenv

from genai.extensions.langchain import LangChainInterface
from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.model import Model

from langchain.callbacks import StdOutCallbackHandler
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import (HuggingFaceHubEmbeddings,
                                  HuggingFaceInstructEmbeddings)
from typing import Literal, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS, Chroma
from PIL import Image
from sentence_transformers import SentenceTransformer

from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np
# Most GENAI logs are at Debug level.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

st.set_page_config(
    page_title="Retrieval Augmented Generation",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.header("Retrieval Augmented Generation with watsonx.ai 💬")
# chunk_size=1500
# chunk_overlap = 200

load_dotenv()

load_dotenv()

api_key = st.secrets["GENAI_KEY"]
api_endpoint = st.secrets["GENAI_API"]

api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

handler = StdOutCallbackHandler()

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=1000,
    min_new_tokens=1,
    # stream=True,
    top_k=50,
    top_p=1
)

# Sidebar contents
with st.sidebar:
    st.title("RAG App")
    st.markdown('''
    ## About
    This app is an LLM-powered RAG built using:
    - [IBM Generative AI SDK](https://github.com/IBM/ibm-generative-ai/)
    - [HuggingFace](https://huggingface.co/)
    - [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai) LLM model
 
    ''')
    st.write('Powered by [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai)')
    # image = Image.open('/Users/buckylee/Documents/github/Incubation_watsonx_Chinese/lab06a_Building Question-Answering with watsonx.ai and Streamlit with Retrieval Augmented Generation (Transient)/watsonxai.jpg')
    # st.image(image, caption='Powered by watsonx.ai')
    max_new_tokens= st.number_input('max_new_tokens',1,1024,value=300)
    min_new_tokens= st.number_input('min_new_tokens',0,value=15)
    repetition_penalty = st.number_input('repetition_penalty',1,2,value=2)
    decoding = st.text_input(
            "Decoding",
            "greedy",
            key="placeholder",
        )
    
uploaded_files = st.file_uploader("Choose a PDF file", accept_multiple_files=True)

@st.cache_data
def read_pdf(uploaded_files,chunk_size =250,chunk_overlap=20):
    for uploaded_file in uploaded_files:
      bytes_data = uploaded_file.read()
      with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
      # Write content to the temporary file
          temp_file.write(bytes_data)
          filepath = temp_file.name
          with st.spinner('Waiting for the file to upload'):
             loader = PyPDFLoader(filepath)
             data = loader.load()
             text_splitter = RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap=chunk_overlap)
             docs = text_splitter.split_documents(data)
             return docs

@st.cache_data
def read_push_embeddings():
    # embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = HuggingFaceEmbeddings()
    if os.path.exists("db.pickle"):
        with open("db.pickle",'rb') as file_name:
            db = pickle.load(file_name)
    else:     
        db = FAISS.from_documents(docs, embeddings)
        with open('db.pickle','wb') as file_name  :
             pickle.dump(db,file_name)
        st.write("\n")
    return db

# show user input
if user_question := st.text_input(
    "Ask a question about your Policy Document:"
):
    docs = read_pdf(uploaded_files)
    db = read_push_embeddings()
    docs = db.similarity_search(user_question)
    params = GenerateParams(
        decoding_method="greedy",
        max_new_tokens=1000,
        min_new_tokens=1,
        # stream=True,
        top_k=50,
        top_p=1
    )

    model = LangChainInterface(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)
    chain = load_qa_chain(model, chain_type="stuff")

    response = chain.run(input_documents=docs, question=user_question)

    st.text_area(label="Model Response", value=response, height=100)
    st.write()