import streamlit as st
import pandas as pd
from io import StringIO
from pptx import Presentation
from pptx.enum.lang import MSO_LANGUAGE_ID

from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.model import Model

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

creds = Credentials(api_key,api_endpoint)

params = GenerateParams(
    decoding_method="greedy",
    max_new_tokens=50,
    min_new_tokens=1,
    stream=False,
    temperature=0.05,
    top_k=50,
    top_p=1,
    stop_sequences=["\\n\\n"]
)

# llm = Model(model="ibm/granite-13b-chat-v1",credentials=creds, params=params)
llm = Model(model="meta-llama/llama-2-70b-chat",credentials=creds, params=params)

def buildprompt(text):
    return f"""[INST]be a translator, be concise.
    return the translated content only.
    dont output note.
    keep the time format.
    keep watsonx, watson.
    please help translate following english to traditional chinese.
    <<SYS>>
    english:{text}
    <</SYS>>
    [/INST]
    traditional chinese:"""

def translate_ppt(pptfile):
    # input_file_path = "sample.pptx"

    sourcelang = MSO_LANGUAGE_ID.ENGLISH_US
    targetlang = MSO_LANGUAGE_ID.CHINESE_HONG_KONG_SAR

    presentation = Presentation(pptfile)

    slide_number = 1
    for slide in presentation.slides:
        print('Slide {slide_number} of {number_of_slides}'.format(
                slide_number=slide_number,
                number_of_slides=len(presentation.slides)))
        slide_number += 1

        # translate comments
        if slide.has_notes_slide:
            text_frame = slide.notes_slide.notes_text_frame
            if len(text_frame.text) > 0:
                prompttemplate = buildprompt(text_frame.text)
                response = llm.generate([prompttemplate])
                slide.notes_slide.notes_text_frame.text = response[0].generated_text


        # translate other texts
        for shape in slide.shapes:
            if shape.has_table:
                for cell in shape.table.iter_cells():
                    engtext = cell.text
                    prompttemplate = buildprompt(cell.text)
                    response = llm.generate([prompttemplate])
                    cell.text = response[0].generated_text
                    # print(engtext+'->'+response[0].generated_text)

            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for index, paragraph_run in enumerate(paragraph.runs):
                        engtext = paragraph_run.text
                        prompttemplate = buildprompt(paragraph_run.text)
                        response = llm.generate([prompttemplate])
                        paragraph.runs[index].text = response[0].generated_text
                        # print(engtext+'->'+response[0].generated_text)
                        paragraph.runs[index].font.language_id = targetlang

    presentation.save(dataoutput)
    return dataoutput

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)