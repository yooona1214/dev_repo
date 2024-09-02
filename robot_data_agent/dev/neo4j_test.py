import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

# graph = Neo4jGraph(url="neo4j+s://0d811677.databases.neo4j.io", username="neo4j", password="dJX89oapsNHdhFZRDM1K8wvrVk-joveEL802qKr0YCM") # connection info
graph = Neo4jGraph(
    url="bolt://98.82.11.37:7687",
    username="neo4j",
    password="stump-refund-signatures",
)  # connection info
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(model="gpt-4o", temperature=0, api_key=API_KEY),
    graph=graph,
    verbose=True,
)

# chain.run("Who played in Top Gun?")
chain1 = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, api_key=API_KEY)

while True:
    chat_history = []
    user_input = input("입력:")
    result = chain.run(user_input)
    result1 = chain1.invoke(
        input="Cypher query결과를 바탕으로 고객에게 적절한 분석결과를 명료하게(3문장 이내) 제공하세요. 고객의 발화:"
        + user_input
        + "\n\n cypher query 결과:"
        + result
        + "chat_history:{chat_history}"
    )
    chat_history.extend(
        [HumanMessage(content=user_input), AIMessage(content=result1.content)]
    )
    print(result1.content)
