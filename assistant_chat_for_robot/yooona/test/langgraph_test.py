import os
import json

from langchain_core.messages import (
    BaseMessage,
    FunctionMessage,
    HumanMessage,
)

from langchain.tools.render import format_tool_to_openai_function
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor, ToolInvocation

from langchain_core.tools import tool
from typing import Annotated
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools.tavily_search import TavilySearchResults
import operator
from typing import Annotated, Sequence, Tuple, TypedDict, Union
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict 

# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"

def create_agent(llm, tools, system_message: str):
    # 에이전트를 생성합니다.
    functions = [format_tool_to_openai_function(t) for t in tools]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join(
        [tool.name for tool in tools]))
    return prompt | llm.bind_functions(functions)

#tavily_tool = TavilySearchResults(max_results=5)

repl = PythonREPL()

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."]
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Succesfully executed:\n```python\n{code}\n```\nStdout: {result}"

# 각 에이전트와 도구에 대한 다른 노드를 생성할 것입니다. 이 클래스는 그래프의 각 노드 사이에서 전달되는 객체를 정의합니다.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    
    
    
import functools


def agent_node(state, agent, name):
    result = agent.invoke(state)
    if isinstance(result, FunctionMessage):
        pass
    else:
        result = HumanMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        "sender": name,
    }


llm = ChatOpenAI(model="gpt-3.5-turbo")

# Research agent and node
research_agent = create_agent(
    llm,
    [tavily_tool],
    system_message="You should provide accurate data for the chart generator to use.",
)
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

# Chart Generator
chart_agent = create_agent(
    llm,
    [python_repl],
    system_message="Any charts you display will be visible by the user.",
)
chart_node = functools.partial(agent_node, agent=chart_agent, name="Chart Generator")

tools = [tavily_tool, python_repl]
tool_executor = ToolExecutor(tools)


def tool_node(state):
    # 그래프에서 도구를 실행하는 함수입니다.
    # 에이전트 액션을 입력받아 해당 도구를 호출하고 결과를 반환합니다.
    messages = state["messages"]
    # 계속 조건에 따라 마지막 메시지가 함수 호출을 포함하고 있음을 알 수 있습니다.
    last_message = messages[-1]
    # ToolInvocation을 함수 호출로부터 구성합니다.
    tool_input = json.loads(
        last_message.additional_kwargs["function_call"]["arguments"]
    )
    # 단일 인자 입력은 값으로 직접 전달할 수 있습니다.
    if len(tool_input) == 1 and "__arg1" in tool_input:
        tool_input = next(iter(tool_input.values()))
    tool_name = last_message.additional_kwargs["function_call"]["name"]
    action = ToolInvocation(
        tool=tool_name,
        tool_input=tool_input,
    )
    # 도구 실행자를 호출하고 응답을 받습니다.
    response = tool_executor.invoke(action)
    # 응답을 사용하여 FunctionMessage를 생성합니다.
    function_message = FunctionMessage(
        content=f"{tool_name} response: {str(response)}", name=action.tool
    )
    # 기존 리스트에 추가될 리스트를 반환합니다.
    return {"messages": [function_message]}


def router(state):
    # 상태 정보를 기반으로 다음 단계를 결정하는 라우터 함수
    messages = state["messages"]
    last_message = messages[-1]
    if "function_call" in last_message.additional_kwargs:
        # 이전 에이전트가 도구를 호출함
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # 어느 에이전트든 작업이 끝났다고 결정함
        return "end"
    return "continue"




workflow = StateGraph(AgentState)

workflow.add_node("Researcher", research_node)
workflow.add_node("Chart Generator", chart_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {"continue": "Chart Generator", "call_tool": "call_tool", "end": END},
)
workflow.add_conditional_edges(
    "Chart Generator",
    router,
    {"continue": "Researcher", "call_tool": "call_tool", "end": END},
)

workflow.add_conditional_edges(
    "call_tool",
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "Chart Generator": "Chart Generator",
    },
)
workflow.set_entry_point("Researcher")
graph = workflow.compile()