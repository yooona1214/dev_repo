from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma
import dotenv

import openai
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.chat_models import ChatOpenAI
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent, create_openai_functions_agent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor

from langchain_community.tools.convert_to_openai import format_tool_to_openai_function



#dotenv.load_dotenv()

OPENAI_API_KEY='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'

def main():
    print("필요한 파일을 불러오는중...")
    loader1 = CSVLoader('assistant_chat_for_robot/shlee/data/VOC_list.csv')
    loader2 = PyPDFLoader("assistant_chat_for_robot/shlee/data/LG1세대[FnB2.0]_사용자매뉴얼.pdf")
    loader3 = PyPDFLoader("assistant_chat_for_robot/shlee/data/LG2세대[FnB3.0]_사용자매뉴얼.pdf")

    data1 = loader1.load()
    data2 = loader2.load()
    data3 = loader3.load()
    
    issue_data = data1
    manual_data = data2 + data3

    
    #print(data)

    def create_vector_store_as_retriever(data, str1, str2):

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
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
    
    tool1 = create_vector_store_as_retriever(data= manual_data, str1="LG_Robot_User_Manual", str2="Based on the customer's question, find the appropriate information in the customer manual and answer it.")
    tool2 = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", str2="Find the appropriate cause for customer inquiries and respond with appropriate action results.")
    

    tools = [tool1, tool2]




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

                    {tools}

                    Use the following format:

                    Question: the input question you must answer
                    Thought: you should always think about what to do
                    Action: the action to take, should be one of [{tool_names}]
                    Action Input: the input to the action
                    Observation: the result of the action
                    ... (this Thought/Action/Action Input/Observation can repeat N times)
                    Thought: I now know the final answer
                    Final Answer: the final answer to the original input question

                    Begin!

                    Question: {input}
                    Thought:{agent_scratchpad}
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
                    model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)



    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
    )
      
    
    
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    


    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
    )



    print("PDF불러오기 완료!")

    while(True):

        update_system_message(memory=memory, memory_base=memory_base)
        prompt = input('=======================\n대화를 입력하세요:')
        result = agent_executor({"input": prompt})

        print('\nAI:',result['output'])

if __name__ == '__main__':
    main()