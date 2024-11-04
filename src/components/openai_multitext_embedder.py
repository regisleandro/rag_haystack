from haystack.components.embedders import OpenAITextEmbedder
from pydantic import BaseModel
from haystack import component
from typing import List

# This is a custom implementation of the OpenAITextEmbedder class that overrides the run method to handle multiple text inputs.
# from https://haystack.deepset.ai/blog/query-decomposition
@component
class OpenAIMultiTextEmbedder:
  def __init__(self, model: str = 'text-embedding-3-small'):
    self.model = model
    self.query_embedder = OpenAITextEmbedder(model=self.model)

  @component.output_types(embeddings=List[List[float]])
  def run(self, questions: BaseModel):
    embeddings = []
    for question in questions.questions:
      embeddings.append(self.query_embedder.run(question.question)['embedding'])
    return {'embeddings': embeddings}
    