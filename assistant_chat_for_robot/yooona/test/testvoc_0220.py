import os 
from chatbot_tools.issue_rag import create_vector_store_as_retriever
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_openai import ChatOpenAI

OPENAI_API_KEY='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'

#unique_id = uuid4().hex[0:8]
# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key




print("필요한 파일을 불러오는중...")
loader1 = CSVLoader('./data/엘지.csv')
#loader2 = CSVLoader('./data/고객자가진단리스트엘지.csv')

data1 = loader1.load()
#data2 = loader2.load()

issue_data = data1

# tool 선언
rag = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", str2="Please search for the customer's {input} at the symptom column and return the cause and action in same row.")


tools = [rag]

# Choose the LLM that will drive the agent
#llm = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
#llm = ChatOpenAI(model="gpt-3.5-turbo-1106", api_key=OPENAI_API_KEY)
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)


# prompt = '''
# Answer the following questions as best you can. You have access to the following tools:

# {tools}

# Use the following format:

# Question: the input question you must answer
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question

# Begin!

# Question: {input}
# Thought:{agent_scratchpad}
# '''


from langchain import hub 
prompt = hub.pull("hwchase17/react-chat")
prompt.template = '''
Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

TOOLS:
------

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
Plaese answer in korean
Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
'''
print('prompt:', prompt)

agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

while True:
    user_input = input('입력:')
    agent_executor.invoke({"input": user_input, "chat_history": ""})

