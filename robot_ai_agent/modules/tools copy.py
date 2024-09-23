from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import pandas as pd
import numpy as np
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#from langchain.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.tools import BaseTool
#from langchain.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from typing import Type

from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from pydantic import PrivateAttr 
'''
class GraphTool(BaseTool):
    name = "graph_tool"
    description = "Neo4j 그래프에서 구조적, 로봇과 공간 내 상호연결된 지식을 검색하는 도구입니다."
    
    def __init__(self):

        self.graph = Neo4jGraph(
            url="bolt://54.235.226.49:7687",  # Neo4j bolt 주소 (예시)
            username="neo4j",  # 사용자 이름
            password="spool-race-odds"  # 비밀번호
        )  # Neo4j 연결 설정 (인증 정보 추가 필요 시 수정)
        
        # Cypher 쿼리 검증기 설정
        self.corrector_schema = [
            Schema(el["start"], el["type"], el["end"])
            for el in self.graph.structured_schema.get("relationships")
        ]
        self.cypher_validation = CypherQueryCorrector(self.corrector_schema)

        # LLM 설정
        self.cypher_llm = ChatOpenAI(model_name="gpt-4o-2024-08-06", temperature=0.0)
        self.qa_llm = ChatOpenAI(model_name="gpt-4o-2024-08-06", temperature=0.0)

    def _run(self, user_input, session_id=None):
        # 사용자 입력에 기반한 Cypher 쿼리 생성
        cypher_template = """
        Neo4j 그래프 스키마에 따라, 아래 질문에 답변할 수 있는 Cypher 쿼리를 작성해 주세요:
        {schema}

        질문: {user_input}
        Cypher 쿼리:"""

        cypher_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "입력된 질문을 Cypher 쿼리로 변환해 주세요."),
                ("human", cypher_template.format(schema=self.graph.get_schema(), user_input=user_input)),
            ]
        )

        # Cypher 쿼리 생성
        cypher_response = (
            RunnablePassthrough.assign(schema=lambda _: self.graph.get_schema())
            | cypher_prompt
            | self.cypher_llm.bind(stop=["\nCypherResult:"])
            | StrOutputParser()
        )

        # 쿼리 실행 및 결과 반환
        cypher_query = cypher_response.invoke({"user_input": user_input})
        query_result = self.graph.query(self.cypher_validation(cypher_query))

        # 결과를 자연어로 변환
        response_template = f"""
        질문: {user_input}
        Cypher 쿼리: {cypher_query}
        Cypher 결과: {query_result}
        
        위 정보를 기반으로 자연어 답변을 작성해 주세요."""

        response_prompt = ChatPromptTemplate.from_messages(
            [("system", "Cypher 쿼리 결과를 자연어로 변환해 주세요."),
             ("human", response_template)]
        )

        # 자연어 응답 생성
        natural_response = (
            RunnablePassthrough.assign(output=response_prompt)
            | self.qa_llm
            | StrOutputParser()
        )

        # 최종 응답 반환
        return natural_response.invoke({"user_input": user_input, "session_id": session_id})
'''
from py2neo import Graph

