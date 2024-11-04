from dotenv import load_dotenv
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
import os

class DocumentStore:
  document_store: PgvectorDocumentStore
  def __init__(self, recreate_table: bool = False):
    load_dotenv()
    self.document_store = self.get_document_store(recreate_table)

  def get_document_store(self, recreate_table: bool = False) -> PgvectorDocumentStore:
    return PgvectorDocumentStore(
      embedding_dimension=1536,
      table_name=os.getenv('TABLE_NAME'),
      vector_function='cosine_similarity',
      recreate_table=recreate_table,
      search_strategy='hnsw',
    )