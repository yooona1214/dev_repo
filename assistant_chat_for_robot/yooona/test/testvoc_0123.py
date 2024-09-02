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
                    
<<<<<<< HEAD
                    "사용자 입력을 기반으로 해당되는 이슈분류를 찾아서 답할 것"
                    "되묻지 말고, 한번에 답을 찾아서 말해라."
                    "찾은 이슈분류만 단답형으로 최종 답변해."
=======
                    고객님의 이슈는 "이슈분류"에 해당하는 것 같습니다. 라는 형식을 지켜서 대답할 것
                    '''
>>>>>>> 6e7747ce95243cb8e47a75e4060eba40152418f1
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
    


    # Cause_list = ['매장 내 테이블 배치 변경', '자율주행 오류(멈춤, 금지구역침범 등)', '매장 내 신규 장애물 발생']


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
        
<<<<<<< HEAD
        if '"' in result['output']:
            issue_val = re.findall(r'"([^"]*)"', result['output'])
        else:
            issue_val = [result['output']]
=======
        issue_val = re.findall(r'"([^"]*)"', result['output'])
>>>>>>> 6e7747ce95243cb8e47a75e4060eba40152418f1
        path = './data/주행관련VOC테스트_이슈-원인0123.csv'
        
        Cause_list = preprocess_csv(issue_val, path)


        for index, row in Cause_list.iterrows():


            question = f"고객님의 이슈에 대한 원인은 '{row['원인']}'으로 보입니다. 맞으실까요? (yes/no): "
            user_answer = input(question).lower()
            
            # 입력이 'yes' 또는 'no'가 아니라면 다시 입력 받기
            #while user_answer not in ['yes', 'no']:
            #    print("잘못된 입력입니다. 'yes' 또는 'no'로 입력해주세요.")
            #    user_answer = input(question).lower()
            
            #ans = input('=======================\n대답을 입력하세요:')        
            result = test_llm.invoke('prompt:고객의 말이 긍정이면 yes, 부정이면 no를 반환해라. 고객의 말:'+user_answer)
            #print(result)   
            user_answer = str(result)         
            #print(type(result))
            print(user_answer)
            yes = "content='yes'"
            no = "content='no'"            
                
            if user_answer == 'yes':
                if row['고객조치가능여부'] == True:
                    print(f"해당 원인에 대한 조치방법은 다음과 같습니다: '{row['조치 방법']}'.")
                    break
                
                if row['고객조치가능여부'] == False:
                    print('상담 종료, 해당 문제 조치를 위해 고객님께 A/S기사를 보내도록 하겠습니다.')
                    break

            elif user_answer == 'no':
                print(f"죄송합니다.")
            


        
def preprocess_csv(issue_value, csv_path):

    import pandas as pd

    ### 값이 여러개 나온다면,,, 우야노
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


    return result_df


if __name__ == '__main__':
    main()