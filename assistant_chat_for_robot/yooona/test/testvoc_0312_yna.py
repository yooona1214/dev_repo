import os 
from chatbot_tools.issue_rag import * 
from chatbot_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, UnstructuredWordDocumentLoader
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
loader3 = UnstructuredWordDocumentLoader('./data/LG1세대[FnB2.0]_사용자매뉴얼_adobe.docx', mode='elements',strategy='fast')

data1 = loader1.load()
#data2 = loader2.load()
data3 = loader3.load()

issue_data = data3

# tool 선언
# rag_symptom = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
#                                        str2="Please search for and return the most relevant symptom name based on {user_input}.")

rag_symptom = create_vector_store_as_retriever_docs(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
                                       str2="Please search for and return the most relevant symptom name based on {user_input}.")


# Choose the LLM that will drive the agent
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

llm_model = llm_4_t
from langchain import hub 
from langchain import hub

tools = [rag_symptom]#

prompt = hub.pull("hwchase17/react-chat")
prompt1 = prompt
prompt1.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']

prompt1.template = '''

You are the general manager who handles inconveniences with KT service robots.

There are 2 main roles that you must play to the customer.
1. manual guide expert
2. 

Depending on what the customer says, an appropriate expert must be called to provide the manaul information or guidance on the cause and measures to be taken.
If the customer makes a comment that is unrelated to the symptoms or cause, respond appropriately and encourage them to focus on the conversation again.

There are a total of 4 experts you can call.
- Manual Guide Expert - When the customer asks you the information in the robot manual, you should answer using {tools}. You must answer based on the manual.
- Symptom identification expert - When the customer tells us their symptoms, we create one summarized word that expresses the symptom.
- Cause identification expert - Based on the symptoms derived by the symptom identification expert, appropriate causes are searched, and these causes are questioned one by one by the customer in a 20-game format.
- Action Guide Expert - Once the cause is identified, appropriate action will be taken.


Once you decide which expert to call, indicate that expert at the beginning of your answer sentence.
```
(Example)
User: My robot can't start and stops.
AI: [Symptom identification expert] The customer's symptom is, "My robot can't start and stops." It is said.
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



#print('P1',prompt1)



from langchain.agents import AgentExecutor, create_openai_functions_agent


chat_history = []



general_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)
symptom_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)
cause_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)
action_agent = create_openai_functions_agent_with_history(llm_model, tools, prompt1)


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
    
    print('\nAI: ',response["output"])
    
    if ('증상 식별 전문가' or 'Symptom identification expert ') in response["output"] :
        ask_cause = '그럼 내 원인은 무엇일까요?'
        symptom_agent_executor = AgentExecutor(agent=symptom_agent, tools=tools, verbose=True)
        response= general_agent_executor.invoke({"input": ask_cause, "chat_history": chat_history})
        chat_history.extend(
            [
                HumanMessage(content=ask_cause),
                AIMessage(content=response["output"]),
            ]
        )
        
    else:
        pass
        
    
    #print('\n\n\n',chat_history)
    





    


