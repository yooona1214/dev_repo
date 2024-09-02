'''
import getpass
import os

os.environ["OPENAI_API_KEY"] = (
    "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"  # set with yours
)

# Uncomment the below to use LangSmith. Not required.
# os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()
# os.environ["LANGCHAIN_TRACING_V2"] = "true"

from langchain_community.graphs import Neo4jGraph

os.environ["NEO4J_URI"] = "neo4j+s://0d811677.databases.neo4j.io"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "dJX89oapsNHdhFZRDM1K8wvrVk-joveEL802qKr0YCM"

graph = Neo4jGraph()

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

llm_transformer = LLMGraphTransformer(llm=llm)

from langchain_core.documents import Document

text = """

"""
documents = [Document(page_content=text)]
graph_documents = llm_transformer.convert_to_graph_documents(documents)
print(f"Nodes:{graph_documents[0].nodes}")
print(f"Relationships:{graph_documents[0].relationships}")


'''
import json
import os
import pandas as pd
from pypdf import PdfReader
from neo4j import GraphDatabase
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers import (
    ReActSingleInputOutputParser,
    OpenAIFunctionsAgentOutputParser,
)
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_community.utilities.sql_database import SQLDatabase
#from langchain_community.utilities.llm_transformer import LLMTransformer
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.messages import AIMessage, HumanMessage
import os 
#from custom_tools.preprocesscsv import PreProcessCSV
#from custom_tools.issue_rag import create_vector_store_as_retriever
#from custom_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, PyPDFDirectoryLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent, Tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain.tools.retriever import create_retriever_tool

# 환경 변수 설정
os.environ["OPENAI_API_KEY"] = "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"
os.environ["GPT_MODEL"] = "gpt-4o"

OPENAI_API_KEY = 'sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe'
llm_4_o = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0)

llm_model = llm_4_o

from langchain_community.utilities import SQLDatabase

# set with yours
username = "postgres"
password = "rbrain!"
host = "localhost"
port = "5432"
database = "agentdb"

pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

db = SQLDatabase.from_uri(pg_uri)


# PDF 파일에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# CSV 파일에서 데이터 읽기
def read_csv_data(csv_path):
    df = pd.read_csv(csv_path)
    return df.to_dict(orient='records')

# Neo4j 연결
def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

def close_neo4j(driver):
    driver.close()

# Neo4j에 노드와 관계 생성
def create_nodes_and_relationships(driver, knowledge_graph):
    with driver.session() as session:
        for entity in knowledge_graph['entities']:
            session.write_transaction(create_entity, entity)
        for relationship in knowledge_graph['relationships']:
            session.write_transaction(create_relationship, relationship)

def create_entity(tx, entity):
    query = (
        "MERGE (e:Entity {name: $name}) "
        "SET e += $properties"
    )
    tx.run(query, name=entity['name'], properties=entity['properties'])

def create_relationship(tx, relationship):
    query = (
        "MATCH (a:Entity {name: $start_node}), (b:Entity {name: $end_node}) "
        "MERGE (a)-[r:RELATION {type: $type}]->(b) "
        "SET r += $properties"
    )
    tx.run(query, start_node=relationship['start_node'], end_node=relationship['end_node'], type=relationship['type'], properties=relationship['properties'])

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

def create_knowledge_graph_agent():
    # Agent의 프롬프트 설정
    template_str = (
        "Create a knowledge graph based on the following data:\n"
        "PostgreSQL Data:\n{postgres_data}\n\n"
        "PDF Text:\n{pdf_text}\n\n"
        "CSV Data:\n{csv_data}\n\n"
        "Output in JSON format."
    )
    
    prompt_template = PromptTemplate(
        template=template_str,
        input_variables=["postgres_data", "pdf_text", "csv_data", "agent_scratchpad"]
    )

    agent_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # PostgreSQL 연결 정보 설정
    tools = {
        "sql_database": db
    }

    # Agent 생성
    agent = create_openai_functions_agent(llm_model, tools=tools, prompt=agent_prompt)
    return agent

# 질의응답 Agent with History 생성 함수
def create_qa_agent_with_history():
    # 널리지 그래프를 참조하는 LLMTransformer 초기화
    #llm_transformer = LLMTransformer(api_key=os.environ["OPENAI_API_KEY"])
    
    # Agent의 프롬프트 설정
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant"),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])
    
    # Agent 생성: 널리지 그래프를 참조하여 질의응답 처리
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
            chat_history=lambda x: x["chat_history"]
        )
        | agent_prompt
        | llm_model  # 널리지 그래프를 참조하는 LLMTransformer 사용
        | OpenAIFunctionsAgentOutputParser()
    )
    
    return agent


# 메인 함수
def main():
    # PDF 파일 경로 설정
    pdf_path = "/home/rbrain/data_agent/data/LG2세대[FnB3.0]_사용자매뉴얼.pdf"
    
    # CSV 파일 경로 설정 (각각의 파일)
    csv_path_1 = "/home/rbrain/data_agent/data/LG0429.csv"
    csv_path_2 = "/home/rbrain/data_agent/data/LG_Error_0403.csv"
    csv_path_3 = "/home/rbrain/data_agent/data/LG_Error_0403.csv"
    
    # Neo4j 연결 설정
    neo4j_uri = "neo4j+s://0d811677.databases.neo4j.io"
    neo4j_user = "neo4j"
    neo4j_password = "dJX89oapsNHdhFZRDM1K8wvrVk-joveEL802qKr0YCM"
    
    # PDF 파일에서 텍스트 추출
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # CSV 파일에서 데이터 읽기 (각각의 파일)
    csv_data_1 = read_csv_data(csv_path_1)
    csv_data_2 = read_csv_data(csv_path_2)
    csv_data_3 = read_csv_data(csv_path_3)
    
    # 에이전트 생성 - 지식 그래프 생성 Agent
    knowledge_graph_agent = create_knowledge_graph_agent()
    
    # 에이전트 생성 - 질의응답 Agent with History
    qa_agent = create_qa_agent_with_history()
    
    # 지식 그래프 생성 및 처리
    knowledge_graph = knowledge_graph_agent.execute(postgres_data=None, pdf_text=pdf_text, csv_data=[csv_data_1, csv_data_2, csv_data_3])
    
    # Neo4j 연결
    neo4j_driver = connect_to_neo4j(neo4j_uri, neo4j_user, neo4j_password)
    
    # Neo4j에 지식 그래프 저장
    create_nodes_and_relationships(neo4j_driver, knowledge_graph)
    
    # 연결 종료
    close_neo4j(neo4j_driver)
    
    # 질의응답 테스트 (터미널에서 직접 입력하여 확인)
    
    while True:
        question = input("Enter your question (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        
        # 사용자가 입력한 질문을 HumanMessage로 생성
        human_message = HumanMessage(content=question)
        
        # 이전 대화 기록과 함께 질의응답 Agent 실행
        response = qa_agent.execute(chat_history=[human_message])
        
        # Agent의 응답을 출력
        print("Answer:", response)
        
if __name__ == "__main__":
    main()