class GraphTool(BaseTool):
    name = "graph_tool"
    description = "Neo4j 그래프에서 로봇 및 공간 정보를 검색하는 도구입니다."
    def _run(self, user_input, session_id=None):
        # Neo4j 연결
        graph = None  # _graph 대신 지역 변수 사용
        try:
            graph = Neo4jGraph(
                url="bolt://54.235.226.49:7687",  
                username="neo4j",  
                password="spool-race-odds"
            )
            print("-----------------------Neo4j 연결 완료")
        except Exception as e:
            print(f"Neo4j 연결 중 에러 발생: {e}")
            return f"Neo4j 연결에 문제가 발생했습니다: {e}"

        # LLM 초기화
        # LLM 초기화
        cypher_llm = ChatOpenAI(model_name="gpt-4o-2024-08-06", temperature=0.0)

        try:
            # 사용자 입력에 기반한 Cypher 쿼리 생성
            cypher_template = """
            Neo4j 그래프 스키마에 따라, 아래 질문에 답변할 수 있는 Cypher 쿼리를 작성해 주세요:
            {schema}

            질문: {user_input}
            Cypher 쿼리:"""

            # 스키마 정보를 가져와서 Cypher 쿼리 생성
            schema_str = str(graph.get_schema())
            cypher_prompt = cypher_template.format(schema=schema_str, user_input=user_input)
            
            print(f"생성된 Cypher 쿼리 프롬프트: {cypher_prompt}")
            
            # ChatOpenAI에 메시지를 전달할 형식으로 변경
            messages = [
                {"role": "system", "content": "입력된 질문을 Cypher 쿼리로 변환해 주세요."},
                {"role": "user", "content": cypher_prompt}
            ]

            # LLM을 사용하여 Cypher 쿼리 생성
            cypher_response = cypher_llm(messages)  # 'invoke' 사용 없이 직접 전달
            print(f"생성된 Cypher 쿼리: {cypher_response}")

            # 쿼리 실행
            if hasattr(graph, "query") and callable(graph.query):
                query_result = graph.query(cypher_response)
                print(f"쿼리 결과: {query_result}")
            else:
                print("graph 객체에 query 메서드가 없습니다.")
                return "쿼리 메서드가 없습니다."

            return query_result

        except Exception as e:
            print(f"쿼리 실행 중 에러 발생: {e}")
            return f"쿼리 실행 중 문제가 발생했습니다: {e}"
    
    '''
    def _run(self, user_input, session_id=None):
        # Neo4j 연결 설정 (런타임에 초기화)
        if not hasattr(self, '_graph') or self._graph is None:
            self._graph = Neo4jGraph(
                url="bolt://54.235.226.49:7687",  # Neo4j bolt 주소 (예시)
                username="neo4j",  # 사용자 이름
                password="spool-race-odds"  # 비밀번호
            )
            print("-----------------------Neo4j 연결 완료")  # Neo4j 연결 확인
        
        # 스키마 정보 가져오기 시도
        try:
            # 쿼리 실행 부분 수정, Cypher 쿼리 사용
            schema_info = self._graph.run("CALL db.schema.visualization()").data()  # 'run' 메서드로 변경
            print(f"---------------------스키마 정보: {schema_info}")  # 스키마 확인
        except Exception as e:
            print(f"스키마 정보 가져오는 중 에러 발생: {e}")
            return f"스키마 정보 가져오는 중 에러 발생: {e}"
        
        # Cypher 쿼리 검증기 설정
        corrector_schema = [
            Schema(el['start'], el['type'], el['end'])
            for el in schema_info.get('relationships', [])
        ]
        print(f"---------------------Cypher 쿼리 스키마: {corrector_schema}")  # 스키마 확인
        cypher_validation = CypherQueryCorrector(corrector_schema)

        # LLM 설정
        cypher_llm = ChatOpenAI(model_name="gpt-4o-2024-08-06", temperature=0.0)
        qa_llm = ChatOpenAI(model_name="gpt-4o-2024-08-06", temperature=0.0)

        # Cypher 쿼리 생성 및 실행 로직
        cypher_template = """
        Neo4j 그래프 스키마에 따라, 아래 질문에 답변할 수 있는 Cypher 쿼리를 작성해 주세요:
        {schema}

        질문: {user_input}
        Cypher 쿼리:"""

        # graph.get_schema()를 문자열로 변환
        schema_str = str(schema_info)
        print(f"---------------------Cypher 쿼리 스키마: {schema_str}")
        cypher_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "입력된 질문을 Cypher 쿼리로 변환해 주세요."),
                ("human", cypher_template.format(schema=schema_str, user_input=user_input)),
            ]
        )

        # Cypher 쿼리 생성
        cypher_response = (
            RunnablePassthrough.assign(schema=lambda _: schema_info)
            | cypher_prompt
            | cypher_llm.bind(stop=["\nCypherResult:"])
            | StrOutputParser()
        )

        # Cypher 쿼리 실행 및 결과 반환
        cypher_query = cypher_response.invoke({"user_input": user_input})
        print(f"------------------------생성된 Cypher 쿼리: {cypher_query}")
        query_result = self._graph.run(cypher_query).data()  # 'run' 메서드로 변경
        print(f"------------------------Cypher 쿼리 실행 결과: {query_result}")

        # 결과를 자연어로 변환
        response_template = f"""
        질문: {user_input}
        Cypher 쿼리: {cypher_query}
        Cypher 결과: {query_result}
        
        위 정보를 기반으로 자연어 답변을 작성해 주세요."""

        response_prompt = ChatPromptTemplate.from_messages(
            [("system", "Cypher 쿼리 결과를 자연어로 변환해 주세요."),
             ("human", response_template)]
        )

        # 자연어 응답 생성
        natural_response = (
            RunnablePassthrough.assign(output=response_prompt)
            | qa_llm
            | StrOutputParser()
        )

        response = natural_response.invoke({"user_input": user_input, "session_id": session_id})
        print(f"-------------------------------최종 자연어 응답: {response}")  # 최종 응답 출력

        return response
        '''

def create_graph_tool():
    # GraphTool 인스턴스 생성
    graph_tool = GraphTool()
    
    # 이 도구는 이미 BaseTool을 상속하므로 바로 반환
    return graph_tool

def create_vector_store_as_retriever(data, str1, str2):
 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(data)

    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(
        documents=docs, embedding=embedding
    )

    retriever = vectorstore.as_retriever()
    
    retriever.search_kwargs = {'k': 63}

    tool = create_retriever_tool(
        retriever,
        str1,
        str2,
    )

    return tool

def create_vector_store_as_retriever2(csv_path, str1, str2):
    # 1. CSV 파일에서 데이터 로드
    df = pd.read_csv(csv_path)
    data = df.to_dict(orient='records')
    
    # 2. OpenAI 임베딩 생성기 로드
    embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # 3. 설명을 임베딩으로 변환
    descriptions = list(set([item['Description'] for item in data]))
    duplicates = [description for description in descriptions if descriptions.count(description) > 1]
    print("###########################################중복된 값들:", duplicates)

    # 4. Chroma 벡터 스토어 생성
    vectorstore = Chroma.from_texts(
        texts=descriptions,
        embedding=embedding_model,
        metadatas=data,
    )
    
    # 5. 벡터 스토어를 리트리버로 변환
    retriever = vectorstore.as_retriever(search_type='similarity')
    retriever.search_kwargs = {'k': 30}  # 검색할 상위 k개 결과 설정

    # 6. LangChain의 retriever_tool 생성
    tool = create_retriever_tool(
        retriever,
        str1,  # 툴의 이름
        str2   # 툴의 설명
    )

    return tool