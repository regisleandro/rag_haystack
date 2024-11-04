from haystack import component
from openai import  Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from haystack.components.generators import OpenAIGenerator
from haystack.components.generators.openai_utils import _convert_message_to_openai_format
from haystack.dataclasses import ChatMessage, StreamingChunk
from pydantic import BaseModel
from typing import List, Any, Dict, Optional, Callable, Union

# This is a custom implementation of the OpenAIGenerator class that overrides the run method to handle the response_format parameter.
# from https://haystack.deepset.ai/blog/query-decomposition
class OpenAIGenerator(OpenAIGenerator):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  @component.output_types(replies=List[str], meta=List[Dict[str, Any]], structured_reply=BaseModel)
  def run(self, prompt: str, streaming_callback: Optional[Callable[[StreamingChunk], None]] = None, generation_kwargs: Optional[Dict[str, Any]] = None,):
    generation_kwargs = {**self.generation_kwargs, **(generation_kwargs or {})}
    if 'response_format' in generation_kwargs.keys():
      message = ChatMessage.from_user(prompt)
      if self.system_prompt:
        messages = [ChatMessage.from_system(self.system_prompt), message]
      else:
        messages = [message]

      streaming_callback = streaming_callback or self.streaming_callback
      openai_formatted_messages = [_convert_message_to_openai_format(message) for message in messages]
      completion: Union[Stream[ChatCompletionChunk], ChatCompletion] = self.client.beta.chat.completions.parse(
        model=self.model,
        messages=openai_formatted_messages,
        **generation_kwargs)
      completions = [self._build_structured_message(completion, choice) for choice in completion.choices]
      for response in completions:
        self._check_finish_reason(response)

      return {
        'replies': [message.content for message in completions],
        'meta': [message.meta for message in completions],
        'structured_reply': completions[0].content
      }
    else:
      return super().run(prompt, streaming_callback, generation_kwargs)

  def _build_structured_message(self, completion: Any, choice: Any) -> ChatMessage:
    chat_message = ChatMessage.from_assistant(choice.message.parsed or '')
    chat_message.meta.update(
      {
        'model': completion.model,
        'index': choice.index,
        'finish_reason': choice.finish_reason,
        'usage': dict(completion.usage),
      }
    )
    return chat_message