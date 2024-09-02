import os
os.environ["OPENAI_API_KEY"] = "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"

username = "postgres"
password = "rbrain!"
host = "localhost"
port = "5432"
database = "agentdb"
 
from langchain_community.utilities.sql_database import SQLDatabase
# db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=1,include_tables=['customers','orders'],custom_table_info={'customers':"customer"})
 
pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
db = SQLDatabase.from_uri(pg_uri)
print(db.dialect)
print(db.get_usable_table_names())
print(db.table_info)

from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
generate_query = create_sql_query_chain(llm, db)
query = generate_query.invoke({"question": "what is Mike's email?"})
# "what is price of `1968 Ford Mustang`"
print(query)


from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
execute_query = QuerySQLDataBaseTool(db=db)
execute_query.invoke(query)

from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

answer_prompt = PromptTemplate.from_template(
     """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

rephrase_answer = answer_prompt | llm | StrOutputParser()

chain = (
    RunnablePassthrough.assign(query=generate_query).assign(
        result=itemgetter("query") | execute_query
    )
    | rephrase_answer
)

chain.invoke({"question": "How many customers have an order count greater than 5"})
