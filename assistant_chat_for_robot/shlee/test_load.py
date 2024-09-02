from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma
import dotenv
dotenv.load_dotenv()
import streamlit as st
import time
import openai




from langchain.document_loaders import PyPDFLoader

loader1 = PyPDFLoader("LG1세대[FnB2.0]_사용자매뉴얼.pdf")
loader2 = PyPDFLoader("LG2세대[FnB3.0]_사용자매뉴얼.pdf")
data1 = loader1.load()
data2 = loader2.load()

data = data1+data2

print(data)

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
docs = text_splitter.split_documents(data)

