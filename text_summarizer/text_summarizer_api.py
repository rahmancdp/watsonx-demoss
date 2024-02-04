import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
]  # Add any other allowed origins as needed


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],  # Add "OPTIONS" method here
    allow_headers=["Content-Type"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/summarize")
async def summarize_text(request: Request, payload: dict):
    source_text = payload.get("source_text")
    print("SOURCE TEXT:"+str(source_text))

    if not source_text.strip():
        return {"error": "Please provide source text"}

    load_dotenv()
    api_key = os.getenv("API_KEY", None)
    project_id = os.getenv("PROJECT_ID", None)

    creds = {
        "url"    : "https://us-south.ml.cloud.ibm.com",
        "apikey" : api_key
    }

    params = {
        GenParams.DECODING_METHOD: "sample",
        GenParams.MAX_NEW_TOKENS: 100,
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.TEMPERATURE: 0.5,
        GenParams.TOP_K: 50,
        GenParams.TOP_P: 1
    }

    model = Model("google/flan-ul2", creds, params, project_id)

    summary = ""
    for response in model.generate_text_stream(source_text):
        summary += response

    for chunk in model.generate_text_stream(source_text):
        print(chunk, end='')
    
    return {"summary": summary}

if __name__ == "__main__":
    space_id = None
    verify = False
    uvicorn.run(app, host="0.0.0.0", port=8000)