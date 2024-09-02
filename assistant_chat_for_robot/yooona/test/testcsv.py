from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma
import streamlit as st
import time
import openai
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.chat_models import ChatOpenAI
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)
from langchain.document_loaders import CSVLoader
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor


OPENAI_API_KEY = "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"
def main():
    print("csv를 불러오는중...")
    # loader1 = PyPDFLoader("./data/LG1세대[FnB2.0]_사용자매뉴얼.pdf")
    # loader2 = PyPDFLoader("./data/LG2세대[FnB3.0]_사용자매뉴얼.pdf")
    # data1 = loader1.load()
    # data2 = loader2.load()

    # data = data1+data2

    loader = CSVLoader("./data/rawdata2.csv", encoding="utf8")

    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    docs = text_splitter.split_documents(data)


    embedding=OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

    retriever = vectorstore.as_retriever()
    tool = create_retriever_tool(
        retriever,
        "KT_VoC_Guide",
        "Searches and returns information regarding the customer service VoC.",
    )

    tools = [tool]




    # This is needed for both the memory and the prompt


    #memory = AgentTokenBufferMemory(memory_key="chat_history", llm=llm, return_messages=True, max_token_limit=2048)
    from langchain.memory import ConversationBufferMemory

    memory = ConversationBufferMemory(memory_key='chat_history', 
                                        return_messages=True,
                                        output_key='output') # using conversation buffer memory to hold past information

    memory_base = []

    def update_system_message(memory, memory_base):

        system_message = SystemMessage(
            content=(
                    '''
                    "형식"       
                    Question: the input question you must answer
                    Thought: 너는 사용자의 VoC가 들어왔을 때, 이에 따른 해결 방법을 내놓는 챗봇이다.
                    Action: the action to take, you should pick one of [{tool_names}]
                    Action Input: the input to the action related to thought
                    Observation: the result of the action
                    ... (this Thought/Action/Action Input/Observation can repeat up to 1 time)
                    Thought: I now know the final answer
                    Final Answer: the final answer to the original input question. you should answer at last.

                    "주요 규칙"
                    1. Make sure to answer in Korean
                    2. 사용자의 VoC를 해석하여 csv의 B열(이슈 신고자 의견)에서 의미적으로 비슷한 값을 찾아라. 그리고 그 값에 맞는 A열(이슈분류) 값을 최종 답변으로 생성해라.
                    3. 무조건 주어진 csv를 참조해서 대답해라.
                    4. csv에서 알 수 없는 내용은 모른다고 대답할 것.
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



    system_message = update_system_message(memory=memory, memory_base=memory_base)


    llm = ChatOpenAI(temperature=0,
                    model="gpt-3.5-turbo",openai_api_key = OPENAI_API_KEY)

    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
    )

    agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)


    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
    )



    print("CSV불러오기 완료!")

    while(True):

        update_system_message(memory=memory, memory_base=memory_base)
        prompt = input('=======================\n대화를 입력하세요:')
        result = agent_executor({"input": prompt})

        print('\nAI:',result['output'])

if __name__ == '__main__':
    main()