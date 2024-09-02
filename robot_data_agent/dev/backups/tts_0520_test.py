import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain

from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool


from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings


# setup OpenAI API Key with yours
os.environ["OPENAI_API_KEY"] = (
    "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"  # set with yours
)

# Connect to the PostgreSQL DB
username = "postgres"
password = "rbrain!"
host = "localhost"
port = "5432"
database = "agentdb"
pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

db = SQLDatabase.from_uri(pg_uri)

print(db.dialect)


_postgres_prompt = """You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per PostgreSQL. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

최종 답변은 실제 db에 바로 입력시킬 수 있도록 쿼리문만 출력해줘.
답변예시:
SELECT "~~~

"""
PROMPT_SUFFIX = """Only use the following tables:
{table_info}

Question: {input}"""

POSTGRES_PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "top_k"],
    template=_postgres_prompt + PROMPT_SUFFIX,
)


# LLM model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm2 = ChatOpenAI(model="gpt-4o", temperature=0)

generate_query = create_sql_query_chain(llm, db, prompt=POSTGRES_PROMPT)
generate_query2 = create_sql_query_chain(llm2, db, prompt=POSTGRES_PROMPT)

while True:
    user_input = input("입력:")
    query = generate_query.invoke({"question": user_input})
    # "what is price of `1968 Ford Mustang`"
    print("SQL query문: ", query)

    # query = """SELECT "last_name"
    # FROM "actor"
    # WHERE "first_name" = 'Nick'
    # LIMIT 1;"""


    # Executed sql result
    execute_query = QuerySQLDataBaseTool(db=db)
    executed_result = execute_query.invoke(query)
    print("Executed Result: ", executed_result)


    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    
    Question: {user_input}
    SqlQuery Result: {executed_result}
    Answer: """
    )

    rephrase_answer = answer_prompt | llm | StrOutputParser()

    chain = (
        RunnablePassthrough.assign(query=generate_query2).assign(
            result=itemgetter("query") | execute_query
        )
        | rephrase_answer
    )

    rephrase_result = chain.invoke({"question": "", "user_input": user_input, "executed_result": executed_result})
    print("\n\n답: ", rephrase_result)
