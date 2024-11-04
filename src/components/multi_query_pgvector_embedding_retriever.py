from pydantic import BaseModel
from haystack import component
from typing import List, Dict
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

@component
class MultiQueryPgVectorEmbeddingRetriever:
  def __init__(self, retriever: PgvectorEmbeddingRetriever, top_k: int = 3):
    self.retriever = retriever
    self.question_context_pairs = []
    self.top_k = top_k

  @component.output_types(question_context_pairs=List[Dict])
  def run(self, queries: BaseModel, query_embeddings: List[List[float]],top_k: int = None):
    if top_k != None:
      self.top_k = top_k
    for query, embedding in zip(queries.questions, query_embeddings):
      result = self.retriever.run(query_embedding = embedding, top_k = self.top_k)
      self.question_context_pairs.append({'question': query.question, 'documents': {doc.content for doc in result['documents']}})
    return {'question_context_pairs': self.question_context_pairs}