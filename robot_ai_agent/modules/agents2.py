import json
import redis
import os
import shutil
import importlib.resources as pkg_resources
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools.google_serper.tool import GoogleSerperRun
from langchain.agents import Tool, AgentExecutor
from langchain.chains import *
from langchain_core.output_parsers import StrOutputParser

from modules.create_react_agent_w_history import (
    create_openai_functions_agent_with_history,
)
from modules.prompts import *
from modules.db_manager import *
from modules.tools import *

# Redis 클라이언트 생성
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# 환경변수설정
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Robot AI Agent"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = (
    "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"  # yooona
)
os.environ["GPT_MODEL"] = "gpt-3.5-turbo"

# LLM model
llm_4 = ChatOpenAI(model="gpt-4-0613")
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
llm_4_o = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
llm_4_o_m = ChatOpenAI(model="gpt-4o-mini")
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125")

llm_google = llm_4_o
llm_goal_builder = llm_4_o
llm_reply_question = llm_4_o
llm_summary = llm_4_o

# path
csv_file_path = pkg_resources.files("robot_info").joinpath("gallery_artwork_copy.csv")


class GeneralChatAgent:
    def __init__(self, db_manager):
        # General Chat 응답 생성 로직 (구글 검색, RAG 등)
        # tool1 : google serper
        # tool2 : RAG
        self.tool_google = [
            GoogleSerperRun(
                api_wrapper=GoogleSerperAPIWrapper(
                    k=5, gl="kr", hl="kr", serper_api_key=SERPER_API_KEY
                )
            )
        ]
        self.google_agent = create_openai_functions_agent_with_history(
            llm_google, self.tool_google, google_prompt
        )
        self.google_executor = AgentExecutor(
            agent=self.google_agent, tools=self.tool_google, verbose=True
        )

        self.db_manager = db_manager

    def respond(self, user_input, session_id):
        chat_history = self.db_manager.get_conversation_history(
            session_id, "general_chat"
        )
        response = self.google_executor.invoke(
            {"input": user_input, "chat_history": chat_history}
        )
        return response


