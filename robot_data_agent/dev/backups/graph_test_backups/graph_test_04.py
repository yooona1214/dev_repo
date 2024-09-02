import numpy as np
import pandas as pd
from neo4j_runway import Discovery, GraphDataModeler, IngestionGenerator, LLM, PyIngest
from IPython.display import display, Markdown, Image
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"
os.environ["GPT_MODEL"] = "gpt-3.5-turbo"

# Neo4j 연결 정보 설정
NEO4J_URL = os.environ["NEO4J_URI"] = "neo4j+s://3d199dc6.databases.neo4j.io"
NEO4J_ID = os.environ["NEO4J_USERNAME"] = "neo4j"
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"] = (
    "YsYsi1CMNW6g9S1mirbmypR6_smqo0qZ8NNi_deXGmg"
)
csv_file1 = "/home/rbrain/data_agent/data/LG0429_.csv"

test_df = pd.read_csv(csv_file1)
# print(test_df)


test_df.columns = test_df.columns.str.strip()
for i in test_df.columns:
    test_df[i] = test_df[i].astype(str)
test_df.to_csv("/home/rbrain/data_agent/data/LG0429_prepared.csv", index=False)

DATA_DESCRIPTION = {
    "충돌을 나타내는 고객의 발화": "고객이 충돌 증상에 대해 표현한 발화",
    "충돌의 원인": "고객의 충돌 증상에 대한 원인을 표현한 말",
    "조치 방안": "고객의 충돌 증상에 대한 원인을 해결하기 위한 조치 방안",
    "자가조치 가능여부": "고객이 충돌 증상에 대한 원인을 스스로 조치 가능한지에 대한 여부(True/False)",
    "자가조치 시 매뉴얼 참조여부": "고객이 스스로 조치 시, 매뉴얼을 참조해야 하는지에 대한 여부(True/False)",
    "자가조치 참조방법": "고객이 스스로 조치 할 때, 어떤 방법을 사용해야하는지에 대한 설명",
    "출동 필요여부": "고객이 스스로 조치가 불가능하여, AS직원 출동 필요 여부(True/False)",
    "출동 담당업체": "AS출동 담당 업체에 대한 설명",
}
llm = LLM()

disc = Discovery(llm=llm, user_input=DATA_DESCRIPTION, data=test_df)
disc.run()

# instantiate graph data modeler
gdm = GraphDataModeler(llm=llm, discovery=disc)

# generate model
gdm.create_initial_model()

# visualize the data model
gdm.current_model.visualize()
