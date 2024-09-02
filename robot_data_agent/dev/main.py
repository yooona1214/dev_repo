import numpy as np
import pandas as pd
import os
import redis
import atexit
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool, AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.google_serper.tool import GoogleSerperRun

from custom_tools.create_react_agent_w_history import (
    create_openai_functions_agent_with_history,
    create_react_agent_w_history,
)

from modules.agents import *
from modules.router import *
from modules.db_manager import *

from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit

# from tools.graph_cypher_tool import graph_cypher_tool
# from tools.vector_graph_tool import vector_graph_tool
# from tools.vector_tool import vector_tool

from custom_prompts.prompts import (
    GENERAL_PROMPTS,
    GENERAL_INPUTS,
    REACT_INPUTS,
    REACT_PROMPT,
)

# 환경변수설정
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Robot Data Agent"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # sh
os.environ["GPT_MODEL"] = "gpt-3.5-turbo"

# LLM model

# llm_4 = ChatOpenAI(model="gpt-4-0613")
# llm_4_t = ChatOpenAI(model="gpt-4-0125-preview")
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125")
llm_4_o_mini = ChatOpenAI(model="gpt-4o-mini")
llm_4_o = ChatOpenAI(model="gpt-4o")

llm_model = llm_4_o


# Redis 클라이언트 생성
r = redis.Redis(host="localhost", port=6379, db=1)

# DB manager 생성
dbmanger = DBManager(r)

# Router 생성
router = Router(encoder=OpenAIEncoder())

# multi agents 선언
agents = multi_agents

# 종료 시 Redis 캐시를 비우도록 atexit에 등록
atexit.register(dbmanger.clear_redis_cache)


def load_all():
    from langchain_community.document_loaders.csv_loader import CSVLoader
    from langchain_community.document_loaders.pdf import PyPDFLoader
    from langchain.agents import AgentExecutor, AgentType
    from langchain_openai import ChatOpenAI
    from custom_tools.issue_rag import (
        CreateVectorstore,
    )

    """Load all files that you need"""
    # Data 로드
    print("필요한 파일을 불러오는중...")

    # VOC데이터
    loader1 = CSVLoader("./data/LG0429.csv")
    loader2 = CSVLoader("./data/LG_Error_0403.csv")
    df_for_pandas = pd.read_csv("./data/LG0429.csv")

    # loader2 = CSVLoader('./data/베어_0226.csv')
    loader3 = PyPDFLoader("./data/LG2세대[FnB3.0]_사용자매뉴얼.pdf")
    data1 = loader1.load()
    data2 = loader2.load()
    data3 = loader3.load()

    issue_data = data1
    error_data = data2
    manual_data = data3

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

    rag_manual = CreateVectorstore.create_vector_store_as_retriever_lg_manual(
        data=manual_data, str1="LG_Robot_Manual_Guide", str2="This is robot manual."
    )

    return rag_issue, rag_error, rag_manual

    # Agent 선언


# from langchain import hub  # requires langchainhub package
# prompt = hub.pull("hwchase17/react")


def load_sql():
    from langchain_community.utilities.sql_database import SQLDatabase

    # Connect to the PostgreSQL DB
    username = "postgres"
    password = "rbrain!"
    host = "localhost"
    port = "5432"
    database = "agentdb"
    pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

    db = SQLDatabase.from_uri(pg_uri)

    return db


def load_prompt_for_sql():
    prefix_template = """

    [INST]You are an agent capable of using a variety of TOOLS to answer a data analytics question.
    Always use MEMORY to help select the TOOLS to be used. You are an Postgresql expert agent designed to interact with a SQL database.
    
    MEMORY
    chat_history
    

    If the question is not related to db or chat_history, then reply gently to ask again in korean
    """

    # TOOLS
    # - Generate Final Answer: Use if answer to User's question can be given with MEMORY
    # - Calculator: Use this tool to solve mathematical problems.
    # - Plot generator : Use this tool to plot the graph
    # - Query_Database: Write an SQL Query to query the Database.

    format_instructions_template = """
    Use the following format:

    Only use the following tables:
    {table_info}
    Question: {input}

    You must answer in korean
    Previous conversation history:
    {chat_history}


    """

    return prefix_template, format_instructions_template


