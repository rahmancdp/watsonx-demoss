import streamlit as st
from pptx import Presentation
from pptx.enum.lang import MSO_LANGUAGE_ID

from genai.credentials import Credentials
from genai.schemas import GenerateParams
from genai.model import Model

import tempfile
import pathlib

import os
from dotenv import load_dotenv

load_dotenv()

api_key = st.secrets["GENAI_KEY"]
api_endpoint = st.secrets["GENAI_API"]

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

llm = Model(model="bigscience/mt0-xxl",credentials=creds, params=params)

def buildprompt(text):
    return f"""be a translator, be concise.
    return the translated content only.
    please help translate following english to traditional chinese.
    english:{text}
    traditional chinese:"""

def translate_ppt(pptfile):
    # input_file_path = "sample.pptx"

    sourcelang = MSO_LANGUAGE_ID.ENGLISH_US
    targetlang = MSO_LANGUAGE_ID.CHINESE_HONG_KONG_SAR

    presentation = Presentation(pptfile)

    slide_number = 1
    for slide in presentation.slides:
        st.write(f'Slide {slide_number} of {len(presentation.slides)}')
        slide_number += 1

        # translate comments
        if slide.has_notes_slide:
            text_frame = slide.notes_slide.notes_text_frame
            if len(text_frame.text) > 0:
                prompttemplate = buildprompt(text_frame.text)
                for response in llm.generate([prompttemplate]):
                    slide.notes_slide.notes_text_frame.text = response.generated_text


        # translate other texts
        for shape in slide.shapes:
            if shape.has_table:
                for cell in shape.table.iter_cells():
                    engtext = cell.text
                    prompttemplate = buildprompt(cell.text)
                    for response in llm.generate_async([prompttemplate]):
                        cell.text = response.generated_text
                        print(engtext+'->'+response.generated_text)

            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for index, paragraph_run in enumerate(paragraph.runs):
                        engtext = paragraph_run.text
                        prompttemplate = buildprompt(paragraph_run.text)
                        for response in llm.generate([prompttemplate]):
                            paragraph.runs[index].text = response.generated_text
                            print(engtext+'->'+response.generated_text)
                            paragraph.runs[index].font.language_id = targetlang

    output_file_path = pptfile.replace('.pptx', '-out.pptx')
    presentation.save(output_file_path)
    return output_file_path

temp_dir = tempfile.TemporaryDirectory()

uploaded_file = st.file_uploader(label="upload a ppt",type=['ppt','pptx'])
if uploaded_file is not None:
    st.write("filename:", uploaded_file.name)
    with open(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name),"wb") as f:
        f.write(uploaded_file.getbuffer())

    output_file_path = translate_ppt(os.path.join(pathlib.Path(temp_dir.name),uploaded_file.name))
    with open(output_file_path,'rb') as f:
        st.download_button('Download translated version', f,'translate.pptx')