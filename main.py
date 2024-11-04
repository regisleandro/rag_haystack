
from src.haystack_ingestor import HaystackIngestor
from src.haystack_query_answer import HaystackQueryAnswer
from src.haystack_multi_query_answer import HaystackMultiQueryAnswer

import logging

def main():
  #logging.basicConfig(level=logging.DEBUG)
  #logging.basicConfig(level=logging.INFO)
  # pdf_path = 'Caderno de Questões OAB - 22º ao 37º Exame.pdf'
  pdfs = ['estatuto_oab.pdf', 'codigo_etica.pdf', 'CF88_EC132_livro.pdf']
  ingestor = HaystackIngestor()

  print('Ingested PDF', ingestor.ingest_files(pdfs))
  print('********************************************')
  
  query_answer = HaystackQueryAnswer()
  multi_query_answer = HaystackMultiQueryAnswer()
  # query_answer.draw()
  # multi_query_answer.draw()

  queries =[
    """ 
      A advogada Maria foi procurada por certo cliente para o patrocínio de uma demanda judicial.  Ela,  então,  apresentou  ao  cliente  contrato  de  prestação  de  seus  serviços profissionais. A cláusula dez do documento estabelecia que Maria obrigava-se apenas a atuar na causa no primeiro grau de jurisdição. Além disso, a cláusula treze dispunha sobre a obrigatoriedade de pagamento de honorários, em caso de ser obtido acordo antes do oferecimento da petição inicial. Irresignado, o cliente encaminhou cópia do contrato à OAB, solicitando providências disciplinares. Sobre os termos do contrato, o que é correto afirmar.
    """,
    """"
      José,  servidor  público  federal  ocupante  exclusivamente  de  cargo  em  comissão,  foi 
      exonerado, tendo a autoridade competente motivado o ato em reiterado 
      descumprimento da carga horária de trabalho pelo servidor. José obteve, junto ao 
      departamento  de  recursos  humanos,  documento  oficial  com  extrato  de  seu  ponto 
      eletrônico, comprovando o regular cumprimento de sua jornada de trabalho. Assim, o 
      servidor  buscou  assistência  jurídica  junto  a  um  advogado,  que  lhe  informou 
      corretamente, à luz do ordenamento jurídico, que  
    """,
    """
      Viviane, Paula e Milena são advogadas. Viviane acaba de dar à luz, Paula adotou uma 
      criança e  Milena está em período de amamentação. Diante da situação narrada, de 
      acordo com o Estatuto da OAB, assinale a afirmativa correta. 
    """,
    """
      Claudio, advogado inscrito na seccional da OAB do RJ cometeu uma infração na seccional da OAB de SP.
      O conselho de ética e disciplina da seccional da OAB do RJ instaurou um processo disciplinar para apuração da infração cometida em outra seccional.
      Sobre o caso, de acordo com o estatuto da OAB, o conselho de ética e disciplina da seccional da OAB do RJ:
    """
  ]

  index = 3
  # print('Answer: -> old pipeline', query_answer.run(queries[index]))

  # print('********************************************')
  # print('********************************************')
  # print('********************************************')

  # result = multi_query_answer.run(queries[index])
  # for pair in result['query_resolver_llm']['structured_reply'].questions:
  #   print(pair)
  # print('\nSo the original query is answered as follows:\n')
  # print(result['reasoning_llm']['replies'][0])

  print('********************************************')
  print('********************************************')
  print('********************************************')

  # for query in queries:
  #   result = multi_query_answer.run(query)
  #   for pair in result['query_resolver_llm']['structured_reply'].questions:
  #     print(pair)
  #   print('\nSo the original query is answered as follows:\n')
  #   print(result['reasoning_llm']['replies'][0])
  #   print('********************************************')


if __name__ == '__main__':
  main()