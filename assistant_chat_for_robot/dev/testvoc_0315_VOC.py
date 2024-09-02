import os 
from custom_tools.preprocesscsv import PreProcessCSV
from custom_tools.issue_rag import create_vector_store_as_retriever
from custom_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_experimental.tools import PythonAstREPLTool
from langchain.tools.retriever import create_retriever_tool

OPENAI_API_KEY='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'

#unique_id = uuid4().hex[0:8]
# LangSmith 추적 기능을 활성화합니다. (선택적)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key




print("필요한 파일을 불러오는중...")
loader1 = CSVLoader('./data/LG0313.csv')
df = pd.read_csv('./data/LG0313.csv')
#python = PythonAstREPLTool(locals={"df": df})
#df_columns = df.columns.to_list()
loader2 = CSVLoader('./data/베어_0226.csv')
loader3 = PyPDFLoader('./data/LG1세대[FnB2.0]_사용자매뉴얼.pdf')
data1 = loader1.load()
#data2 = loader2.load()
        #     loader = PyPDFLoader("LG2.pdf")

data3 = loader3.load()

issue_data = data1
manual_data = data3
# tool 선언
rag_issue = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
                                       str2="This is a csv file containing symptoms, causes of symptoms, and action plans for the causes.")
#Please search for and return the most relevant symptom(words or sentences written in the symptoms column) name based on {user_input}.

# rag_cause = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
#                                        str2="Please search for and return all the most relevant cause names based on {user_input}.")

rag_manual = create_vector_store_as_retriever(data= manual_data, str1="LG_Robot_Manual_Guide", 
                                       str2="Please search for and return the most relevant contents based on {user_input}.")

#preprocess_csv_tool = PreProcessCSV()
'''
pandas_tool = PythonAstREPLTool(
                name = "KT_Robot_Customer_Issue_Data",
                func=python.run,
                description = f"""
                Useful for when you need to get causes about symthom in pandas dataframe 'df'. 
                Run python pandas operations on 'df' to help you get the right answer.
                'df' has the following columns: {df_columns}

                Based on the symptoms derived by the symptom expert, extract the csv file as follows : df[(df['증상']== 'symptoms derived by the symptom expert')]

                Extract only the ‘Cause’ column : causes2 = df.filter(regex='원인')
                
                To a cause expert, you can use the extracted causes in the order of frequency.
                """
            )
'''

#tools = [rag_issue, pandas_tool]

# Choose the LLM that will drive the agent
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

llm_model = llm_4_t
from langchain import hub 
from langchain import hub

tool_symptom = [rag_issue]#
tool_manual = [rag_manual]
final_symthom = ''

#prompt1 = hub.pull("hwchase17/react-chat")

general_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
#(specified in the 'Cause' column of the csv file)
general_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
general_prompt.template = '''

You are the general manager of the team that handles inconveniences with KT service robots.

Depending on what the customer says, an appropriate expert must be called to provide guidance on the cause and measures to be taken.
If the customer makes a comment that is unrelated to the symptoms or cause, respond appropriately and encourage them to focus on the conversation again.

The team members you can call are the four experts below.

- Symptom expert: When a customer describes their symptoms, refer to the 'Sentences in which the customer expressed their symptoms' column in the csv file and say the one most similar symptom based on the 'Symptoms' column.
- Cause expert: Ask customers one by one the causes in the 'Cause' column that match the symptoms derived by the symptom expert in the Twenty Questions game. At this time, ask in order of the most frequent causes.
- Action expert: Once the cause is identified, appropriate action will be taken. If dispatch for repairs is necessary, tell the customer that you will accept dispatch.
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
AI: [General expert] 오늘 저녁은 맛있는 된장찌개 어떠세요? 계속해서 상담을 진행할까요.

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
- Symptom expert: When a customer describes their symptoms, refer to the 'Sentences in which the customer expressed their symptoms' column in the csv file and say the one most similar symptom based on the 'Symptoms' column.
- Cause expert: Ask customers one by one the causes in the 'Cause' column that match the symptoms derived by the symptom expert in the Twenty Questions game. At this time, ask in order of the most frequent causes.
- Action expert: Once the cause is identified, appropriate action will be taken. If dispatch for repairs is necessary, tell the customer that you will accept dispatch.
- Manual expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.

```
(Example)
User: 로봇이 동작을 못하고 멈칫거려.
AI: [Symptom expert] 고객님의 증상은 "멈춤 및 멈칫 거림"으로 분류됩니다.

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

#- Cause expert: Based on the symptoms derived by the symptom identification expert, using only causes in the ‘Cause’ column of the csv file, but use them as is and ask the customer one by one in a 20-question game format, starting with the most overlapping cause that causes the symptom among the causes in the 'Cause' column.
cause_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
cause_prompt.template = '''

You are Cause exprt for KT service robot, You are one of the experts in this team of four people.

- Symptom expert: When a customer describes their symptoms, refer to the 'Sentences in which the customer expressed their symptoms' column in the csv file and say the one most similar symptom based on the 'Symptoms' column.
- Cause expert: Ask customers one by one the causes in the 'Cause' column that match the symptoms derived by the symptom expert in the Twenty Questions game. At this time, ask in order of the most frequent causes.
- Action expert: Once the cause is identified, appropriate action will be taken. If dispatch for repairs is necessary, tell the customer that you will accept dispatch.
- Manual expert: Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.

```
(Example)
User: 고객의 원인에 대해 스무고개 형태로 파악해주세요.
AI: [Cause expert] 센서에 이물질이 묻어있지는 않나요?
User: 아니오.
AI: ...

```

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

#- Cause expert: Using only the causes in the 'Cause' column that match the symptoms derived by the symptom expert, ask the customer questions about the causes of the symptoms one by one using the Twenty Questions game method. At this time, you should ask questions in the order of most frequent, and if the customer says that all the reasons are not correct, tell them that you will connect them to customer service.
manual_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history', 'tool_manual']
manual_prompt.template = '''

You are Manual expert for KT service robot, You are one of the experts in this team of four people.
- Symptom expert: When a customer describes their symptoms, refer to the 'Sentences in which the customer expressed their symptoms' column in the csv file and say the one most similar symptom based on the 'Symptoms' column.
- Cause expert: Ask customers one by one the causes in the 'Cause' column that match the symptoms derived by the symptom expert in the Twenty Questions game. At this time, ask in order of the most frequent causes.
- Action expert: Once the cause is identified, appropriate action will be taken. If dispatch for repairs is necessary, tell the customer that you will accept dispatch.
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
    import re

    if 'Symptom' in general_res :
        ask_symptom = '{chat_history}를 분석하여, 고객의 증상을 최종 분류하여 고객에게 말해주고, {final_symthom}변수에 최종 분류된 증상을 넣어주세요.'
        symptom_agent_executor = AgentExecutor(agent=symptom_agent, tools=tool_symptom, verbose=True)
        response= symptom_agent_executor.invoke({"input": ask_symptom, "chat_history": chat_history})
        chat_history.extend(
            [
                AIMessage(content=ask_symptom),
                AIMessage(content=response["output"]),
            ]
        
        )
        
        print('\nAI: ',response["output"])
        
        #str_splits = re.findall('"([^"]*)"', response["output"])

        print('\n############################################ ',final_symthom)
        
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



    


