from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_vector_store_as_retriever(data, str1, str2):
 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(data)

    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(
        documents=docs, embedding=embedding
    )

    retriever = vectorstore.as_retriever()
    
    retriever.search_kwargs = {'k': 63}

    tool = create_retriever_tool(
        retriever,
        str1,
        str2,
    )

    return tool