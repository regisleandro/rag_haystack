from fastapi import (
    FastAPI,
    Body,
    Depends,
    File,
    HTTPException,
    status,
    UploadFile
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import logging
import tempfile

import sys
sys.path.append('../')

from dotenv import load_dotenv
import os

load_dotenv()

from pydantic import BaseModel
from src.haystack_ingestor import HaystackIngestor
from src.haystack_multi_query_answer import HaystackMultiQueryAnswer
from src.typesense_ingestor import TypesenseIngestor
from src.typesense_query_answer import TypesenseQueryAnswer

log = logging.getLogger(__name__)

app = FastAPI()

SIMPLE_TOKEN = os.getenv('API_TOKEN')

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  if token != SIMPLE_TOKEN:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid token",
      headers={"WWW-Authenticate": "Bearer"},
    )

origins = ['*']

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.state.multi_query_pipeline = HaystackMultiQueryAnswer()
app.state.ingestor = HaystackIngestor(recreate_table=False)

app.typesense_ingestor = TypesenseIngestor()
app.typesense_query_answer = TypesenseQueryAnswer()

class QuestionRequest(BaseModel):
  query: str

@app.post('/ask', dependencies=[Depends(verify_token)])
async def process_question(question_request: QuestionRequest = Body(...)):
  return app.state.multi_query_pipeline.run(question_request.query)

@app.post('/ingest', dependencies=[Depends(verify_token)])
async def ingest_data(file: UploadFile = File(...)):
  with tempfile.TemporaryDirectory() as tmp_dir:
    file_path = os.path.join(tmp_dir, file.filename)
    with open(file_path, 'wb') as temp_file:
      content = await file.read()
      temp_file.write(content)
    app.state.ingestor.ingest_files([file_path])
  return {'message': 'Data ingested successfully'}

@app.post('/typesense/ask', dependencies=[Depends(verify_token)])
def typesense_process_question(question_request: QuestionRequest = Body(...)):
  return app.typesense_query_answer.query(question_request.query)

@app.post('/typesense/ingest', dependencies=[Depends(verify_token)])
async def typesense_ingest_data(file: UploadFile = File(...)):
  with tempfile.TemporaryDirectory() as tmp_dir:
    file_path = os.path.join(tmp_dir, file.filename)
    with open(file_path, 'wb') as temp_file:
      content = await file.read()
      temp_file.write(content)
    app.typesense_ingestor.ingest_files([file_path])
  return {'message': 'Data ingested successfully'}

@app.post('/typesense/schema', dependencies=[Depends(verify_token)])
def create_typesense_schema():
  app.typesense_ingestor.create_schema()
  return {'message': 'Schema created successfully'}