from spacy.lang.pt import Portuguese
from spacy.lang.pt.stop_words import STOP_WORDS

class Lemmatizer:
  def __init__(self):
    self.nlp = Portuguese()
  
  def lemmatize(self, text: str) -> str:
    doc = self.nlp(text)
    return ' '.join([token.lemma_ for token in doc])
  
  def lemmatize_without_stopwords(self, text: str) -> str:
    doc = self.nlp(text)
    tokens_list = []
    for token in doc:
      tokens_list.append(token.text)
    
    filtered_sentence = []
    for word in tokens_list:
      lexeme = self.nlp.vocab[word]
      if lexeme.is_stop == False:
        filtered_sentence.append(word)
    
    return ' '.join(filtered_sentence)