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


# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", api_key=OPENAI_API_KEY)




from langchain.tools.render import format_tool_to_openai_function

def create_agent(llm, tools, system_message: str):
    """Create an agent."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " Answer in korean"
                " You have access to the following tools: {tool_names}.\n{system_message}"
                " \n{system_message}"
                "\nchat_history:{history}" 
            ),
            MessagesPlaceholder(variable_name="history"),            
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    if tools != None :
        

        functions = [format_tool_to_openai_function(t) for t in tools]
    
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        chain = RunnablePassthrough.assign(
                history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
            ) |prompt | llm.bind_functions(functions)
        
    else: 
        prompt = prompt.partial(tool_names='')
        prompt = prompt.partial(system_message=system_message)
        chain = RunnablePassthrough.assign(
                history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
            ) |prompt | llm
        
    return chain


# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    result = agent.invoke(state)
    
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, FunctionMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


#gpt-4-0613


#초기 메모리 선언
memory = ConversationBufferMemory(return_messages=True)
print(memory.load_memory_variables({}))






# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


members = ['Researcher', 'Consultant', 'Cause Classificator'] #
decision_agent = create_agent(llm, None, 
                              system_message= '''
                              You are a general purpose supervisor tasked with managing a conversation between the following workers:  {members}. Given the following user request, respond with the worker to act next. 
                              Each worker will perform a task and respond with their results and status. 
                                '''
                            )
decision_node = functools.partial(agent_node, agent=decision_agent, name="DecisionMaker")


rag_agent = create_agent(llm, [rag], system_message="{messages} 기반으로, 어떤 이슈분류에 해당하는지 검색하고, 가장많이 검색된 {이슈분류}를 return 하세요.")
rag_node = functools.partial(agent_node, agent=rag_agent, name="Researcher")


cause_classification_agent = create_agent(llm, [preprocess_csv_tool], system_message="{이슈분류}를 기반으로 원인 리스트를 return하세요.")
class_node = functools.partial(agent_node, agent=cause_classification_agent, name="Cause Classificator")

consulting_agent = create_agent(llm, None, system_message="cause_list의 첫번째 요소를 유발하는 행동을 혹시 최근에 한적 있는지 물어봐주세요.")
consulting_node = functools.partial(agent_node, agent=consulting_agent, name="Consultant")



tools = [rag, preprocess_csv_tool]
tool_executor = ToolExecutor(tools)

def tool_node(state):
    """This runs tools in the graph

    It takes in an agent action and calls that tool and returns the result."""
    messages = state["messages"]
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation from the function_call
    tool_input = json.loads(
        last_message.additional_kwargs["function_call"]["arguments"]
    )
    # We can pass single-arg inputs by value
    if len(tool_input) == 1 and "__arg1" in tool_input:
        tool_input = next(iter(tool_input.values()))
    tool_name = last_message.additional_kwargs["function_call"]["name"]
    action = ToolInvocation(
        tool=tool_name,
        tool_input=tool_input,
    )
    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    # We use the response to create a FunctionMessage
    function_message = FunctionMessage(
        content=f"{tool_name} response: {str(response)}", name=action.tool
    )
    # We return a list, because this will get added to the existing list
    return {"messages": [function_message]}


# Either agent can decide to end
def router(state):
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if "function_call" in last_message.additional_kwargs:
        # The previus agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return "end"
    return "continue"


workflow = StateGraph(AgentState)

workflow.add_node("DecisionMaker", decision_node)

workflow.add_node("Researcher", rag_node) #이슈 분류기
workflow.add_node("Cause Classificator", class_node) # 원인 정렬기
workflow.add_node("Consultant", consulting_node)

workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {"continue": "Cause Classificator", "call_tool": "call_tool", "end": END},
)
workflow.add_conditional_edges(
    "Cause Classificator",
    router,
    {"continue": "Consultant", "call_tool": "call_tool", "end": END},
)

workflow.add_conditional_edges(
    "Consultant",
    router,
    {"continue": END, "call_tool": "call_tool", "end": END},
)

workflow.add_conditional_edges(
    "DecisionMaker",
    router,
    {"continue": "Researcher", "call_tool": "call_tool", "end": END},
)

workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "Cause Classificator": "Cause Classificator",
        # "Consultant": "Consultant",
        # "DecisionMaker": "DecisionMaker",
        
    },
)

workflow.set_entry_point("DecisionMaker")


while True:
    graph = workflow.compile()    

    user_input = input('대화를 입력하세요: ')
    start = False
    memory.save_context({"input": user_input}, {"output": ''}) #response.content

    for s in graph.stream(
        {
            "messages": [
                HumanMessage(
                    content=user_input
                )
            ],
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": 150},
    ):
        memory.save_context({"input":''}, {"output": str(s)}) #response.content

        print(s)
        print("----\n\n\n")

        #print('\n\n\n챗히스토리',memory.load_memory_variables({}),'\n\n\n')

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