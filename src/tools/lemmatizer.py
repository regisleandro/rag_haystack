import spacy

class Lemmatizer:
  def __init__(self):
    self.nlp = spacy.load('pt_core_news_sm')
  
  def lemmatize(self, text: str) -> str:
    doc = self.nlp(text)
    return ' '.join([token.lemma_ for token in doc])