def graphql_agent(user_input, chat_history):
    graph = Neo4jGraph(
        url="bolt://98.82.11.37:7687",
        username="neo4j",
        password="stump-refund-signatures",
    )  # connection info
    chain = GraphCypherQAChain.from_llm(
        ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY),
        graph=graph,
        verbose=True,
    )
    chain1 = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)

    result = chain.run(user_input)
    result1 = chain1.invoke(
        input="Cypher query결과를 바탕으로 고객에게 적절한 분석결과를 명료하게(3문장 이내) 제공하세요. 고객의 발화:"
        + user_input
        + "\n\n cypher query 결과:"
        + result
        + "chat_history:{chat_history}"
    )

    return result1


if __name__ == "__main__":
    # 문서 데이터 검색 툴 load
    rag_issue, rag_error, rag_manual = load_all()
    # 문서 데이터 검색위한 툴 선언
    tool_doc_data = [rag_issue, rag_error, rag_manual]
    tools_data = load_tools([], llm=llm_model)

    # doc 검색 위한 react 프롬프트 선언
    react_prompt = PromptTemplate(input_variables=REACT_INPUTS, template=REACT_PROMPT)
    # doc 데이터 검색 에이전트 선언
    doc_data_agent = create_react_agent_w_history(
        llm_model, tool_doc_data, react_prompt
    )

    # SQL DB load
    db = load_sql()

    # Prompts for SQL Agent
    prefix_template, format_instructions_template = load_prompt_for_sql()

    # tool
    toolkit = SQLDatabaseToolkit(db=db, llm=llm_model)
    # Agent 선언
    sql_agent = create_sql_agent(
        llm=llm_model,
        toolkit=toolkit,
        prefix=prefix_template,
        format_instructions=format_instructions_template,
        agent_type="openai-tools",
        verbose=True,
    )

    START = False
    chat_history = []
    while True:

        user_input = input("입력: ")
        if not START:
            # 현재 날짜와 시간을 세션 ID로 설정
            session_id = dbmanger.get_session_id()
            START = True

        route_name = router.route(user_input)
        print(route_name)
        print(type(route_name))

        if route_name is not None:

            if "general_chat" in route_name:

                from langchain_core.prompts import PromptTemplate

                general_prompt = PromptTemplate(
                    input_variables=GENERAL_INPUTS, template=GENERAL_PROMPTS
                )

                chain = general_prompt | llm_model
                general_response = chain.invoke(
                    {
                        "input": user_input,
                        "chat_history": chat_history,
                    }
                )

                print("AI: ", general_response.content)
                chat_history.extend(
                    [
                        HumanMessage(content=user_input, id=session_id),
                        AIMessage(content=general_response.content, id=session_id),
                    ]
                )
            elif "robot_data" in route_name:
                doc_data_agent_executor = AgentExecutor(
                    agent=doc_data_agent,
                    tools=tool_doc_data,
                    verbose=True,
                )
                doc_data_response = doc_data_agent_executor.invoke(
                    {
                        "input": user_input,
                        "chat_history": chat_history,
                    }
                )

                sql_agent_res = sql_agent.invoke(
                    {"input": user_input, "chat_history": chat_history}
                )

                gql_agent_res = graphql_agent(user_input, chat_history)

                chat_history.extend(
                    [
                        HumanMessage(content=user_input, id=session_id),
                        AIMessage(content=doc_data_response["output"], id=session_id),
                        AIMessage(content=sql_agent_res["output"], id=session_id),
                        AIMessage(content=gql_agent_res.content, id=session_id),
                    ]
                )

                print(
                    "AI: \n\n문서 데이터 검색 결과: \n\n",
                    doc_data_response["output"],
                    "\n\nSQL결과: ",
                    sql_agent_res["output"],
                    "\n\nGQL결과: ",
                    gql_agent_res.content,
                )

                print("\n\n\nchat_history: ", chat_history)
        else:
            pass

        # current_agent = agents[route_name]
        # print(current_agent)

        dbmanger.add_turn(session_id, user_input, route_name, route_name)
