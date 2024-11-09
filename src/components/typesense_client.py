import itertools
import typesense
from haystack import component, Document
from typing import List
from src.tools.lemmatizer import Lemmatizer
from dotenv import load_dotenv
import os

@component
class TypesenseClient:
  def __init__(self):
    load_dotenv()
    self.client = typesense.Client({
      'nodes': [{
        'host': os.getenv('TYPESENSE_HOST'),
        'port': os.getenv('TYPESENSE_PORT'),
        'protocol': os.getenv('TYPESENSE_PROTOCOL')
      }],
      'api_key': os.getenv('TYPESENSE_API_KEY'),
      'connection_timeout_seconds': 2
    })
    self.lemmatizer = Lemmatizer()

  @component.output_types(documents=List[Document])
  def run(self, documents: List[Document]):
    for batch in itertools.batched(documents, 50):
      documents_for_typesense = []
      for doc in batch:
        documents_for_typesense.append({
          'content': self.lemmatizer.lemmatize_without_stopwords(doc.content),
          'meta': doc.meta or {}
        })
      # Import documents into Typesense
      self.client.collections['documents'].documents.import_(documents_for_typesense)

    return {'documents': documents}