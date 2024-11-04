
from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
import src.document_store as document_store_module

class HaystackIngestor:
  def __init__(self, recreate_table=True):
    load_dotenv()
    self.document_store = document_store_module.DocumentStore(recreate_table=recreate_table).document_store

  def ingest_files(self, file_names: list[str]):
    pipeline = Pipeline()
    pipeline.add_component('converter', PyPDFToDocument())
    pipeline.add_component('cleaner', DocumentCleaner())
    pipeline.add_component('splitter', DocumentSplitter(split_by='sentence', split_length=30))
    pipeline.add_component('embedder', OpenAIDocumentEmbedder(model='text-embedding-3-small'))
    pipeline.add_component('writer', DocumentWriter(document_store=self.document_store))

    pipeline.connect('converter', 'cleaner')
    pipeline.connect('cleaner', 'splitter')
    pipeline.connect('splitter', 'embedder')
    pipeline.connect('embedder', 'writer')

    pipeline.run({'converter': {'sources': file_names}})


