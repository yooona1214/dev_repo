import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"
os.environ["GPT_MODEL"] = "gpt-3.5-turbo"

# Neo4j 연결 정보 설정

from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from prompts.prompt import LLM_INPUTS, LLM_PROMPTS, GRAPH_INPUTS, GRAPH_PROMPTS


graph = Neo4jGraph(
    url="neo4j+s://9bb7f8ec.databases.neo4j.io",
    username="neo4j",
    password="6divqnk_LBw-7zrAsvxNXvVCirJwboIbfSnU0FSYkCw",
)

# graph = Neo4jGraph(
#     url="neo4j+s://0d811677.databases.neo4j.io",
#     username="neo4j",
#     password="dJX89oapsNHdhFZRDM1K8wvrVk-joveEL802qKr0YCM",
# )  # connection info
# graph = Neo4jGraph(
#     url="bolt://100.24.123.52:7687",
#     username="neo4j",
#     password="wholesales-entry-arithmetic",
# )  # connection info
graphql_chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0, api_key=API_KEY, model="gpt-4o"),
    graph=graph,
    verbose=True,
)

system_prompt = PromptTemplate(input_variables=LLM_INPUTS, template=LLM_PROMPTS)
graphql_prompt = PromptTemplate(input_variables=GRAPH_INPUTS, template=GRAPH_PROMPTS)
llm1 = ChatOpenAI(model="gpt-4o", temperature=0, api_key=API_KEY)
llm2 = ChatOpenAI(model="gpt-4o", temperature=0, api_key=API_KEY)

chain_router = system_prompt | llm1
chain1 = graphql_prompt | llm1

chat_history = []
while True:

    user_input = input("입력:")

    router_result = chain_router.invoke(
        {"input": user_input, "chat_history": chat_history}
    )

    if "GraphDB" in router_result.content:

        graph_ql_result = graphql_chain.run(router_result)
        result1 = chain1.invoke(
            {
                "input": "너는 Graph db 전문가야. 고객의 발화를 듣고, 해당 발화에 적절한 증상을 찾아낸 뒤, 대응되는 원인을 알려주는 역할이야. Cypher query 결과를 통해 entity와 edge간의 관계를 분석하고, 고객의 발화에 맞게 그 결과를 명료하게 제공하세요. 고객의 발화와 Cypher query결과는 아래와 같습니다."
                + "\n\n 고객의 발화:"
                + router_result.content
                + "\n\n cypher query 결과:"
                + graph_ql_result,
                "chat_history": chat_history,
            }
        )

        chat_history.extend(
            [HumanMessage(content=user_input), AIMessage(content=result1.content)]
        )
        print("f")
        print(result1.content)

    else:
        chat_history.extend(
            [HumanMessage(content=user_input), AIMessage(content=router_result.content)]
        )

        print("h")
        print(router_result.content)
        # print(chat_history)
