import os 
from chatbot_tools.issue_rag import create_vector_store_as_retriever
from chatbot_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

OPENAI_API_KEY='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'

#unique_id = uuid4().hex[0:8]
# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key




print("필요한 파일을 불러오는중...")
loader1 = CSVLoader('./data/엘지_0226.csv')
loader2 = CSVLoader('./data/베어_0226.csv')
loader3 = PyPDFLoader('./data/LG1세대[FnB2.0]_사용자매뉴얼.pdf')
data1 = loader1.load()
#data2 = loader2.load()
        #     loader = PyPDFLoader("LG2.pdf")

data3 = loader3.load()

issue_data = data1
manual_data = data3
# tool 선언
rag_symptom = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
                                       str2="Please search for and return the most relevant symptom name based on {user_input}.")

# rag_cause = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
#                                        str2="Please search for and return all the most relevant cause names based on {user_input}.")

rag_manual = create_vector_store_as_retriever(data= manual_data, str1="LG_Robot_Manual_Guide", 
                                       str2="Please search for and return the most relevant contents based on {user_input}.")


# Choose the LLM that will drive the agent
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

llm_model = llm_4_t
from langchain import hub 
from langchain import hub

tools = [rag_symptom]#
tool_manual = [rag_manual]

prompt1 = hub.pull("hwchase17/react-chat")
prompt1.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']

prompt1.template = '''

You are the general manager who handles inconveniences with KT service robots.

Depending on what the customer says, an appropriate expert must be called to provide guidance on the cause and measures to be taken.
If the customer makes a comment that is unrelated to the symptoms or cause, respond appropriately and encourage them to focus on the conversation again.

There are total of 4 experts you can call.
- Symptom expert: When the customer tells us their symptoms, we create one summarized word that expresses the symptom.
- Cause expert: Based on the symptoms derived by the symptom identification expert, appropriate causes are searched, and these causes are questioned one by one by the customer in a 20-game format.
- Action Expert: Once the cause is identified, appropriate action will be taken.
- Manual Expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.


Once you decide which expert to call, indicate that expert at the beginning of your answer sentence.
```
(Example, When you have the right experts to call.)
User: 로봇이 동작을 못하고 멈칫거려.
AI: [Symptom expert] 고객님의 증상은 "로봇 동작불가 및 멈칫 거림"으로 분류됩니다.

(Example, If you don't have the right expert to call)
User: 오늘 저녁은 뭐먹을까요?
AI: [General expert] 오늘 저녁은 맛있는 된장찌개 어떠세요? KT로봇 사용중 불편한 점이 있으시다면 말씀해주세요.

```

If you are unable to properly respond to the customer through your experts, offer to ultimately refer them to customer service.

Keep all questions and answers concise and limited to two sentences or less.

All response must be answered in korean.
Begin!

Previous conversation history:
{chat_history}


New input: {input}
{agent_scratchpad}
'''



prompt2 = hub.pull("hwchase17/react-chat")
prompt2.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']

prompt2.template = '''

You are Symptom exprt for KT service robot
- Symptom expert: When the customer tells us their symptoms, we create one summarized word that expresses the symptom.

User: 로봇이 동작을 못하고 멈칫거려.
AI: [Symptom expert] 고객님의 증상은 "로봇 동작불가 및 멈칫 거림"으로 분류됩니다.

```

Keep all questions and answers concise and limited to two sentences or less.

All response must be answered in korean.
Begin!

Previous conversation history:
{chat_history}


New input: {input}
{agent_scratchpad}
'''



#print('P1',prompt1)



from langchain.agents import AgentExecutor, create_openai_functions_agent


chat_history = []



general_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)
symptom_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt2)
cause_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)
action_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)

manual_agent = create_openai_functions_agent_with_history(llm_model, tool_manual, prompt1)






while True:
    user_input = input('입력:')
    
    general_agent_executor = AgentExecutor(agent=general_agent, tools=tools, verbose=True)
    response= general_agent_executor.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_input),
            AIMessage(content=response["output"]),
        ]
    )
    general_res = response["output"]


    if 'Symptom' in general_res :
        ask_cause = '해당증상과 관련된 고객의 원인을 스무고개 형태로 파악해주세요. 질문을 먼저 시작해주세요.'
        symptom_agent_executor = AgentExecutor(agent=symptom_agent, tools=tools, verbose=True)
        response= symptom_agent_executor.invoke({"input": ask_cause, "chat_history": chat_history})
        chat_history.extend(
            [
                AIMessage(content=ask_cause),
                AIMessage(content=response["output"]),
            ]
        )
        
        print('\nAI: ',response["output"])

        
    elif 'Manual' in general_res :
        ask_manual = '고객의 이전 질문에 대해 적절히 답해주세요.'
        manual_agent_executor = AgentExecutor(agent=manual_agent, tools=tool_manual, verbose=True)
        response= general_agent_executor.invoke({"input": ask_manual, "chat_history": chat_history})
        chat_history.extend(
            [
                AIMessage(content=ask_manual),
                AIMessage(content=response["output"]),
            ]
        )
        
        print('\nAI: ',response["output"])

    else:
        print('\nAI: ',general_res)

    
    #print('\n\n\n',chat_history)
    





    


