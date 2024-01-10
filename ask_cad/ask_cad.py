import sys
import logging
import os
import tempfile
import pathlib

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer

from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM


from typing import Literal, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np
# Most GENAI logs are at Debug level.
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

st.set_page_config(
    page_title="AskCAD",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


st.header("AskCAD")
# chunk_size=1500
# chunk_overlap = 200

load_dotenv()

api_key = os.getenv("API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

# handler = StdOutCallbackHandler()

creds = {
    "url"    : "https://us-south.ml.cloud.ibm.com",
    "apikey" : api_key
}

params = {
    GenParams.DECODING_METHOD:"greedy",
    GenParams.MAX_NEW_TOKENS:2000,
    GenParams.MIN_NEW_TOKENS:1,
    GenParams.TEMPERATURE:0.5,
    GenParams.TOP_K:50,
    GenParams.TOP_P:1,
    GenParams.STOP_SEQUENCES:['</html>'],
}

def askcad(question):
    prompt = f"""generate html file include 3d model base on input, leverage three.js
- generate the html only
input: generate a 3d cube
output:
```
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Three.js Cube</title>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <script src="https://cdn.jsdelivr.net/npm/three@0.133.0/build/three.min.js"></script>
    <script>
      // Create a scene
      const scene = new THREE.Scene();

      // Create a camera
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 5;

      // Create a renderer
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      // Create a cube geometry
      const geometry = new THREE.BoxGeometry(1, 1, 1);

      // Create a basic material with a red color
      const material = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});

      // Create a mesh using the geometry and material
      const cube = new THREE.Mesh(geometry, material);

      // Add the cube to the scene
      scene.add(cube);

      // Animation loop
      function animate() {{
        requestAnimationFrame(animate);

        // Rotate the cube
        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;

        // Render the scene with the camera
        renderer.render(scene, camera);
      }}

      // Start the animation loop
      animate();
    </script>
  </body>
</html>
```
input: generate a cylinder
output:
```
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Three.js Cylinder</title>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <script src="https://cdn.jsdelivr.net/npm/three@0.133.0/build/three.min.js"></script>
    <script>
      // Create a scene
      const scene = new THREE.Scene();

      // Create a camera
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 5;

      // Create a renderer
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      // Create a cylinder geometry
      const geometry = new THREE.CylinderGeometry(1, 1, 2, 32);

      // Create a basic material with a red color
      const material = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});

      // Create a mesh using the geometry and material
      const cylinder = new THREE.Mesh(geometry, material);

      // Add the cylinder to the scene
      scene.add(cylinder);

      // Animation loop
      function animate() {{
        requestAnimationFrame(animate);

        // Rotate the cylinder
        cylinder.rotation.x += 0.01;
        cylinder.rotation.y += 0.01;

        // Render the scene with the camera
        renderer.render(scene, camera);
      }}

      // Start the animation loop
      animate();
    </script>
  </body>
</html>
```
input: generate a cube with strong lighting
output:
```
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Three.js Iron Cube</title>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <script src="https://cdn.jsdelivr.net/npm/three@0.133.0/build/three.min.js"></script>
    <script>
      // Create a scene
      const scene = new THREE.Scene();

      // Create a camera
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.z = 5;

      // Create a renderer
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      // Create a cube geometry
      const geometry = new THREE.BoxGeometry(1, 1, 1);

      // Create a metallic material
      const material = new THREE.MeshStandardMaterial({{ color: 0x888888, metalness: 1 }});

      // Create a mesh using the geometry and material
      const cube = new THREE.Mesh(geometry, material);

      // Add the cube to the scene
      scene.add(cube);

      // Create directional light
      const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
      directionalLight.position.set(5, 5, 5);
      scene.add(directionalLight);

      // Create ambient light
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
      scene.add(ambientLight);

      // Animation loop
      function animate() {{
        requestAnimationFrame(animate);

        // Rotate the cube
        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;

        // Render the scene with the camera
        renderer.render(scene, camera);
      }}

      // Start the animation loop
      animate();
    </script>
  </body>
</html>
```
input: {question}
output:
```"""

    prompts = [prompt]
    answer = ""
    for response in model.generate_text(prompts):
        answer += response.replace("\\n\\n","\n")
    return answer

model = Model("meta-llama/llama-2-70b-chat",creds, params, project_id)

if "cadhtml" not in st.session_state:
    st.session_state.cadhtml = ""

with st.sidebar:
    st.title("AskCAD")
    # components.html(st.session_state.cadhtml,height=300)

with st.chat_message("system"):
    st.write("input your instruction")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == 'user':
            st.markdown(message["content"])
        elif message["role"] == 'agent':
            st.code(message["content"],language="html")
            components.html(message["content"])

if query := st.chat_input("your query"):
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner(text="generating...", cache=False):
        answer = askcad(query)

    st.session_state.messages.append({"role": "agent", "content": answer}) 

    with st.chat_message("agent"):
        st.code(answer,language="html")
        components.html(answer)
        # st.session_state.cadhtml = answer
        