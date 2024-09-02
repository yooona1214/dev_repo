# Human-in-the-graphLLM-loop

import os
import json
import operator
from typing import TypedDict, Annotated, Sequence

from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_openai import ChatOpenAI
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import FunctionMessage, BaseMessage

OPENAI_API_KEY='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'



# Set up the tools
tools = ["???"]

tool_executor = ToolExecutor(tools)

llm = ChatOpenAI(temperature=0,model="gpt-3.5-turbo", api_key=OPENAI_API_KEY, streaming = True)

functions = [format_tool_to_openai_function(t) for t in tools]
model = llm.bind_functions(functions)


# Define the agent state [StatefulGraph]
# SET specific attribute or ADD to the exisiting attribute 설정하거나 더하기
# In this case, the state we will track is a LIST of the messages. 
# So, we will use TypedDict with one key(messages) and annotate it so that the messages attribute is always added to
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# Define the nodes
# 1. the agent: responsible for deciding what actions to take 행동 결정 에이전트
# 2. invoking tools: 에이전트가 결정한 행동(tool)을 실행하는 함수
# Define the edges
# 1. conditional edge: 에이전트가 내논 답변에 의해 invoke tool을 할지 끝낼지 결정
# 2. normal edge: tool이 invoke된후, 에이전트한테 다시 가서 뭐할지 결정

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state['messages']
    last_message = messages[-1]
    # If there is no function call, then we finish
    if "function_call" not in last_message.additional_kwargs:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"

# Define the function that calls the model
def call_model(state):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}
    
# Define the function to execute tools
def call_tool(state):
    messages = state['messages']
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct an ToolInvocation from the function_call
    action = ToolInvocation(
        tool=last_message.additional_kwargs["function_call"]["name"],
        tool_input=json.loads(last_message.additional_kwargs["function_call"]["arguments"]),
    )
    response = input(f"[y/n] continue with: {action}?")
    if response == "n":
        raise ValueError
    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    # We use the response to create a FunctionMessage
    function_message = FunctionMessage(content=str(response), name=action.tool)
    # We return a list, because this will get added to the existing list
    return {"messages": [function_message]}