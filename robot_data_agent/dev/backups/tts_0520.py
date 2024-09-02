import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentExecutor
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage


from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


# OpenAI

# setup OpenAI API Key with yours
os.environ["OPENAI_API_KEY"] = (
    "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"  # set with yours
)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Text2SQL Test"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"


# Connect to the PostgreSQL DB
username = "postgres"
password = "rbrain!"
host = "localhost"
port = "5432"
database = "agentdb"
pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

db = SQLDatabase.from_uri(pg_uri)


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


Previous conversation history:
{chat_history}


"""


# LLM model
llm_4 = ChatOpenAI(model="gpt-4-0613")
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview")
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125")

llm = llm_3_5

# tool
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = []

# Agent 선언
sql_agent = create_sql_agent(
    llm,
    toolkit=toolkit,
    prefix=prefix_template,
    format_instructions=format_instructions_template,
    agent_type="openai-tools",
    verbose=True,
)

chat_history = []


def main():

    while True:
        question = input("Q: ")
        response = sql_agent.invoke({"input": question, "chat_history": chat_history})

        chat_history.extend(
            [
                HumanMessage(content=question),
                AIMessage(content=response["output"]),
            ]
        )

        print("first query is done!!!!", response["output"])


if __name__ == "__main__":
    main()
