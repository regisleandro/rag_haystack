from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from src.tools.lemmatizer import Lemmatizer

from src.components.typesense_retriever import TypesenseRetriever

class TypesenseQueryAnswer:
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
  
  def __init__(self):
    self.typesense_retriever = TypesenseRetriever()
    self.lemmatizer = Lemmatizer()
    self.query_pipeline = self.query_pipeline()

  def query(self, query: str):
    lemmatized_query = self.lemmatizer.lemmatize_without_stopwords(query)
    search_parameters = self.search_parameters_builder(lemmatized_query)
    return self.query_pipeline.run({
      'retriever': {'search_parameters': search_parameters},
      'prompt_builder': {'question': query}
    })

  def query_pipeline(self) -> Pipeline:
    pipeline = Pipeline()
    pipeline.add_component(instance=self.typesense_retriever, name='retriever')
    pipeline.add_component('prompt_builder', PromptBuilder(template=self.query_prompt_template))
    pipeline.add_component('llm', OpenAIGenerator(model='gpt-4o-mini', generation_kwargs={'temperature': 0.2}))

    pipeline.connect('retriever.documents', 'prompt_builder.documents')
    pipeline.connect('prompt_builder', 'llm')
    return pipeline
  
  def search_parameters_builder(self, query: str):
    return {
      'searches':[{
        'q'         : query,
        'query_by'  : 'embedding',
        'collection': 'documents',
        'per_page'  : 5,
        'page'      : 1,
        'prefix'    : False
      }]
    }
