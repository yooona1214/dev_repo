from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma

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

import re

#dotenv.load_dotenv()

OPENAI_API_KEY='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'

def main():
    print("필요한 파일을 불러오는중...")
    loader1 = CSVLoader('./data/주행관련VOC테스트_입력_이슈.csv')
    # loader2 = CSVLoader('./data/주행관련VOC테스트_이슈_원인.csv')


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
                    '''
                    사용자 입력을 기반으로 해당되는 이슈분류를 찾아서 답할 것
                    되묻지 말고, 한번에 답을 찾아서 말해라. 답은 "" 콜론 안에 넣어서 말해라.
                    
                    고객님의 이슈는 "이슈분류"에 해당하는 것 같습니다.원인을 파악해드릴게요. 라는 형식을 지켜서 대답할 것
                    
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

    def update_agent(system_message):
        llm = ChatOpenAI(temperature=0,
                        model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)



        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
        )
        
        agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
        
        return agent


    agent_executor = AgentExecutor(
        agent=update_agent(system_message=system_message),
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
    )

    test_llm = ChatOpenAI(temperature=0,
                        model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
    


    # Cause_list = ['매장 내 테이블 배치 변경', '자율주행 오류(멈춤, 금지구역침범 등)', '매장 내 신규 장애물 발생']


    print("파일 불러오기 완료!")

    
    #########
    update_system_message(memory=memory, memory_base=memory_base)
    prompt = input('=======================\n안녕하세요! KT 서비스로봇 에이전트입니다. \n어떤 문제가 있으신가요?:')
    result = agent_executor({"input": prompt})

    print('\nAI:',result['output'])
    
    #result['output']이 pandas 전처리 함수에 들어가서,
    #원인에 대한 리스트를 추출(원인의 자가 조치 가능여부 및 발생 빈도에 따른 우선순위)
    #순서대로 llm에 해당 리스트의 원인을 안내하고, 
    # 해당 원인으로 문제 해결 yes일 경우, 원인 및 출동 안내 후 상담 종료
    # 해당 원인이 문제해결 No일 경우, 원인 리스트의 다음 요소를 물어봄
    # 문제 해결이 yes가 나올 때까지 반복
    
    issue_val = re.findall(r'"([^"]*)"', result['output'])
    path = './data/주행관련VOC테스트_이슈-원인0123.csv'
    
    Cause_list = preprocess_csv(issue_val, path)
    cause_list_to_string = str(Cause_list)
    cause_list_to_string = '\n'+cause_list_to_string 
    

    
    system_message1 = SystemMessage(
            content=(
                    '''
                    아래 원인 데이터프레임을 참고하여 첫번째 행의 원인을 발생시키는 행동을 최근에 한 적 있는지 고객에게 한문장으로 물어봐주세요.

                    \n\n원인 데이터프레임: \n
                    '''
            )
        ) 
    
    system_message2 = SystemMessage(
            content=(
                    '''
                    아래 원인 데이터프레임을 참고하여 두번째 행의 원인을 발생시키는 행동을 최근에 한 적 있는지 고객에게 친절하게 한문장으로 물어봐주세요.
                    if 고객이 n번째 행의 원인이 맞거나, 맞는것 같다고 대답하면 :
                        감사합니다. 출동기사를 연결해드리겠습니다. 라고 말해주세요.
                    elif 고객이 n번째 행의 원인이 아닌 것 같다고 하거나 잘모르겠다고 대답하면:
                        n+1 행의 원인을 다시 물어봐주세요.
                    
                    대화가 반복됨에 따라 n은 1부터 시작해서 n까지 증가한다.
                    n은 아래 원인행의 총 갯수이다
                    n번째 행을 물어보면 
                    감사합니다. 대화를 종료하겠다고 말해주세요.
                    \n\n원인 데이터프레임: \n
                    '''
            )
        )     
    

    sys_prompt1 = system_message1.content+cause_list_to_string
    
    question1 = test_llm.invoke(sys_prompt1) 
    print('\nAI:',question1)        
    
    sys_prompt2 = system_message2.content+cause_list_to_string
    
    while(True):

        #print(new_sys_prompt) 
        
        
        user_answer=input('대답해주세요:')
        question = test_llm.invoke( sys_prompt2+'고객의 대답:'+user_answer) 

        chat_history = 'chat_history:\n고객:'+user_answer +'\nAI:'+str(question)
        sys_prompt = sys_prompt2+'\n'+chat_history

        print('\nAI:', question)
        
        print('\n\n\n\n\n\nsys_prompt:',sys_prompt)
        

          
        

        
        
        


        
def preprocess_csv(issue_value, csv_path):

    import pandas as pd
    for issue in issue_value:

        df = pd.read_csv(csv_path)

        selected_rows = df[df['이슈분류'] == issue]

        # 원인을 탐색하고 각 원인이 얼마나 발생했는지 정규화하여 저장
        issue_counts = selected_rows['원인(원인별명)'].value_counts(normalize=True)

        # 각 원인에 대한 '고객조치가능여부' 값 가져오기
        customer_actions = selected_rows.groupby('원인(원인별명)')['고객조치가능여부'].first()
        detail_actions = selected_rows.groupby('원인(원인별명)')['조치 방법'].first()

        # DataFrame으로 변환
        result_df = pd.DataFrame({
            '원인': issue_counts.index,
            '고객조치가능여부': customer_actions.loc[issue_counts.index].values,
            '빈도': issue_counts.values,
            '조치 방법': detail_actions.loc[issue_counts.index].values
        })

        result_df = result_df.sort_values(by=['고객조치가능여부', '빈도'], ascending=[False, False])
        # result_df = result_df.sort_values(by=['빈도'], ascending=[False])
        print('--------------')
        print(result_df)
        print('--------------')

    print(type(result_df))
    return result_df


if __name__ == '__main__':
    main()