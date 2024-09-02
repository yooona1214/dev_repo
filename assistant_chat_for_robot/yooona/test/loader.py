from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma
import streamlit as st
import time
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.chat_models import ChatOpenAI
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory


# OpenAI API KEY
API_KEY = "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"


class Loader:
    def __init__(self):
        self.memory = None
        self.memory_base = None
        self.agent_executor = None

    def update_system_message(self, memory, memory_base):

        system_message = SystemMessage(
            content=(
                    '''
                    "형식"       
                    Question: the input question you must answer
                    Thought: you should always think about what to do. If the words in question is not related to robot manual, you should replace that word with the simillar word in manual. 
                    Action: the action to take, you should pick one of [{tool_names}]
                    Action Input: the input to the action related to thought
                    Observation: the result of the action
                    ... (this Thought/Action/Action Input/Observation can repeat up to 1 time)
                    Thought: I now know the final answer
                    Final Answer: the final answer to the original input question. you should answer at last.

                    "주요 규칙"
                    1. Make sure to answer in Korean
                    2. 다른 일반적인 로봇을 이야기하지 말 것
                    3. 절대 고객에게 직접 manual을 참조하라고 말하지 말 것
                    4. max_iteration 안에 무조건 final answer를 답해라
                    '''
            )
        )

        memory_content = memory.buffer_as_str
        memory_base.append(memory_content)
        memory_message = SystemMessage(content=''.join(memory_base))    

        #print('메모리 기록:', memory_base)


        updated_memory = system_message.content + memory_message.content
        #print('updated_memory:', updated_memory)

        #시스템 메시지 프롬프트 업데이트
        system_message = SystemMessage(content=updated_memory)


        return system_message


    def load_all(self):

        # PDF 불러오기
        loader1 = PyPDFLoader("./data/LG1세대[FnB2.0]_사용자매뉴얼.pdf")
        loader2 = PyPDFLoader("./data/LG2세대[FnB3.0]_사용자매뉴얼.pdf")
        data1 = loader1.load()
        data2 = loader2.load()
        data = data1+data2

        # 벡터 스토어 만들기
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        docs = text_splitter.split_documents(data)


        embedding=OpenAIEmbeddings(openai_api_key = API_KEY)
        vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

        retriever = vectorstore.as_retriever()
        tool = create_retriever_tool(
            retriever,
            "LG_customer_service_guide",
            "Searches and returns information regarding the customer service guide.",
        )

        tools = [tool]
        self.memory = ConversationBufferMemory(memory_key='chat_history', 
                                            return_messages=True,
                                            output_key='output') # using conversation buffer memory to hold past information

        self.memory_base = []

        system_message = self.update_system_message(memory=self.memory, memory_base=self.memory_base)

        llm = ChatOpenAI(temperature=0.2,
                        model="gpt-3.5-turbo", openai_api_key=API_KEY)

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
        )

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)


        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=False,
            return_intermediate_steps=True,
        )

        print("PDF불러오기 완료!")



    def chatwithGPT(self, kakaomessages):

        self.update_system_message(memory=self.memory, memory_base=self.memory_base)
        print("-----------------------------------------")
        print('\nKAKAO USER:',kakaomessages)
        result = self.agent_executor({"input": kakaomessages})

        print('AI:',result['output'])

        return result['output']
