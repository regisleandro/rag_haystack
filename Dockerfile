FROM python:3.12
LABEL name="Legal RAG"
LABEL version="0.0.1"
LABEL description="Legal RAG is a tool for legal research and analysis."
LABEL maintainer="Regis Leandro Buske - regisleandro@gmail.com"

RUN addgroup --gid 1002 --system user
RUN adduser --uid 1002 --ingroup user --disabled-password --gecos "" user
RUN adduser --uid 1002 --system user -G user -h /home/user --shell /bin/bash

WORKDIR /app

RUN git clone https://github.com/regisleandro/rag_haystack.git .

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN chown user:user -R /app
USER user

EXPOSE 35000
