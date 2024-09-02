import os 
from chatbot_tools.issue_rag import create_vector_store_as_retriever
from chatbot_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate

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

tool_symptom = [rag_symptom]#
tool_manual = [rag_manual]

#prompt1 = hub.pull("hwchase17/react-chat")

general_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
general_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
general_prompt.template = '''

You are the general manager of the team that handles inconveniences with KT service robots.

Depending on what the customer says, an appropriate expert must be called to provide guidance on the cause and measures to be taken.
If the customer makes a comment that is unrelated to the symptoms or cause, respond appropriately and encourage them to focus on the conversation again.
Ask the previously called agent again the question it was asking and encourage it to return to the original conversation flow.

The team members you can call are the four experts below.

- Symptom expert: When the customer tells us their symptoms, we create one summarized word that expresses the symptom.
- Cause expert: Based on the symptoms derived by the symptom identification expert, appropriate causes are searched, and these causes are questioned one by one by the customer in a 20-game format.
- Action expert: Once the cause is identified, appropriate action will be taken.
- Manual expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.


Once you decide which expert to call, indicate that expert at the beginning of your answer sentence.
```
(Example, When you have the right experts to call.)
User: 로봇이 동작을 못하고 멈칫거려.
AI: [Symptom expert]에게 전달
User: 로봇을 충전기에 연결하는 방법을 알려주세요.
AI: [Manual expert]에게 전달

(Example, If you don't have the right expert to call)
User: 오늘 저녁은 뭐먹을까요?
AI: [General expert] 오늘 저녁은 맛있는 된장찌개 어떠세요? KT로봇 사용중 불편한 점이 있으시다면 말씀해주세요.

(Example, while determining the cause)
AI: [Cause expert] 센서에 이물질이 묻지는 않았나요?
User: 안녕하세요 된장찌개가 먹고싶네요.
AI: [Cause expert] 된장찌개는 오늘 저녁에 드시면 되겠네요! 지금은 고객님의 원인파악이 우선이니, 다시 여쭤볼게요. 센서에 이물질이 묻지는 않았나요?

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
# print(type(prompt1))
# print(prompt1)



symptom_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
symptom_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
symptom_prompt.template = '''

You are Symptom exprt for KT service robot, You are one of the experts in this team of four people.
- Symptom expert: When the customer tells us their symptoms, we create one summarized word that expresses the symptom.
- Cause expert: Based on the symptoms derived by the symptom identification expert, appropriate causes are searched, and these causes are questioned one by one by the customer in a 20-game format.
- Action expert: Once the cause is identified, appropriate action will be taken.
- Manual expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.

```
(Example)
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



cause_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
cause_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
cause_prompt.template = '''

You are Cause exprt for KT service robot, You are one of the experts in this team of four people.

- Symptom expert: When the customer tells us their symptoms, we create one summarized word that expresses the symptom.
- Cause expert: Based on the symptoms derived by the symptom identification expert, appropriate causes are searched, and these causes are questioned one by one by the customer in a 20-game format.
- Action expert: Once the cause is identified, appropriate action will be taken.
- Manual expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.

```
(Example)
User: 고객의 원인에 대해 스무고개 형태로 파악해주세요.
AI: [Cause expert] 센서에 이물질이 묻어있지는 않나요?
User: 아니오.
AI: ...

```
If the customer says something unrelated to determining the cause during the Q&A, 
respond appropriately and then ask again about the cause that was previously asked.

Keep all questions and answers concise and limited to two sentences or less.

All response must be answered in korean.
Begin!

Previous conversation history:
{chat_history}


New input: {input}
{agent_scratchpad}
'''





manual_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
manual_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history', 'tool_manual']
manual_prompt.template = '''

You are Manual expert for KT service robot, You are one of the experts in this team of four people.
- Symptom expert: When the customer tells us their symptoms, we create one summarized word that expresses the symptom.
- Cause expert: Based on the symptoms derived by the symptom identification expert, appropriate causes are searched, and these causes are questioned one by one by the customer in a 20-game format.
- Action expert: Once the cause is identified, appropriate action will be taken.
- Manual expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.

```
```
If necessary, actively use {tool_manual} to answer.

Keep all questions and answers concise and limited to two sentences or less.

All response must be answered in korean.
Begin!

Previous conversation history:
{chat_history}


New input: {input}
{agent_scratchpad}
'''




#print('P1',prompt1)



from langchain.agents import AgentExecutor


chat_history = []



general_agent = create_openai_functions_agent_with_history(llm_model, tool_symptom, general_prompt)

symptom_agent = create_openai_functions_agent_with_history(llm_model, tool_symptom, symptom_prompt)

cause_agent = create_openai_functions_agent_with_history(llm_model, tool_symptom, cause_prompt)
action_agent = create_openai_functions_agent_with_history(llm_model, tool_symptom, general_prompt)

manual_agent = create_openai_functions_agent_with_history(llm_model, tool_manual, manual_prompt)






while True:
    user_input = input('입력:')
    
    general_agent_executor = AgentExecutor(agent=general_agent, tools=tool_symptom, verbose=True)
    response= general_agent_executor.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_input),
            AIMessage(content=response["output"]),
        ]
    )
    general_res = response["output"]
    print('[Log: ',general_res,']')

    #증상 파악 및 분류시 바로 원인 분석 시작

    if 'Symptom' in general_res :
        ask_symptom = '{chat_history}를 분석하여, 고객의 증상을 최종 분류해주세요.'
        symptom_agent_executor = AgentExecutor(agent=symptom_agent, tools=tool_symptom, verbose=True)
        response= symptom_agent_executor.invoke({"input": ask_symptom, "chat_history": chat_history})
        chat_history.extend(
            [
                AIMessage(content=ask_symptom),
                AIMessage(content=response["output"]),
            ]
        )
        
        print('\nAI: ',response["output"])
        
        #원인 분석 강제 입력
        ask_cause = '해당증상과 관련된 고객의 원인을 스무고개 형태로 파악해주세요. 질문을 먼저 시작해주세요.'
        cause_agent_executor = AgentExecutor(agent=cause_agent, tools=tool_symptom, verbose=True)
        response= cause_agent_executor.invoke({"input": ask_cause, "chat_history": chat_history})
        chat_history.extend(
            [
                AIMessage(content=ask_cause),
                AIMessage(content=response["output"]),
            ]
        )
        
        print('\nAI: ',response["output"])

        
    elif 'Manual' in general_res :
        ask_manual = '{chat_history}에서 고객의 가장 최근 질문에 대해서 답해주세요.'
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
    

    '''
    3.11의견:
    VOC처리 모듈에서 Manual Expert에 할당이되면, 
    "더 정확한 답변을 위해, 매뉴얼 처리 탭을 눌러서 질문 부탁드립니다."라는 발화만 하고 넘길 것.
    '''



    


