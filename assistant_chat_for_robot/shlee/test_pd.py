import os
import pandas as pd


# csv 파일을 데이터프레임으로 로드
df = pd.read_csv('assistant_chat_for_robot/shlee/data/주행관련VOC테스트_이슈-원인.csv')
print(df)


from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType

os.environ['OPENAI_API_KEY'] = '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'

# 에이전트 생성
agent = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0),        # 모델 정의
    df,                                    # 데이터프레임
    verbose=True,                          # 추론과정 출력
    agent_type=AgentType.OPENAI_FUNCTIONS, # AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

agent.invoke('')
