import os

# setup OpenAI API Key with yours
os.environ["OPENAI_API_KEY"] = (
    "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"  # set with yours
)

# Connect to the PostgreSQL DB
from langchain_community.utilities import SQLDatabase

# set with yours
username = "postgres"
password = "rbrain!"
host = "localhost"
port = "5432"
database = "agentdb"

pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

db = SQLDatabase.from_uri(pg_uri)


# Helper functions
def get_schema(_):
    return db.get_table_info()


def run_query(query):
    return db.run(query)


# Prompt for generating a SQL query
from langchain.prompts import ChatPromptTemplate

template_query = """
Based on the table schema below,
Write a PostgreSQL query that answer the user's question:
{schema}

Question: {question}
SQL Query:"""

prompt = ChatPromptTemplate.from_template(template_query)


# Chaining prompt, LLM model, and Output Parser
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

model = ChatOpenAI(temperature=0, model_name="gpt-4-0125-preview")

sql_response = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | model.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)

#a = sql_response.invoke({"question": "How many staff in there"})

#print(a)


# Prompt for generating the final answer by running a SQL query on DB
template_response = """
Based on the table schema below, question, sql query, and sql response,
write a natural language response:
{schema}

Question: {question}
SQL Query: {query}
SQL Response: {response}"""

prompt_response = ChatPromptTemplate.from_template(template_response)

full_chain = (
    RunnablePassthrough.assign(query=sql_response)
    | RunnablePassthrough.assign(
        schema=get_schema,
        response=lambda x: db.run(x["query"]),
    )
    | prompt_response
    | model
    | StrOutputParser()
)

a = full_chain.invoke({"question": "이 db의 테이블 총 갯수는?"})

print(a)