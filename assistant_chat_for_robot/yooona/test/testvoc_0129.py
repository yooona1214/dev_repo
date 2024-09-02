from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma

import openai
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.chat_models import ChatOpenAI
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent, create_openai_functions_agent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor

from langchain_community.tools.convert_to_openai import format_tool_to_openai_function

import re

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain



#dotenv.load_dotenv()

OPENAI_API_KEY='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'

def main():
    print("필요한 파일을 불러오는중...")
    loader1 = CSVLoader('./data/주행관련VOC테스트_입력_이슈.csv')
    # loader2 = CSVLoader('./data/주행관련VOC테스트_이슈_원인.csv')

    llm = ChatOpenAI(temperature=0,
                        model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
    
    data1 = loader1.load()
    #data2 = loader2.load()

    issue_data1 = data1
    #issue_data2 = data2

    def create_vector_store_as_retriever(data, str1, str2):

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        docs = text_splitter.split_documents(data)


        embedding=OpenAIEmbeddings(openai_api_key =OPENAI_API_KEY)
        vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

        retriever = vectorstore.as_retriever()
        
        tool = create_retriever_tool(
            retriever,
            str1,
            str2,
        )
        
        return tool
    
    
    tool = create_vector_store_as_retriever(data= issue_data1, str1="KT_Robot_Customer_Issue_Guide", str2="적합한 이슈분류를 말해주세요.")
    tools = [tool]
    memory = ConversationBufferMemory(memory_key="chat_history")

    

    

    
    init_template = """                
    
                
    
                사용자 입력을 기반으로 해당되는 이슈분류를 찾아서 답할 것
                되묻지 말고, 한번에 답을 찾아서 말해라. 답은 "" 콜론 안에 넣어서 말해라.
                
                고객님의 이슈는 "이슈분류"에 해당하는 것 같습니다.원인을 파악해드릴게요. 라는 형식을 지켜서 대답할 것
                
                {chat_history}
                Human: {human_input}
                AI:
                
                """
                
 
         
    
    system_message = SystemMessage(
        content=(
                '''
                사용자 입력을 기반으로 해당되는 이슈분류를 찾아서 답할 것
                되묻지 말고, 한번에 답을 찾아서 말해라. 답은 "" 콜론 안에 넣어서 말해라.
                
                고객님의 이슈는 "이슈분류"에 해당하는 것 같습니다.원인을 파악해드릴게요. 라는 형식을 지켜서 대답할 것
                
                
                '''
        )
    )
    
    agent_prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
    )

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=agent_prompt)
        



    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
    )

    user_ = input('=======================\n안녕하세요! KT 서비스로봇 에이전트입니다. \n어떤 문제가 있으신가요?:')
    result = agent_executor({"input": user_})

    print('\nAI:',result['output'])


    
    #print('프롬프트:',prompt)
    
    
    prompt = PromptTemplate(
    template=init_template,  input_variables=["chat_history", "human_input"]
    )   
    
    llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
    )
    

    user_input = input('대화를 입력하세요:')
    res1 = llm_chain.predict(human_input=user_input) 
    memory.chat_memory.add_ai_message(res1)
    print("\nAI:",res1)
    
    #print(memory)
    
    # while(True):
        
    #     user_input = input('\n대답을 입력하세요.:')
    #     memory.chat_memory.add_user_message(user_input)

    #     res = test_llm.invoke(user_input)
    #     print("\nAI:",res)  
    #     memory.chat_memory.add_ai_message(res)
        
    #     print('\n\nprompt:',system_message.content)
      
        


if __name__ == '__main__':
    main()
    