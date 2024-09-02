"""
ROLE RMQ 메세지 수신 역할 및 콜백으로 llm agent 통신 

(default 기능) llm agent 기본 셋팅 로드 - llm_agent.load_all()


그다음 기능
1. user id 판단

2. user id 별 llm agent 생성

3. 각 id 별 agent로 바로 메세지 전송 - callback_agent
"""

import pika
from llm_agent import LLMagent

# RabbitMQ 연동 위한 채널 큐 설정
HOST_NAME = "localhost"
QUEUE_NAME = "Chat"

# LLM AGENT 기본 설정 로드
llm_agent = LLMagent()
llm_agent.load_all()

# 연결 세팅
connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)
channel.basic_consume(
    queue=QUEUE_NAME, on_message_callback=llm_agent.identify_user, auto_ack=True
)
try:
    print("Waiting for messages.")
    channel.start_consuming()

except KeyboardInterrupt:
    print("Ctrl+C is Pressed.")
