"""llm_processor"""

import os
from custom_tools.preprocesscsv import PreProcessCSV
from custom_tools.issue_rag import create_vector_store_as_retriever
from custom_tools.create_react_agent_w_history import (
    create_react_agent_w_history,
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
)
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_openai_functions_agent,
    create_react_agent,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain.agents import AgentExecutor
from langchain_experimental.agents import create_pandas_dataframe_agent


import pika

OPENAI_API_KEY = "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"

# RabbitMQ 연동 위한 채널 큐 설정
HOST_NAME = "localhost"
QUEUE_NAME = "Chat"
QUEUE_NAME2 = "Chat2"

# unique_id = uuid4().hex[0:8]
# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = (
    "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key
)


# Data 로드
print("필요한 파일을 불러오는중...")


# Manual 데이터
# loader_manual = UnstructuredWordDocumentLoader('./data/LG1세대[FnB2.0]_사용자매뉴얼.docx') #mode='elements',strategy='fast')
# data_manual = loader_manual.load()

# VOC데이터
loader1 = CSVLoader("./data/LG0403.csv")
df_for_pandas = pd.read_csv("./data/LG0403.csv")

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
    str2="This is a data containing symptoms, causes of symptoms, and action plans for the causes.",
)

rag_manual = create_vector_store_as_retriever(
    data=manual_data, str1="LG_Robot_Manual_Guide", str2="This is robot manual."
)


# LLM 모델 선택
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

llm_model = llm_4_t

tool_symptom = [rag_issue]  #
tool_manual = [rag_manual]
final_symptom = ""

# prompt1 = hub.pull("hwchase17/react-chat")

general_prompt = PromptTemplate(
    input_variables=GENERAL_INPUTS, template=GENERAL_PROMPTS
)


symptom_prompt = PromptTemplate(
    input_variables=SYMPTOM_INPUTS, template=SYMPTOM_PROMPTS
)


cause_prompt = PromptTemplate(input_variables=CAUSE_INPUTS, template=CAUSE_PROMPTS)

# - Cause expert: Based on the symptoms derived by the symptom identification expert, using only causes in the ‘Cause’ column of the csv file, but use them as is and ask the customer one by one in a 20-question game format, starting with the most overlapping cause that causes the symptom among the causes in the 'Cause' column.

manual_prompt = PromptTemplate(input_variables=MANUAL_INPUTS, template=MANUAL_PROMPTS)


# print('P1',prompt1)


chat_history = []


general_agent = create_openai_functions_agent_with_history(
    llm_model, tool_symptom, general_prompt
)

symptom_agent = create_openai_functions_agent_with_history(
    llm_model, tool_symptom, symptom_prompt
)

from langchain.agents.types import AgentType

pandas_agent = create_pandas_dataframe_agent(
    llm=llm_model,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    df=df_for_pandas,
    verbose=True,
    prefix="Please list the causes appropriate for your symptoms in order of frequency. Please answer all questions concisely and in Korean.",
)
cause_agent = create_openai_functions_agent_with_history(
    llm_model, tool_symptom, cause_prompt
)
action_agent = create_openai_functions_agent_with_history(
    llm_model, tool_symptom, general_prompt
)

manual_agent = create_openai_functions_agent_with_history(
    llm_model, tool_manual, manual_prompt
)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)

    def callback1(ch, method, properties, body):
        message = body.decode("utf-8")  # 바이트를 문자열로 디코딩
        print("Received message:", message)

        if message != "keepgoing":
            general_agent_executor = AgentExecutor(
                agent=general_agent, tools=tool_symptom, verbose=True
            )

            response = general_agent_executor.invoke(
                {"input": message, "chat_history": chat_history}
            )
            chat_history.extend(
                [
                    HumanMessage(content=message),
                    AIMessage(content=response["output"]),
                ]
            )

            general_res = response["output"]
            # print('[Log: ',general_res,']')

            # send_message(general_res)

            # 증상 파악 및 분류시 바로 원인 분석 시작하도록
            if "Symptom" in general_res:
                ask_symptom = "{chat_history}를 분석하여, 고객의 증상을 최종 분류해서 단답형으로 대답해주세요."
                symptom_agent_executor = AgentExecutor(
                    agent=symptom_agent, tools=tool_symptom, verbose=True
                )
                response = symptom_agent_executor.invoke(
                    {"input": ask_symptom, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=ask_symptom),
                        AIMessage(content=response["output"]),
                    ]
                )
                # send_message(response["output"])
                # send_message("고객님의 증상을 기반으로 원인을 파악하는 중입니다.")

                # pandas agent 원인 분석 및 리스트 업
                symptom = response["output"]

                response_causes = pandas_agent.invoke(
                    "고객의 입력으로부터 도출된 증상:" + symptom
                )
                send_message(response_causes["output"])

                chat_history.extend([AIMessage(content=response_causes["output"])])

                ask_cause = "나열된 순서대로 고객의 원인을 스무고개 형태로 파악해주세요. 질문을 먼저 시작해주세요."
                cause_agent_executor = AgentExecutor(
                    agent=cause_agent, tools=tool_symptom, verbose=True
                )
                response = cause_agent_executor.invoke(
                    {"input": ask_cause, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=ask_cause),
                        AIMessage(content=response["output"]),
                    ]
                )

                send_message(response["output"])

            elif "Manual" in general_res:
                ask_manual = "{chat_history}에서 고객의 가장 최근 질문에 로봇 설명서를 참조하여 답해주세요."
                manual_agent_executor = AgentExecutor(
                    agent=manual_agent, tools=tool_manual, verbose=True
                )
                response = manual_agent_executor.invoke(
                    {"input": ask_manual, "chat_history": chat_history}
                )
                chat_history.extend(
                    [
                        AIMessage(content=ask_manual),
                        AIMessage(content=response["output"]),
                    ]
                )

                send_message(response["output"])

            else:
                send_message(general_res)

        else:
            pass

        # send_message('test')

    channel.basic_consume(
        queue=QUEUE_NAME, on_message_callback=callback1, auto_ack=True
    )

    try:
        print("Waiting for messages.")
        channel.start_consuming()

    except KeyboardInterrupt:
        print("Ctrl+C is Pressed.")


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME2)
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME2, body=message)
    print(f"Sent message.\n{message}")

    connection.close()


if __name__ == "__main__":
    main()
