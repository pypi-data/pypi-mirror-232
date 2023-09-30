import os

from wasabi import msg  # type: ignore[import]

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pathlib import Path
from pydantic import BaseModel

from prompt.retrieval.simple_engine import SimpleWeaviateQueryEngine
from prompt.retrieval.advanced_engine import AdvancedWeaviateQueryEngine

from dotenv import load_dotenv

load_dotenv()

# weaviate_engine = SimpleWeaviateQueryEngine()
weaviate_engine = AdvancedWeaviateQueryEngine()

# FastAPI App
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "http://0.0.0.0:8000",
    # add deployed tenx chatbot domain
]

# Add middleware for handling Cross Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryPayload(BaseModel):
    query: str


class GetDocumentPayload(BaseModel):
    document_id: str

#----------------------------------health check api end-point----------------------------------
# Define health check endpoint
@app.get("/chatbot/health")
async def root():
    try:
        if weaviate_engine.get_client().is_ready():
            return JSONResponse(
                content={
                    "message": "Alive!",
                }
            )
        else:
            return JSONResponse(
                content={
                    "message": "Database not ready!",
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
    except Exception as e:
        msg.fail(f"Healthcheck failed with {str(e)}")
        return JSONResponse(
            content={
                "message": f"Healthcheck failed with {str(e)}",
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

#------------------------------------query api end-point---------------------------------------
# Receive query and return chunks and query answer
@app.post("/chatbot/query")
async def query(payload: QueryPayload):
    try:
        system_msg, results = weaviate_engine.query(
            payload.query, os.environ["WEAVIATE_MODEL"]
        )
        msg.good(f"Succesfully processed query: {payload.query}")

        return JSONResponse(
            content={
                "system": system_msg,
                "documents": results,
            }
        )
    except Exception as e:
        msg.fail(f"Query failed")
        print(e)
        return JSONResponse(
            content={
                "system": f"Something went wrong! {str(e)}",
                "documents": [],
            }
        )