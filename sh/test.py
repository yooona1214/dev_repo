import os
#from custom_tools.preprocesscsv import PreProcessCSV
from custom_tools.issue_rag import create_vector_store_as_retriever
from custom_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, PyPDFDirectoryLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent, Tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain.tools.retriever import create_retriever_tool
OPENAI_API_KEY = 'sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe'
os.environ["SERPER_API_KEY"] = ("d8e1922de1a749051dfaf37d7c38990df9c791a5")
#os.environ["LANGCHAIN_TRACING_V2"] = "true"
#os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
#os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
#os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key
print("필요한 파일을 불러오는중...")
loader1 = PyPDFDirectoryLoader('./data')
data1 = loader1.load()
rag_edu = create_vector_store_as_retriever(data= data1, str1="data_Note",
                                       str2="Paper's for")
from langchain.utilities import GoogleSerperAPIWrapper
google_search = GoogleSerperAPIWrapper()
g_search = Tool(
    name="Google_search",
    func=google_search.run,
    description="useful for when you need to search in Google")
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY, temperature=0)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY, temperature=0)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY, temperature=0)
llm_4_o = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY, temperature=0)
llm_model = llm_4_o
from langchain import hub
tool_lecture = [g_search] #rag_edu
general_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
#(specified in the 'Cause' column of the csv file)
general_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
general_prompt.template = '''
You are the assistance for
Begin!
Previous conversation history:
{chat_history}
New input: {input}
{agent_scratchpad}
'''
# print(type(prompt1))
# print(prompt1)
from langchain.agents import AgentExecutor
chat_history = []
general_agent = create_openai_functions_agent_with_history(llm_model, tool_lecture, general_prompt)
while True:
    user_input = input('입력:')
    general_agent_executor = AgentExecutor(agent=general_agent, tools=tool_lecture, verbose=True)
    response= general_agent_executor.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_input),
            AIMessage(content=response["output"]),
        ]
    )
    #general_res = response["output"]
    print('\nAI: ',response["output"])