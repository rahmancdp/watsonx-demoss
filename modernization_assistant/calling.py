# __copyright__ = "Copyright (C) 2023 IBM Client Engineering US FSM Squad 12 and IBM Consulting"
# __author__ = "Renate Hamrick, Boris Acha, Somenath Dutta and Ritu Patel"


import os
from ibm_watson_machine_learning.foundation_models import Model as GA_Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams 
# BAM
from genai.credentials import Credentials
from genai.model import Model as BAM_Model
from genai.schemas import GenerateParams
# from main import cobolParagraph
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv()) 
import sys 
sys.path.append('./') 

import warnings
warnings.filterwarnings('ignore')

# Load WML/Watsonx.ai variables
platform_type = os.environ['PLATFORM_TYPE']
wml_url = os.environ['WML_URL'] 
wml_api = os.environ['WML_API_KEY'] 
genai_proj_id = os.environ['WML_PROJECT_ID']
bam_url = os.environ['BAM_URL']
bam_api = os.environ['BAM_API_KEY']

if platform_type == "BAM":
    params = GenerateParams(
        decoding_method="greedy",
        max_new_tokens=4096,
        min_new_tokens=1,
        temperature=0.2,
        top_k=100,
        top_p=1
        )
    creds = Credentials(api_endpoint=bam_url, api_key=bam_api)
    model = BAM_Model('meta-llama/llama-2-70b-chat', params=params, credentials=creds)
else:
    creds = {
       "url": wml_url, 
       "apikey": wml_api
       }
    # watsonx.ai model parameters
    params = {
       GenParams.DECODING_METHOD: "greedy",
       GenParams.MIN_NEW_TOKENS: 1,
       GenParams.MAX_NEW_TOKENS: 4096,
       GenParams.TEMPERATURE: 0,
       GenParams.STOP_SEQUENCES: [],
       GenParams.REPETITION_PENALTY: 1
       }
    # Create watsonx.ai model
    model = GA_Model(model_id='meta-llama/llama-2-70b-chat', params=params, credentials=creds, project_id=genai_proj_id)

def call_watsonx(question, code_chunk, code_type, context):
     
    def make_prompt(code_chunk, question, code_type, context):
        # Define prompt, starting with the initial instructions for how we want watsonx.ai to behave.
        return (f"\n\nHello Watson! Please use your knowledge as a {code_type} developer and the {code_type} code I send you, to help me with the following tasks or question. Here is some context for some of the code: {context}"
                f"Code: \n {code_chunk} Question or tasks: {question} Watson answer: ")

    prompt = make_prompt(code_chunk, question, code_type, context)

    if platform_type == "BAM":
        response = model.generate([prompt])[0].generated_text
    else:
        # Send prompt to watsonx.ai
        response = model.generate_text(prompt)  
    print(context)
    return(response) 