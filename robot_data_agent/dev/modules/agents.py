import json
import redis
from datetime import datetime

# Redis 클라이언트 생성
redis_client = redis.Redis(host="localhost", port=6379, db=1)


class GeneralChatAgent:
    def respond(self, user_input):
        # General Chat 응답 생성 로직
        # 단순 질의 응대
        return "This is a general chat response."


class DataRetrieveAgent:
    def respond(self, user_input):
        # Data 검색 에이전트
        # tool1 : Document RAG (PDF, CSV)
        # tool2 : Storage RAG
        # tool3 : SQL
        # tool4 : Cypherquery
        return "This is a general chat response."


class DataReasoningAgent:
    def respond(self, user_input):
        # Data 추론 에이전트
        # tool1 : Cypher query
        return "This is a general chat response."


class VerificationAgent:
    def respond(self, user_input, session_id):
        # Task 검증 로직
        plan = json.loads(redis_client.get(f"{session_id}_plan"))
        return f"Task verified: {plan['task']}"


# multi agents 선언
multi_agents = {
    "general": GeneralChatAgent(),
    "robot_data": DataRetrieveAgent(),
}
