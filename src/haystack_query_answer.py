from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.rankers import LostInTheMiddleRanker
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

from src.document_store import DocumentStore

class HaystackQueryAnswer:

  query_prompt_template = """
    You are an Educational AI Assistant, you goal is to provide correct answers for complex queries. 
    Here is the original question you were asked: {{question}}

    Context:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}

    Question: {{question}}
    Answer:
  """  

  pipeline: Pipeline
      
  def __init__(self):
    load_dotenv()
    self.document_store = DocumentStore(recreate_table=False).document_store
    self.pipeline = self.query_pipeline()

  def run(self, query: str) -> dict:
    return self.query_pipeline().run(data={
      'retriever': { 'top_k': 10},
      'ranker': {'top_k': 3},
      'text_embedder': {'text': query},
      'prompt_builder': {'question': query}
    })

  def query_pipeline(self) -> Pipeline:  
    pipeline = Pipeline()

    retriever = PgvectorEmbeddingRetriever(document_store=self.document_store)
    ranker = LostInTheMiddleRanker(word_count_threshold=1024)

    pipeline.add_component('text_embedder', OpenAITextEmbedder(model='text-embedding-3-small'))
    pipeline.add_component(instance=retriever, name='retriever')
    pipeline.add_component(instance=ranker, name='ranker')
    pipeline.add_component('prompt_builder', PromptBuilder(template=self.query_prompt_template))
    pipeline.add_component('llm', OpenAIGenerator(model='gpt-4o-mini', generation_kwargs={'temperature': 0.2}))

    pipeline.connect('text_embedder.embedding', 'retriever.query_embedding')
    pipeline.connect('retriever.documents', 'ranker.documents')
    pipeline.connect('ranker.documents', 'prompt_builder.documents')
    pipeline.connect('prompt_builder', 'llm')

    return pipeline
  
  def draw(self):
    self.pipeline.draw(path='query.jpg')
