from fastapi import (
    FastAPI,
    Body,
    Depends,
    HTTPException,
    status
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import logging

import sys
sys.path.append('../')

from dotenv import load_dotenv
import os

load_dotenv()

from pydantic import BaseModel
from src.haystack_multi_query_answer import HaystackMultiQueryAnswer

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

class QuestionRequest(BaseModel):
  query: str

@app.post('/ask', dependencies=[Depends(verify_token)])
async def process_question(question_request: QuestionRequest = Body(...)):
  answer = app.state.multi_query_pipeline.run(question_request.query)
  print(answer)

  return answer
