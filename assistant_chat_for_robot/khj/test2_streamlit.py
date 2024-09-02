from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import Chroma
import dotenv
dotenv.load_dotenv()
import streamlit as st
import time
import openai

openai.api_key = "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"
# loader = WebBaseLoader("https://dalpha.so/ko/howtouse?scrollTo=custom")
# data = loader.load()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
# all_splits = text_splitter.split_documents(data)

# vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("LG2세대[FnB3.0]_사용자매뉴얼.pdf")
data = loader.load()

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
docs = text_splitter.split_documents(data)

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

embedding=OpenAIEmbeddings(openai_api_key = openai.api_key)
vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

retriever = vectorstore.as_retriever()

from langchain.agents.agent_toolkits import create_retriever_tool

tool = create_retriever_tool(
    retriever,
    "LG_customer_service_guide",
    "Searches and returns information regarding the customer service guide.",
)
print(tool)
tools = [tool]

from langchain.chat_models import ChatOpenAI
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
        "너의 역할 : 로봇을 판매하는 회사에서 운영하는 챗봇 서비스를 제공하는 에이전트"
        "챗봇을 이용하는 사용자 : 로봇을 구매하여 사용하는 고객"
        
        "[주요 규칙]"
          "1. Make sure to answer in Korean"
          "2. 모든 일은 단계적으로 진행"
          "3. 고객의 question이 manual에 나와 있지 않다면, 로봇 manual에 존재할법한 단어로 치환하여 고객에게 다시 확인 받을 것"
              "- 예를 들어, 고객이 '로봇에 있는 쟁반같은거가 물건을 얼마나 실을 수 있어?'라고 한다면, 쟁반은 트레이/선반 등의 단어로 치환하고 얼마나 실을 수 있어라는 문장은 트레이 무게 제한/적재용량 등으로 치환"
          "4. 다른 일반적인 로봇을 이야기하지 말 것"
          "5. 절대 고객에게 직접 manual을 참조하라고 말하지 말 것"
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

        result = agent_executor({"input": prompt})
        for chunk in result['output'].split():
            full_response += chunk + " "
            time.sleep(0.05)

            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
