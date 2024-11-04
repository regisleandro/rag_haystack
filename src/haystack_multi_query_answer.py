from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

from src.components.openai_generator import OpenAIGenerator as OpenAIExtendedGenerator
from src.components.openai_multitext_embedder import OpenAIMultiTextEmbedder
from src.components.multi_query_pgvector_embedding_retriever import MultiQueryPgVectorEmbeddingRetriever
from src.document_store import DocumentStore
from src.models.question import Questions

class HaystackMultiQueryAnswer:

  splitter_prompt = """
    You are a helpful assistant that prepares queries that will be sent to a search component. Always use portuguese language.
    Sometimes, these queries are very complex.
    Your job is to simplify complex queries into multiple queries that can be answered in isolation to eachother.
    Don't invent new information. Don't add your opinion.
    You need to extract the original query meaning and split it into 2 simpler questions. Its essential to keep the original meaning.
    Add the topic of the query in the question.
    Don't generate more than 2 questions.
    If the query is simple, then keep it as it is.
    Examples
    1. Query: Did Microsoft or Google make more money last year?
      Decomposed Questions: [Question(question='How much profit did Microsoft make last year?', answer=None), Question(question='How much profit did Google make last year?', answer=None)]
    2. Query: What is the capital of France?
      Decomposed Questions: [Question(question='What is the capital of France?', answer=None)]
    3. Query: {{question}}
      Decomposed Questions:
  """

  multi_query_prompt_template = """
    You are an Educational AI Assistant, you goal is to provide correct answers for complex queries. Always use portuguese language.
    Here is the original question you were asked: {{question}}

    And you have split the task into the following questions:
    {% for pair in question_context_pairs %}
      {{pair.question}}
    {% endfor %}

    Here are the question and context pairs for each question.
    For each question, generate the question answer pair as a structured output, please be concise and clear
    {% for pair in question_context_pairs %}
      Question: {{pair.question}}
      Context: {{pair.documents}}
    {% endfor %}

    Answers:
  """

  reasoning_template = """
    You are an Educational AI Assistant, you goal is to provide correct answers for complex queries. Always use portuguese language.
    Here is the original question you were asked: {{question}}

    You have split this question up into simpler questions that can be answered in isolation.
    Here are the questions and answers that you've generated
    {% for pair in question_answer_pair %}
      {{pair}}
    {% endfor %}

    Reason about the final answer to the original query based on these questions and aswers
    Final Answer:
  """

  pipeline: Pipeline
      
  def __init__(self):
    load_dotenv()
    self.document_store = DocumentStore(recreate_table=False).document_store
    #self.pipeline = self.multi_query_pipeline()

  def run(self, question: str) -> dict:
    return self.multi_query_pipeline().run(
      {
        'prompt':{'question': question},
        'multi_query_prompt': {'question': question},
        'reasoning_prompt': {'question': question}
      },
      include_outputs_from=['query_resolver_llm']
    )
  
  def multi_query_pipeline(self) -> Pipeline:
    prompt = PromptBuilder(template=self.splitter_prompt)
    llm = OpenAIExtendedGenerator(model='gpt-4o-mini', generation_kwargs={'temperature': 0.2, 'response_format': Questions})
    query_resolver_llm = OpenAIExtendedGenerator(model='gpt-4o-mini', generation_kwargs={'temperature': 0.2, 'response_format': Questions})
    multi_query_prompt = PromptBuilder(self.multi_query_prompt_template)
    reasoning_prompt = PromptBuilder(self.reasoning_template)
    multi_query_pipeline = Pipeline()
    
    multi_query_pipeline.add_component('prompt', prompt)
    multi_query_pipeline.add_component('llm', llm)
    multi_query_pipeline.add_component('embedder', OpenAIMultiTextEmbedder(model='text-embedding-3-small'))
    multi_query_pipeline.add_component('multi_query_retriever', MultiQueryPgVectorEmbeddingRetriever(retriever=self.retriever(), top_k=5))
    multi_query_pipeline.add_component('multi_query_prompt', multi_query_prompt)
    multi_query_pipeline.add_component('query_resolver_llm', query_resolver_llm)
    multi_query_pipeline.add_component('reasoning_prompt', reasoning_prompt)
    multi_query_pipeline.add_component('reasoning_llm', OpenAIExtendedGenerator(model='gpt-4o-mini', generation_kwargs={'temperature': 0.2}))

    multi_query_pipeline.connect('prompt', 'llm')
    multi_query_pipeline.connect('llm.structured_reply', 'embedder.questions')
    multi_query_pipeline.connect('embedder.embeddings', 'multi_query_retriever.query_embeddings')
    multi_query_pipeline.connect('llm.structured_reply', 'multi_query_retriever.queries')
    multi_query_pipeline.connect('llm.structured_reply', 'embedder.questions')
    multi_query_pipeline.connect('multi_query_retriever.question_context_pairs', 'multi_query_prompt.question_context_pairs')
    multi_query_pipeline.connect('multi_query_prompt', 'query_resolver_llm')
    multi_query_pipeline.connect('query_resolver_llm.structured_reply', 'reasoning_prompt.question_answer_pair')
    multi_query_pipeline.connect('reasoning_prompt', 'reasoning_llm')
    return multi_query_pipeline

  def retriever(self):
    return PgvectorEmbeddingRetriever(document_store=self.document_store)
  
  def draw(self):
    self.pipeline.draw(path='query_answer.jpg')