class GoalInferenceAgent:
    def __init__(self, db_manager, goal_json_path):
        self.db_manager = db_manager
        self.chat_history = None
        self.base_goal_json_path = goal_json_path

        # 체인버전
        self.goal_builder_chain = (
            goal_builder_prompt | llm_goal_builder | StrOutputParser()
        )

        # tool 사용 에이전트 버전
        #robot_info_data = CSVLoader(csv_path).load()
        rag_robot_info = create_vector_store_as_retriever2(
            csv_path=csv_file_path,
            str1="KT_Docent_Robot_Gallery_Artwork_Information",
            str2="This is a data containing poi, name, artist and description for the artworks.",
        )
        tool_robot_info = [rag_robot_info]

        goal_builder_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_builder_prompt
        )
        self.goal_builder_executor = AgentExecutor(
            agent=goal_builder_agent, tools=tool_robot_info, verbose=True
        )

        # self.reply_question_agent = create_openai_functions_agent_with_history(llm_reply_question, [], reply_question_prompt)
        # self.reply_question_executor = AgentExecutor(agent=self.reply_question_agent, tools=[], verbose=True)

        # self.summary_agent = create_openai_functions_agent_with_history(llm_summary, [], summary_prompt)
        # self.summary_executor = AgentExecutor(agent=self.summary_agent, tools=[], verbose=True)

    def _get_goal_json_path(self, session_id):
        """세션 ID에 기반한 goal.json 파일 경로를 생성"""
        # 위치는 /data/아래
        return f"data/goal_{session_id}.json"

    def _copy_base_goal_json(self, session_id):
        """기본 goal.json 파일을 세션별로 복사하여 새 파일을 처음에만 생성"""
        new_goal_json_path = self._get_goal_json_path(session_id)
        if not os.path.exists(new_goal_json_path):
            shutil.copy(self.base_goal_json_path, new_goal_json_path)
        return new_goal_json_path

    def load_goal_json(self, session_id):
        """세션별 goal.json 파일을 로드"""
        goal_json_path = self._get_goal_json_path(session_id)
        if os.path.exists(goal_json_path):
            with open(goal_json_path, "r") as f:
                return json.load(f)
        else:
            raise FileNotFoundError(
                f"Goal JSON file for session {session_id} not found."
            )

    def save_goal_json(self, session_id, goal_data):
        """세션별 goal.json 파일에 현재 상태를 저장"""
        goal_json_path = self._get_goal_json_path(session_id)
        with open(goal_json_path, "w") as f:
            json.dump(goal_data, f, indent=4)

    def _update_goal_json_with_user_input(self, user_input, goal_data):
        """LLM을 사용하여 사용자의 입력을 해석하고 goal.json을 업데이트합니다."""
        prompt = f"User input: {user_input}\nCurrent goal data:\n{json.dumps(goal_data, indent=4)}\nBased on the user input, update the goal data accordingly."
        response = self.goal_builder_executor.invoke(
            {"input": prompt, "chat_history": self.chat_history}
        )
        print("RESPONSE: \n", response['output'])
        # updated_goal_data = json.loads(response['output'])
        updated_goal_data = response['output']
        return updated_goal_data

    def _check_incomplete_fields(self, goal_data):
        """빈 필드를 확인하고 빈 필드가 있으면 True를 반환"""
        incomplete_fields = [
            key for key, value in goal_data["goal"].items() if value is None
        ]
        return bool(incomplete_fields)

    def _generate_question(self, goal_data):
        """JSON의 빈 값을 채우기 위해 LLM에 전달할 프롬프트를 생성"""
        prompt = "I have the following JSON data for a goal. I need to fill in the missing values. Here is the current data:\n"
        prompt += json.dumps(goal_data, indent=4)
        prompt += "\nPlease generate questions to fill in the missing information."
        ####
        response = self.goal_builder_chain.invoke(
            {"input": prompt, "chat_history": self.chat_history}
        )
        return response

    def _generate_summary(self, goal_data):
        """모든 값이 채워졌을 때, 서비스를 요약하는 프롬프트를 생성"""
        prompt = f"Here is the completed goal data:\n{json.dumps(goal_data, indent=4)}\nPlease provide a summary of this goal and confirm if it's correct."
        ###
        response = self.goal_builder_chain.invoke(
            {"input": prompt, "chat_history": self.chat_history}
        )
        return response

    def _cache_turn(
        self, session_id, agent_id, user_input, goal_data, additional_question=None
    ):
        """캐시 메모리에 대화 저장"""
        turn = {
            "user_input": user_input,
            "goal_data": goal_data,
            "additional_question": additional_question,
            "timestamp": str(datetime.now()),
        }
        self.db_manager.redis_client.rpush(session_id, json.dumps(turn))

    def respond(self, user_input, session_id):
        # Goal 추론 로직
        # 챗 히스토리 로드
        self.chat_history = self.db_manager.get_conversation_history(
            session_id, "robot_control"
        )  # robot_id도 세션 아이디에 추가

        # 세션 별 goal.json 유무 확인 및 생성
        self._copy_base_goal_json(session_id)
        goal_data = self.load_goal_json(session_id)
        print("========================")
        print("Initial_goal: ", goal_data)

        # LLM을 사용하여 사용자의 발화를 해석하고 goal.json 업데이트
        goal_data = self._update_goal_json_with_user_input(user_input, goal_data)
        print("========================")
        print("Current_goal: ", goal_data)

        # 테스트용
        if input("Y/N: ") == "Y":
            self.save_goal_json(session_id, goal_data)

            # 빈 필드 확인
            if self._check_incomplete_fields(goal_data):
                # 빈 값이 있으면, 추가 정보를 요청하는 질문 생성
                response = self._generate_question(goal_data)
                question = response["output"]
                return question


            else:
                # 모든 값이 채워졌으면 요약 발화 생성
                summary_response = self._generate_summary(goal_data)
                summary_text = summary_response["output"]

                # 요약 발화를 사용자에게 전달 (여기서는 출력으로 가정)
                print(f"Summary for the user: {summary_text}")

                # 서비스 요약 발화의 긍정을 확인하여 goal_generated를 True로 업데이트
                self.save_goal_json(session_id, goal_data)
                return "Goal generated and updated."


class GoalVerificationAgent:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def respond(self, user_input, session_id):
        # Goal 검증 로직
        goal = json.loads(self.db_manager.redis_client.get(f"{session_id}_goal"))
        return f"Goal verified: {goal['goal']}"


class TaskPlanningAgent:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def respond(self, user_input, session_id):
        # Task 계획 로직
        plan = {"task": "planned_task", "timestamp": str(datetime.now())}
        self.db_manager.redis_client.set(f"{session_id}_plan", json.dumps(plan))
        return "Task planned."


class TaskVerificationAgent:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def respond(self, user_input, session_id):
        # Task 검증 로직
        plan = json.loads(self.db_manager.redis_client.get(f"{session_id}_plan"))
        return f"Task verified: {plan['task']}"


class RobotControlAgent:
    def __init__(self, db_manager, goal_json_path):
        self.agents = {
            "goal_inference": GoalInferenceAgent(db_manager, goal_json_path),
            "goal_verification": GoalVerificationAgent(db_manager),
            "task_planning": TaskPlanningAgent(db_manager),
            "task_verification": TaskVerificationAgent(db_manager),
        }
        self.state = None
        self.db_manager = db_manager

    def route(self, user_input, session_id):
        # # 특정 조건에 따라 하위 에이전트 선택 및 실행
        # if "infer goal" in user_input:
        #     self.state = "goal_inference"
        # elif "verify goal" in user_input:
        #     self.state = "goal_verification"
        # elif "plan task" in user_input:
        #     self.state = "task_planning"
        # elif "verify task" in user_input:
        #     self.state = "task_verification"
        # else:
        #     return "Unknown command."

        self.state = "goal_inference"

        return self.agents[self.state].respond(user_input, session_id)


# multi agents 선언
def get_multi_agents(db_manager, GOAL_JSON_PATH):
    return {
        "general_chat": GeneralChatAgent(db_manager),
        "robot_control": RobotControlAgent(db_manager, GOAL_JSON_PATH),
    }
