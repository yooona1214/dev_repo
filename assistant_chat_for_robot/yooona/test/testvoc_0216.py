from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import PyPDFLoader, CSVLoader

import os
from uuid import uuid4
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

import json

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
)
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation
import functools

from chatbot_tools.preprocesscsv import PreProcessCSV
from chatbot_tools.issue_rag import create_vector_store_as_retriever


import operator
from typing import Annotated, List, Sequence, Tuple, TypedDict, Union

from langchain.agents import create_openai_functions_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from operator import itemgetter

OPENAI_API_KEY='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'

#unique_id = uuid4().hex[0:8]
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

# tool 선언
rag = create_vector_store_as_retriever(data= issue_data1, str1="KT_Robot_Customer_Issue_Guide", str2="Find appropriate issue categories from user input")

preprocess_csv_tool = PreProcessCSV()

tools = [rag, preprocess_csv_tool]

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", api_key=OPENAI_API_KEY)




from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers.openai_functions import (
    OpenAIFunctionsAgentOutputParser,
)

def create_agent(llm, tools, system_message: str):
    """Create an agent."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
            '''
            Assistant has access to the following tools:

            {tools}

            To use a tool, please use the following format:

            ```
            Thought: Do I need to use a tool? Yes
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ```

            When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

            ```
            Thought: Do I need to use a tool? No
            Final Answer: [your response here]
            ```

            Begin!

            Previous conversation history:
            {chat_history}

            New input: {input}
            {agent_scratchpad}
            '''
            ),
            MessagesPlaceholder(variable_name="history"),            
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

        

    functions = [format_tool_to_openai_function(t) for t in tools]

    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    chain = RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        ) |prompt | llm.bind_functions(functions)| OpenAIFunctionsAgentOutputParser()

    
        
    return chain




#초기 메모리 선언
memory = ConversationBufferMemory(return_messages=True)
print(memory.load_memory_variables({}))


agent = create_agent(llm=llm, tools=tools, system_message="")

while True:

    user_input=input('입력:')
    ans = agent.invoke({'messages': [
                    HumanMessage(
                        content=user_input
                    )
                ],})

    print(ans)
# user_input = input()
# rag_agent.invoke({'messages':user_input})

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