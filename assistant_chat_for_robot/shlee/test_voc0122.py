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
    loader1 = CSVLoader('assistant_chat_for_robot/shlee/data/주행관련VOC테스트_입력_이슈.csv')
    loader2 = CSVLoader('assistant_chat_for_robot/shlee/data/주행관련VOC테스트_이슈_원인.csv')


    data1 = loader1.load()
    #data2 = loader2.load()

    
    issue_data1 = data1
    #issue_data2 = data2
    

    
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
    
    tool = create_vector_store_as_retriever(data= issue_data1, str1="KT_Robot_Customer_Issue_Guide", str2="Find appropriate issue categories from user input")
    

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
                    
                    "사용자 입력을 기반으로 해당되는 이슈분류를 찾아서 답할 것"
                    "되묻지 말고, 한번에 답을 찾아서 말해라."
                    "단답형으로 응답."
                    
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

    test_llm = llm
    


    Cause_list = ['매장 내 테이블 배치 변경', '자율주행 오류(멈춤, 금지구역침범 등)', '매장 내 신규 장애물 발생']


    print("파일 불러오기 완료!")

    
    while(True):

        update_system_message(memory=memory, memory_base=memory_base)
        prompt = input('=======================\n어떤 문제가 있으신가요?:')
        result = agent_executor({"input": prompt})

        print('\nAI:',result['output'])
        
        #result['output']이 pandas 전처리 함수에 들어가서,
        #원인에 대한 리스트를 추출(원인의 자가 조치 가능여부 및 발생 빈도에 따른 우선순위)
        #순서대로 llm에 해당 리스트의 원인을 안내하고, 
        # 해당 원인으로 문제 해결 yes일 경우, 원인 및 출동 안내 후 상담 종료
        # 해당 원인이 문제해결 No일 경우, 원인 리스트의 다음 요소를 물어봄
        # 문제 해결이 yes가 나올 때까지 반복
        
        print('\n가능한 원인리스트:',Cause_list)
        
        for i in range(len(Cause_list)):
            print('고객님의 이슈에 대한 원인은 '+Cause_list[i]+ '으로 추측됩니다. 맞으십니까?')
            ans = input('=======================\n대답을 입력하세요:')        
            result = test_llm.invoke('prompt:고객의 말이 긍정이면 yes, 부정이면 no를 반환해라. 고객의 말:'+ans)
            
            #print(result)   
            result = str(result)         
            #print(type(result))
            print(result)
            yes = "content='yes'"
            no = "content='no'"
            if result == yes:
                print('상담 종료, 해당 문제 조치를 위해 고객님께 A/S기사를 보내도록 하겠습니다.')
                break
            elif result == no:
                print('죄송합니다. 그 문제가 아니라면, 고객님의 이슈에 대한 원인은 '+Cause_list[i]+ '으로 추측됩니다. 맞으십니까?')
            
            result = None
        
        
        
        

if __name__ == '__main__':
    main()