from langgraph.prebuilt import create_agent_executor
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
import os
from uuid import uuid4
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.tools import BaseTool
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import pandas as pd

OPENAI_API_KEY='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'

unique_id = uuid4().hex[0:8]
# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key




print("필요한 파일을 불러오는중...")
loader1 = CSVLoader('./data/주행관련VOC테스트_입력_이슈.csv')
# loader2 = CSVLoader('./data/주행관련VOC테스트_이슈_원인.csv')


data1 = loader1.load()
#data2 = loader2.load()


issue_data1 = data1
#issue_data2 = data2



#print(data)

def create_vector_store_as_retriever(data, str1, str2):

    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
    docs = text_splitter.split_documents(data)


    embedding=OpenAIEmbeddings(openai_api_key =OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

    retriever = vectorstore.as_retriever()
    
    tool = create_retriever_tool(
        retriever,
        str1,
        str2,
    )
    
    return tool


rag = create_vector_store_as_retriever(data= issue_data1, str1="KT_Robot_Customer_Issue_Guide", str2="Find appropriate issue categories from user input")



from langchain.pydantic_v1 import BaseModel, Field

class CSVProcessInput(BaseModel):
    issue_value: list = Field(description="이슈 분류를 입력")



class PreProcessCSV(BaseTool):
    """Convert CSV file to pandas dataframe."""
    name = "Classifier"
    description = "useful for when you need to find the cause about issues"
    args_schema: Type[BaseModel] = CSVProcessInput
    return_direct: bool = False

    def _run(
        self, issue_value :list, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        for issue in issue_value:
            csv_path= './data/주행관련VOC테스트_이슈-원인0123.csv'

            df = pd.read_csv(csv_path)

            selected_rows = df[df['이슈분류'] == issue]

            # 원인을 탐색하고 각 원인이 얼마나 발생했는지 정규화하여 저장
            issue_counts = selected_rows['원인(원인별명)'].value_counts(normalize=True)

            # 각 원인에 대한 '고객조치가능여부' 값 가져오기
            customer_actions = selected_rows.groupby('원인(원인별명)')['고객조치가능여부'].first()
            detail_actions = selected_rows.groupby('원인(원인별명)')['조치 방법'].first()

            # DataFrame으로 변환
            result_df = pd.DataFrame({
                '원인': issue_counts.index,
                '고객조치가능여부': customer_actions.loc[issue_counts.index].values,
                '빈도': issue_counts.values,
                '조치 방법': detail_actions.loc[issue_counts.index].values
            })

            result_df = result_df.sort_values(by=['고객조치가능여부', '빈도'], ascending=[False, False])
            # result_df = result_df.sort_values(by=['빈도'], ascending=[False])
            print('--------------')
            print(result_df)
            print('--------------')

        return result_df
    


preprocess_csv_tool = PreProcessCSV()


# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", api_key=OPENAI_API_KEY)

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI



def create_agent(
    llm: ChatOpenAI, tools: list, system_prompt: str
):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}



from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

members = ["Retriever", "Classifier"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  {members}. "
    " {members}들 중 하나의 task가 종료되면 바로 FINISH로 응답하고, 고객의 다음 발화를 기다려."
    " {members}와 관련 없는 일반적인 질문은 그냥 너가 바로 대답해."
)
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members
# Using openai function calling can make output parsing easier for us
function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "anyOf": [
                    {"enum": options},
                ],
            }
        },
        "required": ["next"],
    },
}
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", api_key=OPENAI_API_KEY) #"gpt-4-1106-preview")


from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from operator import itemgetter

#초기 메모리 선언
memory = ConversationBufferMemory(return_messages=True)
print(memory.load_memory_variables({}))

supervisor_chain = (
        # RunnablePassthrough.assign(
        # history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        # )      
    prompt
    | llm.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)


prompt1 = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 로봇 사용 고객의 VOC를 처리하는 챗봇입니다. 고객님의 이슈가 어떤 이슈 분류에 해당하는지 검색해주세요."),
        # MessagesPlaceholder(variable_name="messages"),
        # (
        #     "system",
        #     "Given the conversation above, who should act next?"
        #     " Or should we FINISH? Select one of: {options}",
        # ),        
        
        
    ]
)


prompt2 = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 로봇 사용 고객의 VOC를 처리하는 챗봇입니다. 사용자의 이슈가 어떤 이슈 분류에 해당하는지 검색해주세요.{검색결과}를 기반으로 해당되는 이슈분류 하나를 찾아서 한 단어로 답하세요."),

    ]        
    
)

from langchain_core.output_parsers import StrOutputParser

chain1 = (
    # RunnablePassthrough.assign(
    #     history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    # )
    prompt1
    | llm
    | StrOutputParser()
    | rag
)

chain2 = (
    { "검색결과": chain1}
    | prompt2
    | llm
    | StrOutputParser()
)








import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import functools

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


# rag_agent = create_agent(llm, [rag], "유저입력을 기반으로, 어떤 이슈 분류에 해당하는지 검색하고, 이를 한 단어로 표현해주세요.")
# rag_node = functools.partial(agent_node, agent=rag_agent, name="Retriever")

# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION. PROCEED WITH CAUTION
# code_agent = create_agent(llm, [python_repl_tool], "You may generate safe python code to analyze data and generate charts using matplotlib.")
# code_node = functools.partial(agent_node, agent=code_agent, name="Coder")
cause_classification_agent = create_agent(llm, [preprocess_csv_tool], "이슈 분류를 입력하여 원인 Dataframe을 return해주세요.")
class_node = functools.partial(agent_node, agent=cause_classification_agent, name="Classifier")

workflow = StateGraph(AgentState)
workflow.add_node("Retriever", chain2)
workflow.add_node("supervisor", supervisor_chain)
workflow.add_node("Classifier", class_node)

for member in members:
    # We want our workers to ALWAYS "report back" to the supervisor when done
    workflow.add_edge(member, "supervisor")
# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
# Finally, add entrypoint
workflow.set_entry_point("supervisor")

graph = workflow.compile()

#print(len(graph.stream))
print(type(graph.stream))

while True:
    user_input = input("대화를 입력하세요:")
    for s in graph.stream(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        {"recursion_limit": 100},

    ):
        if "__end__" not in s:
            print(s)
            print("----")




    '''
    0. 글로벌 상태 관제 --> Agent 0

    1. 고객 발화를 통해 "이슈"를 분류  --> Agent 1

    2. 이슈가 분류되면 그에 해당하는 "원인"을 뽑아내고,
    3. 해당 "원인"을 순서대로 정렬함.(고객 조치가능한 순, 발생 빈도가 높은 순) --> Agent2

    4. 정렬된 "원인" 순서대로 해당 원인을 유발하는 행동을 한적 있는지 하나씩 고객에게 질문함.(각 원인들을 체크했는지 상태관리 필요) --> Agent3

        5. "맞다"고 했을 때, 

            5.1. 조치 가능하다면 조치 방법 안내
            5.2. 조치 불가능하다면 A/S출동 기사 연결 안내
            
        6. "아니다" 또는 "모르겠다" 라고 했을 때, 4번으로 이동하여 반복

        7. 모든 원인에 대해서 "아니다" 또는 "모르겠다" 라고 할 시, A/S출동 기사 연결 안내


    '''