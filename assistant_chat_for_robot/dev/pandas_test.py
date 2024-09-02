import os
import pandas as pd
from langchain.agents import load_tools
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI

# openai 설정
OPENAI_API_KEY='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'
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# df
df = pd.read_csv('./data/LG0313.csv')
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)

llm_model = llm_4_t
# 에이전트
agent = create_pandas_dataframe_agent(llm=llm_model,
                                      df=df,
                                      verbose=True,
                                      prefix='Please list the causes appropriate for your symptoms in order of frequency. Please answer all questions concisely and in Korean.',
                                    
                                      )

from langchain_core.messages import AIMessage, HumanMessage

chat_history = []
while True :
    # 프롬프트
    user_input = input('입력:')

    
    res = agent.run(user_input)
    chat_history.extend(
        [
            HumanMessage(content=user_input),
            AIMessage(content=res)
        ]
    )
    print('AI:', res)
    
    print('history:', chat_history)
