# API KEY를 환경변수로 관리하기 위한 설정 파일
import os
os.environ["OPENAI_API_KEY"] = (
    "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"  # set with yours
)
OPENAI_API_KEY = "sk-proj-4ebppYSwaJFfWxESdsOcT3BlbkFJ3RMHQxQlSkuBZ07ZX2Xe"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3b0b4639413547b1992222420ad58d30"  # Update to your API key

#from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage



client = ChatOpenAI(model="gpt-4-vision-preview", api_key=OPENAI_API_KEY)


system_message = SystemMessage(
    content=[
        """
        로봇 인지에 사용할 Knowledge Graph를 만들기 위해, 이 그림을 한글로 상세하게 설명해줘
        """
    ]
)

image_url = "https://aws-tiqets-cdn.imgix.net/images/content/8ea928dc74d94b29b092a9f07fe0c563.jpeg?auto=format&fit=crop&h=800&ixlib=python-3.2.1&q=70&w=800&s=38ed0df8c32985449ee5af6d56e23420"
vision_message = HumanMessage(
    content=[
        {"type": "text", "text": "설명해주세요."},
        {
            "type": "image_url",
            "image_url": {
                "url": image_url,
                "detail": "auto",
            },
        },
    ]
)
output = client.invoke([system_message, vision_message])


print(output)