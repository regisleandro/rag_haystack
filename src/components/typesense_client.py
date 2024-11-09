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
    documents_for_typesense = []
    documents_for_typesense = [{'content': self.lemmatizer.lemmatize(doc.content), 'meta': doc.meta} for doc in documents]

    print(documents_for_typesense)

    # Import documents into Typesense
    self.client.collections['documents'].documents.import_(documents_for_typesense)
    return {'documents': documents}