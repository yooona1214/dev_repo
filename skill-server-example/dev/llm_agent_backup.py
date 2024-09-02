"""llm server"""

import os
import json
import csv

import pika
from custom_tools.issue_rag import create_vector_store_as_retriever
from custom_tools.create_react_agent_w_history import (
    create_openai_functions_agent_with_history,
)
from custom_prompts.prompts import (
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
)
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.agents import AgentExecutor, AgentType
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent


OPENAI_API_KEY = "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"

# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = (
    "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key
)

# RabbitMQ 연동 위한 채널 큐 설정
HOST_NAME = "localhost"
QUEUE_NAME = "Chat"
# QUEUE_NAME2 = "Chat2"


class LLMagent:
    """LLM Agent"""

    def __init__(self):

        self.user_agents = {}
        self.user_chat_history = {}
        self.tool_symptom = []
        self.tool_manual = []

        self.general_agent = None
        self.symptom_agent = None
        self.pandas_agent = None
        self.cause_agent = None
        self.action_agent = None
        self.manual_agent = None

    def load_all(self):
        """Load all files that you need"""
        # Data 로드
        print("필요한 파일을 불러오는중...")

        # VOC데이터
        loader1 = CSVLoader("./data/LG0429.csv")
        df_for_pandas = pd.read_csv("./data/LG0429.csv")

        # loader2 = CSVLoader('./data/베어_0226.csv')
        loader3 = PyPDFLoader("./data/LG1세대[FnB2.0]_사용자매뉴얼.pdf")
        data1 = loader1.load()

        data3 = loader3.load()

        issue_data = data1
        manual_data = data3

        # tool 선언
        rag_issue = create_vector_store_as_retriever(
            data=issue_data,
            str1="KT_Robot_Customer_Issue_Guide",
            str2="This is a data containing symptoms, causes of symptoms, and solutions for the causes.",
        )

        rag_manual = create_vector_store_as_retriever(
            data=manual_data, str1="LG_Robot_Manual_Guide", str2="This is robot manual."
        )

        """ollama test"""

        from langchain_community.chat_models.ollama import ChatOllama

        llm_eve = ChatOllama(model="EEVE-Korean-10.8B:latest")

        # LLM 모델 선택
        llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
        llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
        llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

        llm_model = llm_4_t

        self.tool_symptom = [rag_issue]
        self.tool_manual = [rag_manual]

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

        # - Cause expert: Based on the symptoms derived by the symptom identification expert, using only causes in the ‘Cause’ column of the csv file, but use them as is and ask the customer one by one in a 20-question game format, starting with the most overlapping cause that causes the symptom among the causes in the 'Cause' column.

        manual_prompt = PromptTemplate(
            input_variables=MANUAL_INPUTS, template=MANUAL_PROMPTS
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
        )
        self.cause_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, cause_prompt
        )
        self.action_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_symptom, action_prompt
        )

        self.manual_agent = create_openai_functions_agent_with_history(
            llm_model, self.tool_manual, manual_prompt
        )

    def identify_user(self, ch, method, properties, msg):
        """identify user and get messages"""
        msg = json.loads(msg)
        user_id = msg["user_id"]
        message = msg["message"]

        if user_id not in self.user_chat_history:
            self.user_chat_history[user_id] = []
            print("USER: ", user_id, " AGENT IS INITIALIZED")

        else:
            print("USER: ", user_id, " AGENT IS LOADED")
        self.callback_agent(user_id, message)

    def callback_agent(self, user_id, message):
        """callback user id and messages from LLM"""

        chat_history = self.user_chat_history[user_id]

        general_agent_executor = AgentExecutor(
            agent=self.general_agent, tools=self.tool_symptom, verbose=True
        )
        response = general_agent_executor.invoke(
            {"input": message, "chat_history": chat_history}
        )
        chat_history.extend(
            [
                HumanMessage(content=message, id=user_id),
                AIMessage(content=response["output"], id=user_id),
            ]
        )

        general_res = response["output"]

        # 증상 파악 및 분류시 바로 원인 분석 시작하도록
        if "Symptom" in general_res:
            ask_symptom = "KT_Robot_Customer_Issue_Guide를 검색하여, 고객의 발화에 적합한 증상을 하나 골라서 한 문장으로 대답해주세요.(ex. 고객님의 증상은 ~~으로 분류됩니다.)"
            symptom_agent_executor = AgentExecutor(
                agent=self.symptom_agent, tools=self.tool_symptom, verbose=True
            )
            response1 = symptom_agent_executor.invoke(
                {"input": ask_symptom, "chat_history": chat_history}
            )
            chat_history.extend(
                [
                    AIMessage(content=ask_symptom, id=user_id),
                    AIMessage(content=response1["output"], id=user_id),
                ]
            )

            # pandas agent 원인 분석 및 리스트 업
            symptom = response1["output"]

            response_causes = self.pandas_agent.invoke(
                "고객의 입력으로부터 도출된 증상:" + symptom
            )
            # self.send_message(response_causes["output"])

            chat_history.extend(
                [AIMessage(content=response_causes["output"], id=user_id)]
            )

            ask_cause = "나열된 순서대로 원인이 발생한적 있는지 스무고개 형태로 파악해주세요. 질문을 먼저 시작해주세요."
            cause_agent_executor = AgentExecutor(
                agent=self.cause_agent, tools=self.tool_symptom, verbose=True
            )
            response = cause_agent_executor.invoke(
                {"input": ask_cause, "chat_history": chat_history}
            )
            chat_history.extend(
                [
                    AIMessage(content=ask_cause, id=user_id),
                    AIMessage(content=response["output"], id=user_id),
                ]
            )

            final_response = response1["output"] + "\n\n" + response["output"]
            self.send_message(user_id=user_id, message=final_response)

        elif "Manual" in general_res:
            ask_manual = "{chat_history}에서 가장 최근 질문에 대하여 로봇 매뉴얼을 검색하여 답해주세요."
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

        else:
            self.send_message(user_id=user_id, message=general_res)

        # print(chat_history)
        self.logging_history(user_id=user_id, history=chat_history)
        # 대화 종료시 chat history초기화
        if message == "!종료":
            self.reset_history(user_id=user_id)

    def send_message(self, user_id, message):
        """Publish and send messages to RMQ"""
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
        channel = connection.channel()

        channel.queue_declare(
            queue=user_id
        )  # user id별로 RMQ에 return 하는 메시지의 채널을 생성
        channel.basic_publish(exchange="", routing_key=user_id, body=message)
        print(f"Sent message.\n{message}")

        connection.close()

    def logging_history(self, user_id, history):
        """Logging history for users"""

        f = open("./history/history_" + user_id + ".csv", "w", encoding="utf-8")
        writer = csv.writer(f)
        for row in history:
            writer.writerow(row)
        f.close()

    def reset_history(self, user_id):
        self.user_chat_history[user_id] = []
        print("RESET THE CHATHISTORY")
