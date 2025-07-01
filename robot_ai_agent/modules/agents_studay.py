"""llm server"""

import os
import json
import csv

from modules.rag_issue import CreateVectorstore
from modules.create_react_agent_w_history import (
    create_openai_functions_agent_with_history,
)
from modules.prompts_studay import (
    GENERAL_PROMPTS,
    GENERAL_INPUTS,
    SYMPTOM_PROMPTS,
    SYMPTOM_INPUTS,
    MANUAL_PROMPTS,
    MANUAL_INPUTS,
    CAUSE_PROMPTS,
    CAUSE_INPUTS,
    ACTION_PROMPTS,
    ACTION_INPUTS,
    ROUTING_INPUTS,
    ROUTING_PROMPTS,
    ERROR_PROMPTS,
    ERROR_INPUTS,
)

import importlib.resources as pkg_resources
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.agents import AgentExecutor, AgentType
from langchain_openai import ChatOpenAI

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent



# LangSmith 추적 기능을 활성화합니다. (선택적)
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = (
    "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key
)



class LLMagent:
    """LLM Agent"""

    def __init__(self):

        self.user_agents = {}
        self.user_chat_history = {}
        self.tool_symptom = []
        self.tool_manual = []

        self.routing_agent = None
        self.general_agent = None
        self.symptom_agent = None
        self.pandas_agent = None
        self.cause_agent = None
        self.action_agent = None
        self.error_agent = None

        self.manual_agent = None

    def load_all(self):
        """Load all files that you need"""
        # Data 로드
        print("필요한 파일을 불러오는중...")
        
        
        
        csv_path = pkg_resources.files("modules").joinpath("studay_data/LG0429.csv")
        csv_path2 = pkg_resources.files("modules").joinpath("studay_data/LG_Error_0513.csv")
        csv_path3 = pkg_resources.files("modules").joinpath("studay_data/LG_Error_0403.csv")
       
       
        pdf_path = pkg_resources.files("modules").joinpath("studay_data/LG2세대[FnB3.0]_사용자매뉴얼.pdf")
        pdf_path2 = pkg_resources.files("modules").joinpath("studay_data/베어_사용자매뉴얼.pdf")
        
        # VOC데이터
        loader1 = CSVLoader(csv_path)
        loader2 = CSVLoader(csv_path3)
        df_for_pandas = pd.read_csv(csv_path)
        df_for_pandas_error = pd.read_csv(csv_path2)

        loader3 = PyPDFLoader(pdf_path)
        loader4 = PyPDFLoader(pdf_path2)
        data1 = loader1.load()
        data2 = loader2.load()
        data3 = loader3.load()
        data4 = loader4.load()

        issue_data = data1
        error_data = data2
        manual_lg_data = data3
        manual_bear_data = data4

        # tool 선언
        rag_issue = CreateVectorstore.create_vector_store_as_retriever_lg_voc(
            data=issue_data,
            str1="KT_Robot_Customer_Issue_Guide",
            str2="This is a data containing symptoms, causes of symptoms, and solutions for the causes.",
        )

        rag_error = CreateVectorstore.create_vector_store_as_retriever_error(
            data=error_data,
            str1="KT_Robot_Error_Guide",
            str2="This is a data containing error code, causes of error code, and solutions for the error code.",
        )

        rag_lg_manual = CreateVectorstore.create_vector_store_as_retriever_lg_manual(
            data=manual_lg_data, str1="LG_Robot_Manual_Guide", str2="This is LG robot manual."
        )
        
        rag_bear_manual = CreateVectorstore.create_vector_store_as_retriever_bear_manual(
            data=manual_bear_data, str1="Bear_Robot_Manual_Guide", str2="This is Bear robot manual."
        )

        # LLM 모델 선택
        llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY, temperature=0)
        llm_4_t = ChatOpenAI(
            model="gpt-4-0125-preview", api_key=OPENAI_API_KEY, temperature=0
        )
        llm_3_5 = ChatOpenAI(
            model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY, temperature=0
        )
        # llm_4_o = ChatOpenAI(
        #     model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0
        # )
        llm_4_o = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0)

        llm_model = llm_4_o

        self.tool_symptom = [rag_issue]
        self.tool_error = [rag_error]
        self.tool_manual = [rag_lg_manual, rag_bear_manual]

        routing_prompt = PromptTemplate(
            input_variables=ROUTING_INPUTS, template=ROUTING_PROMPTS
        )

        general_prompt = PromptTemplate(
            input_variables=GENERAL_INPUTS, template=GENERAL_PROMPTS
        )

        symptom_prompt = PromptTemplate(
            input_variables=SYMPTOM_INPUTS, template=SYMPTOM_PROMPTS
        )

        cause_prompt = PromptTemplate(
            input_variables=CAUSE_INPUTS, template=CAUSE_PROMPTS
        )

        action_prompt = PromptTemplate(
            input_variables=ACTION_INPUTS, template=ACTION_PROMPTS
        )

        error_prompt = PromptTemplate(
            input_variables=ERROR_INPUTS, template=ERROR_PROMPTS
        )
        # - Cause expert: Based on the symptoms derived by the symptom identification expert, using only causes in the ‘Cause’ column of the csv file, but use them as is and ask the customer one by one in a 20-question game format, starting with the most overlapping cause that causes the symptom among the causes in the 'Cause' column.

        manual_prompt = PromptTemplate(
            input_variables=MANUAL_INPUTS, template=MANUAL_PROMPTS
        )

        self.routing_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, routing_prompt
        )

        self.general_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, general_prompt
        )

        self.symptom_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, symptom_prompt
        )

        self.pandas_agent = create_pandas_dataframe_agent(
            llm=llm_model,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            df=df_for_pandas,
            verbose=True,
            prefix="Please refer only to the loaded data, find all causes corresponding to the symptom, and then list them in order of frequency. Please answer all questions concisely in Korean.",
            allow_dangerous_code=True
            
        )

        self.error_pandas_agent = create_pandas_dataframe_agent(
            llm=llm_model,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            df=df_for_pandas_error,
            verbose=True,
            prefix="Please refer only to the loaded data, find specific column corresponding to the Error Code, and then Error Code의 원인과 조치방법에 대해 상담원 처럼 대응해.(example: 고객님의 에러에 대한 원인은 ~이며, 조치방법은 아래와 같습니다.\n\n 우선, 고객님께서 직접 조치할 수 있는 방법은 ~이고, \n\n 만약 직접 조치하셔도 잘 안될 경우, 출동 서비스를 통해 문제 해결에 도움을 드릴 수 있습니다.). Please answer all questions concisely in Korean.",
            number_of_head_rows = df_for_pandas_error.shape[0],
            allow_dangerous_code=True
            
        )
        
        self.cause_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, cause_prompt
        )
        self.action_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, action_prompt
        )

        self.error_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_error, error_prompt
        )

        self.manual_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_manual, manual_prompt
        )
        
        self.final_response = None
        print("완료")

    def identify_user(self, user_id, utterance):
        """identify user and get messages"""
        user_id = user_id
        message = utterance

        if user_id not in self.user_chat_history:
            self.user_chat_history[user_id] = []
            print("USER: ", user_id, " AGENT IS INITIALIZED")

        else:
            print("USER: ", user_id, " AGENT IS LOADED")
        # self.callback_agent(user_id, message)
        self.identify_menu(user_id, message)
        
        return self.final_response

    def identify_menu(self, user_id, message):
        if message in ["LG로봇 사용법 문의", "베어로봇 사용법 문의", "LG로봇 고장신고", "LG로봇 에러조회"]:
            '''메뉴 선택'''
            if len(self.user_chat_history[user_id]) == 0 :    
                '''챗 히스토리가 빈값이면 새로운 채팅이 시작된 경우'''
                #self.callback_agent(user_id, message)
                greeting_message = f"안녕하세요! 고객님 {message} 상담을 진행하겠습니다. 어떤 도움이 필요하신가요?"
                self.send_message(user_id=user_id, message=greeting_message)
                self.user_chat_history[user_id].extend(
                    [
                        HumanMessage(content=message, id=user_id),
                        AIMessage(content=greeting_message, id=user_id)
                    ] 
                )

            else: 
                trans_message = f"상담 메뉴를 전환하셨습니다. 기존 상담을 종료하고 {message} 상담을 진행하겠습니다. 어떤 도움이 필요하신가요?"
                '''챗 히스토리가 있으면 중간에 메뉴 전환 된 경우'''
                self.reset_history(user_id=user_id)
                self.send_message(user_id=user_id, message=trans_message)

                self.user_chat_history[user_id].extend(
                    [
                        HumanMessage(content=message, id=user_id),
                        AIMessage(content=trans_message, id=user_id)
                    ]
                )

        else:
            '''일반 대화 '''
            self.callback_agent(user_id, message)
            
    


    def callback_agent(self, user_id, message):
        """callback user id and messages from LLM"""

        # 대화 종료시 chat history초기화
        if message == "!종료":
            self.reset_history(user_id=user_id)
            self.send_message(
                    user_id=user_id,
                    #message=routed_result + "\n\n\n" + general_response["output"],
                    message="고객님, 서비스 로봇을 이용하시면서 불편한 점이나 궁금한 사항이 있으시면 언제든지 말씀해 주세요. 도와드릴 수 있는 모든 정보를 제공해 드리겠습니다. 무엇이든 물어보세요! 😊",
                )


        else:
            chat_history = self.user_chat_history[user_id]

            routing_agent_executor = AgentExecutor(
                agent=self.routing_agent, tools=self.tool_symptom, verbose=True,
            )
            routing_response = routing_agent_executor.invoke(
                {"input": message, "chat_history": chat_history}
            )

            routed_result = routing_response["output"]

            # self.send_message(user_id=user_id, message=routed_result)

            if "General" in routed_result:

                general_agent_executor = AgentExecutor(
                    agent=self.general_agent, tools=self.tool_symptom, verbose=True
                )
                general_response = general_agent_executor.invoke(
                    {"input": message, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        HumanMessage(content=message, id=user_id),
                        AIMessage(content=routing_response["output"], id=user_id),
                        AIMessage(content=general_response["output"], id=user_id),
                    ]
                )
                self.send_message(
                    user_id=user_id,
                    #message=routed_result + "\n\n\n" + general_response["output"],
                    message=general_response["output"],
                )

            elif "Symptom" in routed_result:
                ask_symptom = (
                    "KT_Robot_Customer_Issue_Guide를 검색하여, 고객의 발화("
                    + message
                    + ")에 적합한 증상을 하나 골라서 한 문장으로 대답해주세요.(ex. 고객님의 증상은 ~~으로 분류됩니다.)"
                )

                symptom_agent_executor = AgentExecutor(
                    agent=self.symptom_agent, tools=self.tool_symptom, verbose=True, handle_parsing_errors=True
                )
                symptom_response = symptom_agent_executor.invoke(
                    {"input": ask_symptom, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        HumanMessage(content=message, id=user_id),
                        AIMessage(content=routing_response["output"], id=user_id),
                        AIMessage(content=symptom_response["output"], id=user_id),
                    ]
                )
                response_causes = self.pandas_agent.invoke(
                    "고객의 입력으로부터 도출된 증상:" + symptom_response["output"]
                )

                chat_history.extend(
                    [AIMessage(content=response_causes["output"], id=user_id)]
                )

                ask_cause = "나열된 순서대로 원인이 발생한적 있는지 스무고개 형태로 파악해주세요. 질문을 먼저 시작해주세요."
                cause_agent_executor = AgentExecutor(
                    agent=self.cause_agent, tools=self.tool_symptom, verbose=True, handle_parsing_errors=True
                )
                cause_response = cause_agent_executor.invoke(
                    {"input": ask_cause, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=ask_cause, id=user_id),
                        AIMessage(content=cause_response["output"], id=user_id),
                    ]
                )

                self.send_message(
                    user_id=user_id,
                    message= symptom_response["output"]
                    + "\n\n\n"
                    + cause_response["output"],
                )
                


            elif "Cause" in routed_result:
                cause_agent_executor = AgentExecutor(
                    agent=self.cause_agent, tools=self.tool_symptom, verbose=True
                )
                cause_response = cause_agent_executor.invoke(
                    {"input": message, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=message, id=user_id),
                        AIMessage(content=cause_response["output"], id=user_id),
                    ]
                )

                self.send_message(
                    user_id=user_id,
                    message=cause_response["output"],
                )

            elif "Action" in routed_result:
                action_agent_executor = AgentExecutor(
                    agent=self.action_agent, tools=self.tool_symptom, verbose=True
                )
                action_response = action_agent_executor.invoke(
                    {"input": message, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=message, id=user_id),
                        AIMessage(content=action_response["output"], id=user_id),
                    ]
                )

                self.send_message(
                    user_id=user_id,
                    message=action_response["output"],
                )

            elif "Error" in routed_result:
                # error_agent_executor = AgentExecutor(
                #     agent=self.error_agent, tools=self.tool_error, verbose=True
                # )
                # error_response = error_agent_executor.invoke(
                #     {"input": message, "chat_history": chat_history}
                # )

                e_input = f"고객의 에러코드 관련 발화는 {message} 입니다."
                #test = f"Error code {message} row 의 column2, column3, column4 값은 뭐니"
                
                error_response = self.error_pandas_agent.invoke(
                    e_input
                )
                # 
                chat_history.extend(
                    [   AIMessage(content=error_response["output"], id=user_id),
                    ]
                )   
                

                self.send_message(
                    user_id=user_id,
                    message=error_response["output"],
                )

            elif "Manual" in routed_result:
                ask_manual = (
                    message + "라는 고객의 질문에 대하여 로봇 매뉴얼을 검색하여 답해주세요."
                )
                manual_agent_executor = AgentExecutor(
                    agent=self.manual_agent, tools=self.tool_manual, verbose=True
                )
                response = manual_agent_executor.invoke(
                    {"input": ask_manual, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=ask_manual, id=user_id),
                        AIMessage(content=response["output"], id=user_id),
                    ]
                )

                self.send_message(user_id=user_id, message=response["output"])

            self.logging_history(user_id=user_id, history=chat_history)

    


    # def send_message(self, user_id, message):
    #     """Publish and send messages to RMQ"""
    #     connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    #     channel = connection.channel()

    #     channel.queue_declare(
    #         queue=user_id
    #     )  # user id별로 RMQ에 return 하는 메시지의 채널을 생성
    #     channel.basic_publish(exchange="", routing_key=user_id, body=message)
    #     print(f"Sent message.\n{message}")

    #     connection.close()
    
    def send_message(self, user_id, message):
        """Return message to API"""
        self.final_response = message
        # print(self.final_response)

    def logging_history(self, user_id, history):
        """Logging history for users"""
        history_path = pkg_resources.files("modules").joinpath("studay_data/history/history_"+ user_id + ".csv")

        f = open(history_path, "w", encoding="utf-8")
        writer = csv.writer(f)
        for row in history:
            writer.writerow(row)
        f.close()

    def reset_history(self, user_id):
        self.user_chat_history[user_id] = []
        print("RESET THE CHATHISTORY")
