import streamlit as st
# from code_editor import code_editor

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

import javalang

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
    top_p=1,
    stop_sequences=["''''","end of code"],
)

llmstarcoder = Model(model="bigcode/starcoder",credentials=creds, params=params)
llmllama = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

def buildpromptforrefactor(code,sourcelang):
    return f"""[INST]as java developer, update the following {sourcelang} code in backquoted base on following rules:
<<SYS>>
notes:
- provide the problem and review comment only
- end the generation with <end-of-code>
- review only base on following rules:
rule 1. include transaction to class and method:
example: 
//添加事务
@Transactional(rollbackFor = Exception.class)
rule 2. put log of function input variable in the first line of function:
example:
//打印参数
public Result<TokenVo> login(@RequestBody @Valid LoginForm record) {{
        log.info("/hqActivityTemplateAuth/login 请求:{{}}", record);
<<SYS>>
target code:
`{code}`
[/INST]
rewrited version:"""

def buildpromptforrefactor2(code,sourcelang):
    return f"""[INST]as java developer, rewrite the following {sourcelang} code in backquoted with following rules:
<<SYS>>
notes:
- provide the problem and review comment only
- end the generation with <end-of-code>
- review only base on following rules:
rule 1. controller should not just return object:
bad example:
JsonResultVo<Object>
rule 2. use enum instead of number value:
bad example:
switch (queryVo.getQueryType()) {{
            case "1":
}}
good example:
switch (queryVo.getQueryType()) {{
            case queryVo.MEANING_FUL_NAME:
}}
rule 3. include transaction:
example: 
//添加事务
@Transactional(rollbackFor = Exception.class)
rule 4. should not return hashmap:
example:
List<HashMap> queryUserAnswerDetails();
rule 5. exception related log should exception information.
rule 6. put log of function input variable in the first line of function:
example:
//打印参数
public Result<TokenVo> login(@RequestBody @Valid LoginForm record) {{
        log.info("/hqActivityTemplateAuth/login 请求:{{}}", record);
<<SYS>>
target code:
`{code}`
[/INST]
rewrited version:"""

def buildpromptforreview(code,sourcelang):
    return f"""[INST]
as solution architect, please do code review for the {sourcelang} source code in backquoted
<<SYS>>
notes:
- provide the problem and review comment only
- end the generation with <end-of-code>
- review only base on following rules:
rule 1. controller should not just return object:
bad example:
JsonResultVo<Object>
rule 2. use enum instead of number value:
bad example:
switch (queryVo.getQueryType()) {{
            case "1":
}}
good example:
switch (queryVo.getQueryType()) {{
            case queryVo.MEANING_FUL_NAME:
}}
rule 3. include transaction:
example: 
@Transactional(rollbackFor = Exception.class)
rule 4. should not return hashmap:
example:
List<HashMap> queryUserAnswerDetails();
rule 5. exception related log should exception information.
rule 6. put log of function input variable in the first line of function:
example:
public Result<TokenVo> login(@RequestBody @Valid LoginForm record) {{
        log.info("/hqActivityTemplateAuth/login 请求:{{}}", record);

target code:
`{code}`
<<SYS>>
[/INST]
review:"""

def codesplit(incode,sourcelang):
    prompts = f"""
extract the method declaration and body in following java code in backquoted:
`{incode}`
method delaration and bodys:
    """
    review = ""
    for response in llmstarcoder.generate(prompts):
        review += response.generated_text
    return review

def coderefactor(incode,sourcelang):
    #chunking
    chunk_size = 500
    #//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptforrefactor(chunk,sourcelang)]
    code = ""
    for response in llmllama.generate_async(prompts,ordered=True):
        if response is not None:
            code += response.generated_text
    return code

def codereview(incode,sourcelang):
    #chunking
    chunk_size = len(incode)//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptforreview(chunk,sourcelang)]
    review = ""
    for response in llmllama.generate_async(prompts,ordered=True):
        review += response.generated_text
    return review

temp_dir = tempfile.TemporaryDirectory()

st.set_page_config(layout="wide")
st.header("code quality assistant powered by watsonx")

incode = ""
outcode = ""
outdocumenation = ""

colsource, colreview, colrefactor = st.columns(3)

with colsource:
    uploaded_file = st.file_uploader(label="upload a java source code file",type=['java'])
    if uploaded_file is not None:
        st.write("filename:", uploaded_file.name)
        with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
            incode = uploaded_file.read().decode()
    sourcelang = st.selectbox(
        'What program language you want to review?',
        ('java',))
    sourcecode = st.code(incode,language=sourcelang)
    # sourcecode = code_editor(incode, lang=sourcelang)

with colreview:
    reviewbutton = st.button("review")
    if reviewbutton:
        with st.spinner(text="In progress...", cache=False):
            outreview = codereview(incode,sourcelang)
        st.write(outreview)

with colrefactor:
    splitbutton = st.button("split")
    if splitbutton:
        with st.spinner(text="In progress...", cache=False):
            outcode = codesplit(incode,sourcelang)
        st.code(outcode,language=sourcelang)

    refactorbutton = st.button("refactor")
    if refactorbutton:
        with st.spinner(text="In progress...", cache=False):
            outcode = coderefactor(incode,sourcelang)
        st.code(outcode,language=sourcelang)