import typesense
from haystack import component, Document
from typing import List
from dotenv import load_dotenv
import os

@component
class TypesenseRetriever:
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

  @component.output_types(documents=List[Document])
  def run(self, search_parameters: dict):
    documents = self.client.multi_search.perform(search_parameters, {})
    documents = [
      Document(content=hit['document']['content'], embedding=hit['document']['embedding']) for hit in documents['results'][0]['hits']
    ]
    return {'documents': documents}