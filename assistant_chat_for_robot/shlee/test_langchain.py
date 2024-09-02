from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

OPENAI_API_KEY='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'


from langchain_core.runnables import RunnablePassthrough

from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults

search = DuckDuckGoSearchResults()


prompt = ChatPromptTemplate.from_template(
    " {topic}에 대해 잘 검색하도록 query를 만들어주세요."
)
output_parser = StrOutputParser()
model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
chain = (
    {"topic": RunnablePassthrough()} 
    | prompt
    | model
    | output_parser
    | search
)




res = chain.invoke('robotics')
print(res)
