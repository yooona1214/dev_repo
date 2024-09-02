import os
import pandas as pd
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = (
    "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"
)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"
os.environ["GPT_MODEL"] = "gpt-3.5-turbo"

# Neo4j 연결 정보 설정
os.environ["NEO4J_URI"] = "neo4j+s://3d199dc6.databases.neo4j.io"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "YsYsi1CMNW6g9S1mirbmypR6_smqo0qZ8NNi_deXGmg"

# CSV 파일 경로
csv_file1 = "/home/rbrain/data_agent/data/LG0429.csv"
csv_file2 = "/home/rbrain/data_agent/data/플랫폼 데이터 규격 - 주기.csv"

# PDF 파일 경로
pdf_file = "/home/rbrain/data_agent/data/LG_Error_0403 - LG_Error_0403.csv.pdf"

# CSV 파일 로드
df1 = pd.read_csv(csv_file1)
df2 = pd.read_csv(csv_file2)


# PDF 파일 텍스트 추출
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text


pdf_text = extract_text_from_pdf(pdf_file)

# LLM 초기화
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# LLM을 이용한 그래프 변환기 초기화
llm_transformer = LLMGraphTransformer(llm=llm)

# CSV 데이터를 Document 객체로 변환
documents = [
    Document(page_content=row.to_string())  # 예시로 각 행을 Document로 변환
    for _, row in pd.concat([df1, df2]).iterrows()
]

# PDF 데이터를 Document 객체로 변환
pdf_document = Document(page_content=pdf_text)

# 모든 문서를 하나의 리스트로 결합
all_documents = documents + [pdf_document]

# 문서를 그래프 문서로 변환
graph_documents = llm_transformer.convert_to_graph_documents(all_documents)

# Neo4j 그래프 인스턴스 생성
graph = Neo4jGraph()

# 그래프에 문서 추가
graph.add_graph_documents(graph_documents)

print("Graph documents added to Neo4j.")
