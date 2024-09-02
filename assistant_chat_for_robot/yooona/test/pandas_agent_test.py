import pandas as pd

# csv 파일을 데이터프레임으로 로드
df = pd.read_csv('data/titanic.csv')
df.head()

from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType


# 에이전트 생성
agent = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0, 
               model='gpt-4-0613'),        # 모델 정의
    df,                                    # 데이터프레임
    verbose=True,                          # 추론과정 출력
    agent_type=AgentType.OPENAI_FUNCTIONS, # AgentType.ZERO_SHOT_REACT_DESCRIPTION
)