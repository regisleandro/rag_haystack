### Python RAG with Haystack AI
This is a simple Python RAG (Retrieval Augmented Generation) model using Haystack AI. T
The goal of this project is to demonstrate how to use Haystack AI to build a simple RAG model in Python.
It uses a PostgreSQL database to store the documents and the model is built using the Haystack AI library.
It ingests the documents from the database and then uses the RAG model to answer questions based on the documents.
There are an api interface to ask questions and get answers from the model.

### Installation
1. Clone the repository
```bash
git clone
```
2. Install the dependencies
```bash
pip install -r requirements.txt
```
3. Create a PostgreSQL database
4. Update the database connection string in the `.env` file
5. Run the ingest script to ingest the documents into the database
6. Run the app
```bash
./start.sh
```

