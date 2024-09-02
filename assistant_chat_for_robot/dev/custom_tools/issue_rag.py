from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores import utils

OPENAI_API_KEY='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'


def create_vector_store_as_retriever(data, str1, str2):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
    docs = text_splitter.split_documents(data)


    embedding=OpenAIEmbeddings(openai_api_key =OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

    retriever = vectorstore.as_retriever()
    
    tool = create_retriever_tool(
        retriever,
        str1,
        str2,
    )
    
    return tool


def create_vector_store_as_retriever_w_mode(data, str1, str2):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
    docs = text_splitter.split_documents(data)
    docs = utils.filter_complex_metadata(docs)


    embedding=OpenAIEmbeddings(openai_api_key =OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

    retriever = vectorstore.as_retriever()
    
    tool = create_retriever_tool(
        retriever,
        str1,
        str2,
    )
    
    return tool