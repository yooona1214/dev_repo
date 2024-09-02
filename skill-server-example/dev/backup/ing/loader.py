from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma
import streamlit as st
import time
from langchain.document_loaders import PyPDFLoader, CSVLoader
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
import re
# OpenAI API KEY
API_KEY = "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"


class Loader_Rag:
    def __init__(self):
        self.memory = None
        self.memory_base = None
        self.agent_executor = None

        self.user_agents = {}

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
            verbose=True,
            return_intermediate_steps=True,
        )

        print("PDF불러오기 완료!")

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

    def create_or_load_user_agent(self, user_id):

        # user id 확인
        if user_id not in self.user_agents:
            # 없으면 해당 id에 맞게 agent 생성
            user_agent = self.create_new_agent(user_id)
            self.user_agents[user_id] = user_agent
        else:    
            print("USER: ", user_id, " AGENT IS LOADED")

        return self.user_agents[user_id]        
    
    def create_new_agent(self, user_id):

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

        print("USER: ", user_id, " AGENT IS CREATED")




    def chatwithGPT(self, kakaomessages):

        self.update_system_message(memory=self.memory, memory_base=self.memory_base)
        print('KAKAO USER:',kakaomessages)
        result = self.agent_executor({"input": kakaomessages})

        print('AI:',result['output'])

        print("-----------------------------------------")
        return result['output']



class Loader_Voc:
    def __init__(self):
        self.memory = None
        self.memory_base = []
        self.agent_executor = None
        self.llm = None
        self.user_agents = {}
        self.path = './data/주행관련VOC테스트_이슈-원인0123.csv'

    def load_all(self):

        print("필요한 파일을 불러오는중...")
        loader1 = CSVLoader('./data/주행관련VOC테스트_입력_이슈.csv')
        data1 = loader1.load()
        issue_data1 = data1


        def create_vector_store_as_retriever(data, str1, str2):

            text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
            docs = text_splitter.split_documents(data)


            embedding=OpenAIEmbeddings(openai_api_key =API_KEY)
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



        system_message = self.update_system_message(memory=memory, memory_base=self.memory_base)


        self.llm = ChatOpenAI(temperature=0,
                        model="gpt-3.5-turbo", api_key=API_KEY)


        from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent, create_openai_functions_agent

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
        )
        
        
        
        agent = create_openai_functions_agent(llm=self.llm , tools=tools, prompt=prompt)
        

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            return_intermediate_steps=True,
        )


    def update_system_message(self, memory, memory_base):

            system_message = SystemMessage(
                content=(
                        '''
                        사용자 입력을 기반으로 해당되는 이슈분류를 찾아서 답할 것
                        되묻지 말고, 한번에 답을 찾아서 말해라. 답은 "" 콜론 안에 넣어서 말해라.
                        
                        고객님의 이슈는 "이슈분류"에 해당하는 것 같습니다. 라는 형식을 지켜서 대답할 것
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


        
    def preprocess_csv(self, issue_value, csv_path):

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

        print(type(result_df))
        return result_df

    def find_cause(self, kakaomessages):
        print('KAKAO USER:',kakaomessages)
        
        self.update_system_message(memory=self.memory, memory_base=self.memory_base)
        result = self.agent_executor({"input": kakaomessages})
        print('AI:',result['output'])

        import re
        issue_val = re.findall(r'"([^"]*)"', result['output'])
        Cause_list = self.preprocess_csv(issue_val, self.path)

        return Cause_list

    def findCausewithGPT(self, Cause_list, index):

        for index, row in Cause_list.iterrows():


            #question = f"고객님의 이슈에 대한 원인은 '{row['원인']}'으로 보입니다. 맞으실까요?"
            #user_answer = input(question).lower()
            
            question = self.llm.invoke(str({row['원인']}) +'을 발생시키는 행동을 최근에 한 적 있는지 친절하게 한문장으로 물어봐주세요.') 
            print('\nAI:',question)
            
            # 입력이 'yes' 또는 'no'가 아니라면 다시 입력 받기
            #while user_answer not in ['yes', 'no']:
            #    print("잘못된 입력입니다. 'yes' 또는 'no'로 입력해주세요.")
            #    user_answer = input(question).lower()
            
            #ans = input('=======================\n대답을 입력하세요:')        
            
            user_answer = input('대화를 입력해주세요:')
            result = self.llm.invoke('prompt:고객의 말이 긍정이거나 애매하면 yes, 부정이면 no를 반환해라. 고객의 말:'+user_answer)
            #print(result)   
            user_answer = str(result)         
            #print(type(result))
            #print(user_answer)
            yes = "content='yes'"
            no = "content='no'"            
            
            if user_answer == yes:
                if row['고객조치가능여부'] == True:
                    ans = self.llm.invoke(str(row['조치 방법'])+'을 통해 문제를 해결해보라고 권유 해주는 문장을 말해주세요.')
                    print('\nAI:',ans)
                    #print(f"'{row['조치 방법']}'으로 한번 해결 해보시겠어요?")
                    
                    break
                
                if row['고객조치가능여부'] == False:
                    ans1 = self.llm.invoke('이용해주셔서 감사합니다. 라고 말하고, '+ str(row['원인'])+ '을'+ '해결하기 위해 고객님께 직원을 연결해드린다고 대답해주세요.')
                    
                    print('\nAI:',ans1)
                    break

            elif user_answer == no:
                print('\nAI: 죄송합니다. 다른 원인을 알아볼게요.')
            
        print("-----------------------------------------")
        return result['output']