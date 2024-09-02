'''
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import chroma
import dotenv
dotenv.load_dotenv()
import streamlit as st
import time
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import dotenv
dotenv.load_dotenv()
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.document_loaders import TextLoader, DirectoryLoader

#loader = DirectoryLoader ('./data', glob="푸두봇 가이드북.pdf")
#loader = PyPDFLoader("LG2세대[FnB3.0]_사용자매뉴얼.pdf")

text_loader_kwargs = {'autodetect_encoding' : True}
loader = DirectoryLoader('./data', show_progress=True, loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
data = loader.load()
 
def split_docs(documents,chunk_size=500,chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs
 
#docs = split_docs(documents)

vectorstore = Chroma.from_documents(documents=data, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever()

from langchain.agents.agent_toolkits import create_retriever_tool

tool = create_retriever_tool(
retriever,
"cusomter_service",
"Searches and returns documents regarding the customer service guide.",
)

tools = [tool]

####################

llm = ChatOpenAI(temperature=0)

# This is needed for both the memory and the prompt
memory_key = "history"

from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder

system_message = SystemMessage(
    content=(
        "You are a nice customer service agent."
        "Do your best to answer the questions. "
        "Feel free to use any tools available to look up "
        "relevant information, only if necessary"
        "If you don't know the answer, just say you don't know. Don't try to make up an answer."
        "Make sure to answer in Korean"
        "너의 역할은 로봇 관련 챗봇 서비스에서 고객의 말에 대답을 하는거야. 고객은 무작정 '뭐가 안됩니다.' 이런식으로 말을 할거고, 너는 고객에게 질물을 해가면서 어떤 문제인지 유추하는거지. 너가 답변한걸 챗봇 서비스 앱의 UI를 통해 고객에게 보여줄거야."
        "로봇 설명서를 보고 단계적으로 고객이 궁금한 분야가 어디인지 줄여나가는 시나리오식 대응을 하자."
    )
)

prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)],
)

agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    return_intermediate_steps=True,
)

# result = agent_executor({"input": "어떻게 Dalpha AI를 사용하나요?"})
# result["output"]

st.title("AI 고객 서비스 상담원")

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        result = agent_executor({"input": prompt})
        for chunk in result['output'].split():
            full_response += chunk + " "
            time.sleep(0.05)

            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
'''

import openai

openai.api_key = "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"

#Use the following pieces of context to answer the users question. If you don't know the answer, just say that you don't know, don't try to make up an answer.
#"마지막으로 고객이 맞다고 하면, 너는 프롬프트를 이용해 제공된 설명서(context) 내용을 기반으로 답변하는 거야, 일반적인 상황 또는 다른 로봇에 대해서 답변할 필요 없어, 메뉴얼에 나온 로봇만 취급하니까"
#"예를 들어서, 선반에 대하여 물어보면, 선반은 트레이로도 사용하는 단어니까 트레이를 말하는건지 물어보는고 관련해서 답변을 하는거지"
#"또한, 로봇을 끌고 가고 싶다. 이런 요청사항은 비상정지 버튼을 누르고 로봇을 끌고 갈 수 있으니까! 가능한 사항이자나?"
#"이런식으로 단계적으로도 생각해보자"
# "첫 번째로 해야할 일은 로봇 메뉴얼(context)에 고객의 질문에 답을 할 수 있는지 보는거야"
# "만약, 답변을 할 수 없다면, 고객이 물어본 질문을 로봇 메뉴얼에 나올법한 단어로 치환해서 고객에게 이런 질문을 하고자 하시는게 맞냐고 물어보자."
# "예를 들어, 로봇에 서랍이 몇개야?라고 고객이 물어보면, 로봇에 있는 트레이/선반을 의미하시는 건가요? 이렇게 역으로 고객에게 물어보는거지"
# '절대 고객에게 직접 메뉴얼을 참조하라고 하지마"
system_template = """
"Make sure to answer in Korean"
"너는 역할은 로봇 관련 챗봇 서비스를 제공하는 에이전트야"
"모든 일은 단계적으로 진행될거야"
"첫 번째로 해야할 일은 로봇 메뉴얼(context)에 고객의 질문에 답을 할 수 있는지 보는거야"
"만약, 답변을 할 수 없다면, 고객이 물어본 질문을 로봇 메뉴얼에 나올법한 단어로 치환해서 고객에게 이런 질문을 하고자 하시는게 맞냐고 물어보자."
"예를 들어, 로봇에 서랍이 몇개야?라고 고객이 물어보면, 로봇에 있는 트레이/선반을 의미하시는 건가요? 이렇게 역으로 고객에게 물어보는거지"
'절대 고객에게 직접 메뉴얼을 참조하라고 하지마"

your Role :
Human Role : 

Task : 
  1. d
  2. 

{context}
------
<hs>
{history}
</hs>
------
Begin!
----------------
Question: {question}
Helpful Answer:"""

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{history}"),
    HumanMessagePromptTemplate.from_template("{question}")
]

prompt = ChatPromptTemplate.from_messages(messages)

from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("LG2세대[FnB3.0]_사용자매뉴얼.pdf")
data = loader.load()

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
docs = text_splitter.split_documents(data)
print(docs)
print('\033[96m'+"########################################################################################" + '\033[0m')
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

embedding=OpenAIEmbeddings(openai_api_key = openai.api_key)
vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

from langchain.chat_models import ChatOpenAI

llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613",openai_api_key = openai.api_key)

question = "로봇에 있는 쟁반같은거 있자나 몇키로까지 견뎌?"


from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectorstore.as_retriever(),
    verbose=True,
    chain_type_kwargs = {"verbose": True, "prompt":prompt, "memory": ConversationBufferMemory(
            memory_key="history",
            input_key="question")})
result = qa_chain({"query": question})

#print('\033[96m'+"########################################################################################" + '\033[0m')
#print(question)
#print('\033[96m'+"########################################################################################" + '\033[0m')
print(result)

#############################################################################################################
'''
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import streamlit as st
import time

import dotenv
dotenv.load_dotenv()

st.title("KT 로봇 서비스 상담원")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # 여기서 위에서 만든 LLM 에이전트를 실행시킵니다. 유저 prompt가 인풋으로 들어갑니다. 
        result = agent_executor({"input": prompt})
        for chunk in result["output"].split():
            full_response += chunk + " "
            time.sleep(0.5)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    '''