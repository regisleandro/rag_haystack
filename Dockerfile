FROM python:3.11.2-slim-bullseye
LABEL name="Legal RAG"
LABEL version="0.0.1"
LABEL description="Legal RAG is a tool for legal research and analysis."
LABEL maintainer="Regis Leandro Buske - regisleandro@gmail.com"

RUN addgroup --gid 1002 --system user
RUN adduser --uid 1002 --ingroup user --disabled-password --gecos "" user
RUN adduser --uid 1002 --system user -G user -h /home/user --shell /bin/bash

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  gfortran \
  libopenblas-dev \
  libc6-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD api /app/api
ADD src /app/src
ADD requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-compile --no-cache-dir -r /app/requirements.txt

RUN apt-get remove -y build-essential libpq-dev && \
  apt-get autoremove -y

RUN python -m spacy download pt_core_news_sm

RUN chown user:user -R /app
USER user

EXPOSE 35000

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "35000"]
