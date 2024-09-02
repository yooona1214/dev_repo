import os 
from chatbot_tools.issue_rag import create_vector_store_as_retriever, create_vector_store_as_retriever_w_mode
from chatbot_tools.create_react_agent_w_history import create_react_agent_w_history, create_openai_functions_agent_with_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader, UnstructuredWordDocumentLoader
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
loader1 = UnstructuredWordDocumentLoader('./data/LG2세대[FnB3.0]_사용자매뉴얼.docx', mode= 'elements')

data1 = loader1.load()
#data2 = loader2.load()
        #     loader = PyPDFLoader("LG2.pdf")


manual_data = data1
# tool 선언

# rag_manual = create_vector_store_as_retriever(data= manual_data, str1="LG_Robot_Manual_Guide", 
#                                        str2="Please search for and return the most relevant contents based on {user_input}.")

rag_manual = create_vector_store_as_retriever_w_mode(data= manual_data, str1="LG_Robot_Manual_Guide", 
                                       str2="Please search for and return the most relevant contents based on {user_input}.")


# Choose the LLM that will drive the agent
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

llm_model = llm_4_t
from langchain import hub 
from langchain import hub

tool_manual = [rag_manual]

#prompt1 = hub.pull("hwchase17/react-chat")

general_prompt = PromptTemplate(
    input_variables=[],
    template=''
)
general_prompt.input_variables= ['input', 'intermediate_steps', 'agent_scratchpad', 'chat_history']
general_prompt.template = '''

You are Manual expert: 
Respond appropriately when customers ask questions about specific usage of the robot or structural features of the robot hardware.
Please briefly summarize the retrieved data and explain it to the customer as simply as possible.

All response must be answered in korean.
Begin!

Previous conversation history:
{chat_history}


New input: {input}
{agent_scratchpad}
'''
# print(type(prompt1))
# print(prompt1)





#print('P1',prompt1)



from langchain.agents import AgentExecutor


chat_history = []


manual_agent = create_openai_functions_agent_with_history(llm_model, tool_manual, general_prompt)






while True:
    user_input = input('입력:')
    
    general_agent_executor = AgentExecutor(agent=manual_agent, tools=tool_manual, verbose=True)
    response= general_agent_executor.invoke({"input": user_input, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_input),
            AIMessage(content=response["output"]),
        ]
    )
    general_res = response["output"]

        
    print('\nAI: ',general_res)

    
    #print('\n\n\n',chat_history)
    





    


