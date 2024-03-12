import streamlit as st
import subprocess

from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.extensions.langchain import WatsonxLLM

import pandas as pd
import tempfile
import pathlib

def split_smaller(text):
    return text

# from modernization_assistant.code_sample.assemblerCode import split_assem_code, clean_assem_code
# from javaCode import split_java_code
# from code_sample.cobolCode import split_smaller
from docx import Document

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

creds = {
    "url"    : "https://us-south.ml.cloud.ibm.com",
    "apikey" : api_key
}

params = {
    GenParams.DECODING_METHOD:"greedy",
    GenParams.MAX_NEW_TOKENS:4000,
    GenParams.MIN_NEW_TOKENS:1,
    GenParams.TOP_K:50,
    GenParams.TOP_P:1,
    GenParams.STOP_SEQUENCES:['```'],
}

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


llmmistra = Model("ibm-mistralai/mixtral-8x7b-instruct-v01-q",creds, params, project_id)
# llmllama = Model("ibm/granite-13b-instruct-v2",creds, params, project_id)
llmllama = Model("meta-llama/llama-2-70b-chat",creds, params, project_id)

def generate_funcspec(pseudocode, funcspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of pseudo code from mainframe, \
        please summary the psudo code provide and generate a functional specification:
        -generate functional specific in markdown
        -read into the  funcspec provided in detail.
        -structure the technical specification as unit of each servcie
        -for each service, propose the service name
        -for each service, identify the input and output
        -for each service, identify the key processes
        -for each service, identify the journal
        -generate in concise, clear, professional style.
            <<SYS>>
            pseudo code: `{pseudocode}`
            funcspec: `{funcspec}`
            <</SYS>>
            [/INST]summary:```"""
    prompt = f"""[INST]you be expert on banking system. please summarize the psudo code in backquoted:
        -read into the pseudo code in detail.
        -generate the summary on top of the previous summary provided if any.
        -identify potential service in the pseudo code.
        -for each input identified, describe the purpose, format and potential data source. generate in layout of input name - (format) (purpose) (potential data source)
        -for each output identified, describe the purpose, format and potential usage.
        -for each process identified, provide the programming logic.
            <<SYS>>
            pseudo code: `{pseudocode}`
            previous summary: `{funcspec}`
            <</SYS>>
            [/INST]summary:```"""
    print("$$$$"+prompt)
    paragraph = ""
    for response in llmllama.generate_text(prompt):
        paragraph += response
    print(paragraph)
    return paragraph

def split_string(string, chunk_size):
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]

def generate_factsheet(factsheet, category, funcspec):

    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a factsheet that include essential information from the factsheet:
        -merge to the factsheet provided.
        -generate factsheet in json
        -the funcspec is about `{category}`.
        -generate the factsheet only, dont show notes.
            <<SYS>>
            factsheet: `{factsheet}`
            funcspec: `{funcspec}`
            <</SYS>>
            [/INST]factsheet in json:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_inputfunction(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java Value Object class that implement the input requirement:
        -validate the datatype, length, mandatory/optional and other requriement of the field.
        -the value should be captured from OBN table, OBN field.
        -the value should be captured from Requirement Screen.
        -be aware of CUR, FEX, and other requriement of the field.
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

raml_style = """#%RAML 1.0
title:
version:
baseUri:

/[servicename]:
  [get or post]:
    description: 
    queryParameters:
      [field name]:
        displayName:
        type:
        description:
        example: 
        required: 
        maxLength: 
        minLength:
    body:
      application/json:
        type: |
          {
              "type": "object",
              "$schema": "http://json-schema.org/draft-03/schema",
              "id": "http://jsonschema.net",
              "required": true,
              "properties": {
                "[field name]": {
                  "type": ,
                  "description": ,
                  "minLength": ,
                  "maxLength": ,
                },
                "[field name]": {
                  "type": "object",
                  "properties": {
                    "[property name]": {
                      "type": ,
                      "description": ,
                      "max": 
                      "min":
                    },
                    "[property name]": {
                      "type": ,
                      "description": ,
                    },
                    "[property name]": {
                      "type": ,
                      "description": ,
                      "maxLength": ,
                      "minLength": ,
                    },
                }
            }
        }
    }
    responses:
      [response code]:
        body:
          application/json:
            type: |
              {
                  "type": "object",
                  "$schema": "http://json-schema.org/draft-03/schema",
                  "id": "http://jsonschema.net",
                  "required": true,
                  "properties": {
                    "[property name]": {
                      "type": ,
                      "description": ,
                      "minLength": ,
                      "maxLength": 
                    },
                    "[property name]": {
                      "type": "object",
                      "properties": {
                        "[property name]": {
                          "type":  ,
                          "description": ,
                          "max": 
                        },
                        "[property name]": {
                          "type": ,
                          "description": 
                        },
                        "[property name]": {
                          "type": ,
                          "description": ,
                          "maxLength": ,
                          "minLength": 
                        },
                      }
                    }
                  }
              }"""

def generate_inputfunction_raml(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the input requirement:
        -validate the datatype, length, mandatory/optional and other requriement of the field.
        -the value should be captured from OBN table, OBN field.
        -the value should be captured from Requirement Screen.
        -be aware of CUR, FEX, and other requriement of the field.
        -follow the raml style, replace the bracket name with coreponding name.
        -generate the raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_swagger(raml):
    prompt = f"""[INST]you are an expert on raml and swagger. please translate the raml to swagger.
            <<SYS>>
            raml: `{raml}`
            <</SYS>>
            [/INST]swagger json:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_outputfunction(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java Value Object class that implement the output requirement:
        -validate the datatype, length of the field.
        -the value should be captured from OBN table, OBN field.
        -the value should be captured from Requirement Screen.
        -be aware of CUR, FEX, and other requriement of the field.
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_outputfunction_raml(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a raml that implement the output requirement:
        -validate the datatype, length of the field.
        -the value should be captured from OBN table, OBN field.
        -the value should be captured from Requirement Screen.
        -be aware of CUR, FEX, and other requriement of the field.
        -follow the raml style, replace the bracket name with coreponding name.
        -generate raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_processfunction(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java class that implement the process requirement:
        -include the steps mention in remarks.
        -for each step, create a method.
        -take care condition if any.
        -leverage related domains.
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_processfunction_raml(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the process requirement:
        -include the steps mention in remarks.
        -for each step, create a method.
        -take care condition if any.
        -leverage related domains.
        -follow the raml style, replace the bracket name with coreponding name.
        -generate raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_journalfunction(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java class that implement the journal requirement:
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_journalfunction_raml(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the journal requirement:
        -follow the raml style, replace the bracket name with coreponding name.
        -generate the raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_screenfunction(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate a java class that implement the screen requirement:
        -generate the java class only, dont show notes.
            <<SYS>>
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]java:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def generate_screenfunction_raml(dffuncspec):
    prompt = f"""[INST]you are a system analyist with good knowledge of functional specification extracted from mainframe, \
        please generate raml that implement the screen requirement:
        -follow the raml style, replace the bracket name with coreponding name.
        -generate raml only, dont show notes.
            <<SYS>>
            raml style: `{raml_style}`
            pseudo code: `{dffuncspec.to_csv()[:3000]}`
            <</SYS>>
            [/INST]raml:```"""
    print("$$$$"+prompt)
    answer = ""
    for response in llmllama.generate_text(prompt):
        answer += response
    print(answer)
    return answer

def save_to_excel(excel_file_path, summary):
    # Create a DataFrame with the data you want to write
    data = {
        'Name': ['John', 'Jane', 'Alice'],
        'Age': [25, 30, 28],
        'City': ['New York', 'London', 'Paris']
    }
    df = pd.DataFrame(data)

    # Open the Excel file for writing
    with pd.ExcelWriter(excel_file_path, mode='a') as writer:
        # Check if the sheet already exists
        if 'Sheet1' in writer.sheets:
            # Get the existing sheet
            existing_sheet = writer.sheets['Sheet1']

            # Find the last row in the existing sheet
            last_row = existing_sheet.max_row

            # Write the DataFrame to the existing sheet, starting from the last row
            df.to_excel(writer, sheet_name='Sheet1', startrow=last_row, header=False, index=False)
        else:
            # Write the DataFrame to a new sheet
            df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Get the workbook and the worksheet
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Find and replace placeholders in the worksheet
        find_replace = {
            '<NAME>': 'John',
            '<AGE>': '25',
            '<CITY>': 'New York'
        }
        for find, replace in find_replace.items():
             worksheet.cells().replace(find, replace)

        # Save the changes to the Excel file
        writer.save()

def buildpromptforconvertpseudocode(pseudocode):
    return f"""Assume you are an expert both in java. 
    The code below is in Pseudo Code. 
    Please re-write in the java language, keeping the same logic.
    ### Pseudo Code:
    ```{pseudocode}```

    Please re-write the code above in java language. 

    Here are the requirements:

    1. Indicate the parent class when you define a public class.
    2. The original code can be a snippet from complete code base. 
    3. If some classes are not provided in the given code snippet, import them from external packages. 
    4. Mark with comments if things may not be correct through direct conversion or things can be missing.
    5. Make sure the code concise, brief and elegant.
    6. Import java classes as few as possible. If necessary use ".*" to represent multiple classes.

    ### java code:
    ```java"""

def convertpseudocodetojava(incode):
    #chunking
    chunks = split_smaller(incode)

    prompts = []
    for chunk in chunks:
        print(len(chunk))
        prompts += [buildpromptforconvertpseudocode(chunk)]
    code = ""
    for response in llmllama.generate_text(prompts):
        if response is not None:
            code += response
    return code

def buildpromptforconvert(code):
    return f"""Assume you are an expert both in COBOL and java. The code below is in COBOL. Please re-write in the java language, keeping the same logic. Replace functions from COBOL with the equivalent in java that makes the most sense. 

### COBOL Code:
```{code}```

Please re-write the code above in java language. 

Here are the requirements:

1. Indicate the parent class when you define a public class.
2. The original code can be a snippet from complete code base. 
3. If some classes are not provided in the given code snippet, import them from external packages. 
4. Mark with comments if things may not be correct through direct conversion or things can be missing.
5. Make sure the code concise, brief and elegant.
6. Import java classes as few as possible. If necessary use ".*" to represent multiple classes.

### java code:
```java"""

def buildpromptforDDD(code):
    return f"""Assume you are an expert on java. The code below is in java. 
    Please re-write in the java language with DDD style, keeping the same logic. 

### java Code:
```{code}```

Please re-write the code above in java language with DDD style. 
- add function description with input/output
- add comment on complex logic block
- function name in pattern 'func_HSBC'+business+function name
- variable name in pattern 'var_'+business+variable name

### java code with DDD style:
```java"""

def buildpromptfordoc(code):
    return f"""[INST]
please generate documentation for the java source code in backquoted
<<SYS>>
`{code}`
<<SYS>>
[/INST]
documentation:"""

def buildpromptfortestcase(code):
    return f"""[INST]
please generate testcase in junit for the java source code in backquoted
- test for all conditional case
- test for all possible output
- test for all possible input
- test for exception catching
<<SYS>>
`{code}`
<<SYS>>
[/INST]
testcase:"""

def buildpromptforexplaination(code):
    return f"""[INST]you are expert on COBOL programming,
please explain the programming logic for the COBOL source code in backquoted.
- the explaination should show the logic of the code.
- the explaination should be well structure, easy to understand.
- the explaination should be ready for modernize to java language.
<<SYS>>
`{code}`
<<SYS>>
[/INST]
explaination:"""

def genexplaination(incode):
    #chunking
    chunks = split_smaller(incode)

    prompts = []
    for chunk in chunks:
        print(len(chunk))
        prompts += [buildpromptforexplaination(chunk)]
    code = ""
    for response in llmllama.generate_text(prompts):
        if response is not None:
            code += response
    print(code)
    return code

def convertcoboltojava(incode):
    #chunking
    chunks = split_smaller(incode)

    prompts = []
    for chunk in chunks:
        print(len(chunk))
        prompts += [buildpromptforconvert(chunk)]
    code = ""
    for response in llmllama.generate_text(prompts):
        if response is not None:
            code += response
    return code

def genDDD(incode):
    #chunking
    chunk_size = len(incode)//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptforDDD(chunk)]
    code = ""
    for response in llmllama.generate_text(prompts):
        if response is not None:
            code += response
    return code.replace("```","")

def gendoc(incode):
    #chunking
    chunk_size = len(incode)//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptfordoc(chunk)]
    doc = ""
    for response in llmllama.generate_text(prompts):
        if response is not None:
            doc += response
    return doc

def gentestcase(incode):
    #chunking
    chunk_size = len(incode)//4
    chunks = []
    for i in range(0, len(incode), chunk_size):
        chunks += [incode[i:i+chunk_size]]

    prompts = []
    for chunk in chunks:
        prompts += [buildpromptfortestcase(chunk)]
    testcase = ""
    for response in llmllama.generate_text(prompts):
        if response is not None:
            testcase += response
    return testcase

def querycodeanddoc(informations, question):
    prompt = f"""
    answer the question in 5 sentences base on the informations:
    informations:
    {informations}
    question:
    {question}
    answer in point form:"""

    prompts = [prompt]
    answer = ""
    for response in llmllama.generate_text(prompts):
        answer += response
    return answer

def save_to_word_doc(code, watson_response, prompt):
    doc_filename = "CodeExplain_Output.docx"

    # Check if the document file already exists
    if os.path.isfile(doc_filename):
        # If it exists, open the document
        doc = Document(doc_filename)
    else:
        # If it doesn't exist, create a new document
        doc = Document()

    # Add a new title with the current date and time
    doc.add_heading(f"CodeExplain Output - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", level=0)

    # Add input code
    doc.add_heading("Prompt", level=1)
    doc.add_paragraph(prompt)

    # Add Watson's response
    doc.add_heading("Watson's Response", level=1)
    doc.add_paragraph(watson_response)

    # Add input code
    doc.add_heading("Input Code", level=1)
    doc.add_paragraph(code)

    # Save the document
    doc.save(doc_filename)

temp_dir = tempfile.TemporaryDirectory()

st.set_page_config(layout="wide")

if "df" not in st.session_state:
    st.session_state.df = None
if "pseudocode" not in st.session_state:
    st.session_state.pseudocode = []
if "summary" not in st.session_state:
    st.session_state.summary = []
if "funcspec" not in st.session_state:
    st.session_state.funcspec = None
if "inputraml" not in st.session_state:
    st.session_state.inputraml = []
if "outputraml" not in st.session_state:
    st.session_state.outputraml = []
if "process" not in st.session_state:
    st.session_state.process = []
if "factsheet" not in st.session_state:
    st.session_state.factsheet = "{}"
if "raml" not in st.session_state:
    st.session_state.raml = ""
if "javaout" not in st.session_state:
    st.session_state.javaout = ""
if "javawithddd" not in st.session_state:
    st.session_state.javawithddd = ""
if "outdoc" not in st.session_state:
    st.session_state.outdoc = ""
if "explaination" not in st.session_state:
    st.session_state.explaination = ""

with st.sidebar:
    st.subheader("ModAssist powered by watsonx")

    uploaded_file = st.file_uploader(label="upload the Pseudo Code",type=['doc','docx'])
    if uploaded_file is not None:
        st.write("filename:", uploaded_file.name)
        with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
            # st.session_state.pseudocode = uploaded_file.read().decode("utf-8", errors="ignore")
            doc = Document(uploaded_file)
            page_content = []
            current_page = []

            for paragraph in doc.paragraphs:
                if paragraph.text:  # Skip empty paragraphs
                    current_page.append(paragraph.text)
                elif current_page:  # Store the current page if it's not empty
                    page_content.append("\n".join(current_page))
                    print("\n".join(current_page))
                    print("#####################")
                    current_page = []

            # Add the last page content if it exists
            if current_page:
                page_content.append("\n".join(current_page))
                print("\n".join(current_page))
                print("#####################")

        print(f"total page {len(page_content)}")
        st.session_state.pseudocode = page_content

    uploaded_file = st.file_uploader(label="upload the Functional Spec",type=['xls','xlsx'])
    if uploaded_file is not None:
        st.write("filename:", uploaded_file.name)
        with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
            st.session_state.funcspec = pd.read_excel(uploaded_file, sheet_name=None)

tabPseudoCodeToFuncSpec, tabFuncSpecToFactsheet, tabFuncSpecToRAML, tabRAMLToJava = st.tabs(['pseudocode to funcspec','funcspec to factsheet','funcspec to RAML','RAML to java'])

with tabPseudoCodeToFuncSpec:
    st.subheader(f"Pseudo Code to Functional Specification")

    # st.session_state.pseudocode = pseudocode_to_funcspec.read_docx('pseudocode/C101 As-Is readable v0.9 - Share to IBM.docx')
    funcspec = ""

    if st.button("Generate XLS"):
        data = {
            'Name': ['John', 'Jane', 'Alice'],
            'Age': [25, 30, 28],
            'City': ['New York', 'London', 'Paris']
        }
        st.session_state.df = pd.DataFrame(data)
        # save_to_excel('output/test.xlsx','testing testing')

    colpseudocode, colfuncspec = st.columns(2)
    
    with colpseudocode:
        dfpseudocode = pd.DataFrame(st.session_state.pseudocode)
        dfpseudocode = dfpseudocode.applymap(lambda x: x.replace('\n', '<br>'))

        dffuncspec = pd.DataFrame(st.session_state.summary)
        dffuncspec = dffuncspec.applymap(lambda x: x.replace('\n', '<br>'))

        dfall = pd.concat([dfpseudocode,dffuncspec], axis=1)

        st.markdown(dfall.to_html(escape=False), unsafe_allow_html=True)
        # st.dataframe(df)
        # st.markdown(st.session_state.pseudocode)
 
    with colfuncspec:
        st.dataframe(st.session_state.df)
    
        if st.button("Generate Functional Specification"):

            st.session_state.summary = []
            for code in st.session_state.pseudocode:
                if code.strip() == '':
                    continue
                chunks = split_string(code,3000)
                funcspec = ""
                for chunk in chunks:
                    answer = generate_funcspec(chunk,funcspec)
                    funcspec += answer
                
                st.session_state.summary.append(funcspec)
                st.markdown(funcspec)
                st.text("##########")

            # for page, text in enumerate(st.session_state.pseudocode, start=1):
            #     print(f"Page {page}:\n")
            #     st.markdown(funcspec)
                
with tabFuncSpecToFactsheet:
    st.subheader(f"Functional Specification to Factsheet")

    colfuncspec, colfactsheet = st.columns(2)
    with colfuncspec:

        # st.session_state.funcspec = pd.read_excel('funcspec/Functional Spec - Account Statement & Advice control service - Share to IBM.xlsx', sheet_name=None)
        if st.session_state.funcspec is not None:
            sheetnames = []
            for sheet_name, df in st.session_state.funcspec.items():
                sheetnames.append(sheet_name)

            tabs = st.tabs(sheetnames)
            tabindex = 0
            for sheet_name, df in st.session_state.funcspec.items():
                with tabs[tabindex]:
                    st.text(f"Sheet Name: {sheet_name}")
                    st.dataframe(df)
                    tabindex += 1
    
    with colfactsheet:
        if st.button("Generate Factsheet"):
            st.session_state.factsheet = "{}"
            for sheet_name, df in st.session_state.funcspec.items():
                st.text(f"Sheet Name: {sheet_name}")
                
                df = df.apply(pd.to_numeric, errors='ignore')
                funcspecstr = df.to_csv()

                # Split the string into parts with a maximum of 3000 characters
                parts = split_string(funcspecstr, 3000)

                # Process each part in a for loop
                for part in parts:
                    st.session_state.factsheet = generate_factsheet(st.session_state.factsheet,sheet_name,part)
                    st.code(st.session_state.factsheet,language="json")
                    st.text("##########")

with tabFuncSpecToRAML:
    st.subheader(f"Functional Specification to RAML")


    # st.session_state.funcspec = pd.read_excel('funcspec/Functional Spec - Account Statement & Advice control service - Share to IBM.xlsx', sheet_name=None)
    if st.session_state.funcspec is not None:
        sheetnames = []
        for sheet_name, df in st.session_state.funcspec.items():
            sheetnames.append(sheet_name)

        tabs = st.tabs(sheetnames)
        tabindex = 0
        for sheet_name, df in st.session_state.funcspec.items():
            with tabs[tabindex]:
                st.text(f"Sheet Name: {sheet_name}")
                st.dataframe(df)

                if st.button(f"Generate {sheet_name} RAML/Java"):
                    with st.expander("RAML/Java"):
                        if sheet_name.startswith("Input"):
                            inputfunction = generate_inputfunction_raml(df)
                            st.code(inputfunction,language="yaml")
                            st.session_state.inputraml.append(inputfunction)
                            # inputfunction = generate_inputfunction(df)
                            # st.code(inputfunction,language="java")
                            st.text("##########")
                        elif sheet_name.startswith("Output"):
                            outputfunction = generate_outputfunction_raml(df)
                            st.code(outputfunction,language="yaml")
                            st.session_state.outputraml.append(outputfunction)
                            
                            # outputfunction = generate_outputfunction(df)
                            # st.code(outputfunction,language="java")
                            st.text("##########")
                        elif sheet_name.startswith("Process"):
                            # processfunction = generate_processfunction_raml(df)
                            # st.code(processfunction,language="yaml")
                            processfunction = generate_processfunction(df)
                            st.code(processfunction,language="java")
                            st.session_state.process.append(processfunction)
                            
                            st.text("##########")
                        elif sheet_name.startswith("C"):
                            screenfunction = generate_screenfunction_raml(df)
                            st.code(screenfunction,language="yaml")
                            screenfunction = generate_screenfunction(df)
                            st.code(screenfunction,language="java")
                            st.text("##########")

                tabindex += 1

with tabRAMLToJava:
    st.subheader(f"Generate Java Skeleton")
    if st.button("Generate Swagger"):
        for raml in st.session_state.inputraml:
            st.code(raml,language="yaml")
            with st.expander("swagger"):
                swagger = generate_swagger(raml)
                st.code(swagger,language="json")
                
                jsonfile = swagger.encode('utf-8')

                st.download_button(
                    label="Download JSON",
                    data=jsonfile,
                    file_name='swagger.json',
                    mime='text/json',
                )

                with open("swagger.json", "w") as file:
                    file.write(swagger)
    
                # Execute the command with the saved Swagger JSON file
                command = "swagger-codegen generate -i swagger.json \
-l spring --api-package com.hsbc.hbap.obs.transaction.application.controller.command \
--model-package com.hsbc.hbap.obs.transaction.application.vo \
--invoker-package=com.hsbc.hbap.obs.transaction \
--additional-properties configPackage=com.hsbc.hbap.obs.transaction.config useTags=true -o out"
                print(command)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                # Display the command output
                st.code(result.stdout)