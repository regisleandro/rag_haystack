from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from src.components.typesense_client import TypesenseClient
from dotenv import load_dotenv
import os


class TypesenseIngestor:
  def __init__(self):
    load_dotenv()
    self.typesense_client = TypesenseClient()
    self.pipeline = self.insgest_pipeline()

  def ingest_files(self, file_names: list[str]):
    self.pipeline.connect('converter', 'cleaner')
    self.pipeline.connect('cleaner', 'splitter')
    self.pipeline.connect('splitter', 'writer')

    self.pipeline.run({'converter': {'sources': file_names}})

  def insgest_pipeline(self) -> Pipeline:
    pipeline = Pipeline()
    pipeline.add_component('converter', PyPDFToDocument())
    pipeline.add_component('cleaner', DocumentCleaner())
    pipeline.add_component('splitter', DocumentSplitter(split_by='sentence', split_length=30))
    pipeline.add_component('writer', self.typesense_client)
    return pipeline

  def create_schema(self):
    documents_schema = {
      'name': 'documents',
      'fields': [
        {'name': 'content', 'type': 'string' },
        {"name": ".*", "type": "auto" },
        {
          'name' : 'embedding',
          'type' : 'float[]',
          'embed': {
            'from': [
              'content'
            ],
            'model_config': {
              'model_name': 'openai/text-embedding-3-small',
              'api_key': os.getenv('OPENAI_API_KEY')
            }
          }
        }
      ]
    }

    self.typesense_client.client.collections.create(documents_schema)