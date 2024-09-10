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

llm_google = llm_4_t
llm_goal_builder = llm_4_o
llm_reply_question = llm_4_t
llm_summary = llm_4_t

# path
csv_path2 = pkg_resources.files("robot_info").joinpath("gallery_artwork_des.csv")



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
        self.base_goal_json_path = goal_json_path
        
        # 기본 로봇 셋팅
        self.chat_history = []
        self.poi_list = []
        self.new_service = False
        self.robot_id = None
        self.session_id = None
        self.goal_generated = None
        self.current_agent = "goal_chat_agent" # 맨처음엔 goal_chat한테 가게 설정해야함
        self.ro_x = None
        self.ro_y = None
        self.goal_json = None
        
        # 체인버전
        self.goal_builder_chain = (
            goal_builder_prompt | llm_goal_builder | StrOutputParser()
        )

        # Agent 1: 대화 및 csv를 통한 list 생성, tool 사용 에이전트 버전
        
        rag_robot_info2 = create_vector_store_as_retriever2(
            csv_path=csv_path2,
            str1="KT_Docent_Robot_Gallery_Artwork_Information",
            str2="This is a data containing poi, name, artist and description for the artworks.",
        )
        
        tool_robot_info2 = [rag_robot_info2]
        
        tool_robot_info = tool_robot_info2

        goal_builder_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_builder_prompt
        )
        self.goal_builder_executor = AgentExecutor(
            agent=goal_builder_agent, tools=tool_robot_info, verbose=True
        )
        
        # Agent2: 골 제이슨 생성 에이전트
        rag_robot_info_for_json = create_vector_store_as_retriever2(
            csv_path=csv_path2,
            str1="KT_Docent_Robot_Gallery_Artwork_Information",
            str2="This is a data containing poi, name, artist and description for the artworks.",
        )
        
        tool_robot_info_for_json = [rag_robot_info_for_json]
        
        goal_json_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info_for_json, goal_json_prompt
        )
        self.goal_json_executor = AgentExecutor(
            agent=goal_json_agent, tools=tool_robot_info_for_json, verbose=True
        )
        
        # Agent 1: 채팅 에이전트 정의
        goal_chat_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_chat_prompt
        )
        self.goal_chat_executor = AgentExecutor(
            agent=goal_chat_agent, tools=tool_robot_info, verbose=True
        )

        # Agent 2: POI 리스트 생성 에이전트 정의
        generate_poi_list_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, generate_poi_list_prompt
        )
        self.generate_poi_list_executor = AgentExecutor(
            agent=generate_poi_list_agent, tools=tool_robot_info, verbose=True
        )

        # Agent 3: 목표 완료 확인 에이전트 정의
        goal_done_check_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_done_check_prompt
        )
        self.goal_done_check_executor = AgentExecutor(
            agent=goal_done_check_agent, tools=tool_robot_info, verbose=True
        )

        # Agent 4: 요약 에이전트 정의
        summary_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_summary_prompt
        )
        self.summary_executor = AgentExecutor(
            agent=summary_agent, tools=tool_robot_info, verbose=True
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
        
        # 불필요한 ```json 제거
        cleaned_json_data = goal_data.strip('```json').strip('```').strip()

        # JSON 문자열을 Python 딕셔너리로 변환
        try:
            parsed_data = json.loads(cleaned_json_data)

            # JSON 데이터를 파일에 저장
            with open(goal_json_path, "w", encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=4, ensure_ascii=False)  # JSON 데이터를 파일로 저장
            print(f"JSON 데이터가 '{goal_json_path}' 파일로 저장되었습니다.")
        
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")

    def _update_goal_json_with_user_input(self, poi_list, goal_data):
        """LLM을 사용하여 사용자의 입력을 해석하고 goal.json을 업데이트합니다."""
        prompt = f"Poi_list: {poi_list}\nCurrent goal data:\n{json.dumps(goal_data, indent=4)}\nBased on the poi list, update the goal data accordingly."
        response = self.goal_json_executor.invoke(
            {"input": prompt, "chat_history": self.chat_history}
        )
        updated_goal_data = response['output']
        return updated_goal_data


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
        
    def check_new_service(self, robot_id):
        "맨 처음 발화가 들어온 시점으로 세션 id 자체 생성"
        if not self.new_service:
            self.session_id = self.db_manager.get_session_id()
            self.new_service = True
            self.robot_id = robot_id
        
        return self.session_id

    
    def respond_goal_chat_agent(self, user_input, session_id):
        """채팅 에이전트 - 사용자 입력 처리"""
        response = self.goal_chat_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })

        # 불필요한 ```json 제거 및 JSON 디코딩
        respond_goal_chat = response["output"]
        '''
        output_data_cleaned = output_data.replace("```json", "").replace("```", "").strip()

        try:
            parsed_output = json.loads(output_data_cleaned)
            respond_goal_chat = parsed_output("respond_goal_chat")
            print(f"**Respond Goal Chat:", respond_goal_chat)

        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류1: {e}")
            respond_goal_chat = "Chat response not available."

        # 채팅 결과 반환
        '''
        return respond_goal_chat
    
    def respond_generate_poi_list_agent(self, robot_x, robot_y, chat_history):
        """POI 리스트 생성 에이전트 - POI 이름, BGM 타입, LED 색상 및 제어 정보 포함"""
        response = self.generate_poi_list_executor.invoke({
            "robot_x": robot_x,
            "robot_y": robot_y,
            "chat_history": chat_history
        })
        
        print("################################", response)

        # 불필요한 ```json 제거 및 JSON 디코딩
        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()
        
        poi_list = output_data_cleaned

        return poi_list

    def respond_goal_done_check_agent(self, poi_list, chat_history):
        """목표 완료 확인 에이전트"""
        response = self.goal_done_check_executor.invoke({
            "poi_list": poi_list,
            "chat_history":chat_history
        })

        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()

        try:
            parsed_output = json.loads(output_data_cleaned)
            goal_done = parsed_output['goal_done']

        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류3: {e}")
            goal_done = False

        return goal_done

    def respond_summary_agent(self, poi_list):
        """요약 에이전트 - 최종 요약 응답 생성"""
        response = self.summary_executor.invoke({
            "poi_list": poi_list,
            "chat_history": self.chat_history
        })

        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()

        try:
            parsed_output = json.loads(output_data_cleaned)
            respond_goal_chat = parsed_output.get("respond_goal_chat", "")
            goal_generated = parsed_output["goal_generated"]

            # 값 출력
            print("***Goal Generated:", goal_generated)
            print(f"Summary Output: {respond_goal_chat}")

        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류4: {e}")
            respond_goal_chat = "Summary not available."

        return respond_goal_chat, goal_generated
        
    def respond_goal_json_agent(self, poi_list, session_id):
        
        # 세션 별 goal.json 유무 확인 및 생성
        self._copy_base_goal_json(session_id)
        goal_data = self.load_goal_json(session_id)
        print("========================")
        print("Initial_goal: ", goal_data)

        # LLM을 사용하여 사용자의 발화를 해석하고 goal.json 업데이트
        goal_data = self._update_goal_json_with_user_input(poi_list, goal_data)

        print("========================")
        print("Current_goal: ", goal_data)
                
        # 업데이트한 goal.json 저장
        self.save_goal_json(session_id, goal_data)
        
        return goal_data
    
    def respond_goal_verify_agent(self, user_input):    
        ## 프롬프트 수정해서 에이전트 만들어야 함##
        
        return 
    
    def get_poi_list(self):
        return self.poi_list
        
    def route(self, user_input, robot_x, robot_y, session_id):
        # 챗 히스토리 로드
        self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  

        # 로봇 x,y좌표 초기화
        self.ro_x = robot_x
        self.ro_y = robot_y
        
        goal_done = False  # 목표 완료 여부를 추적
        goal_generated = False  # goal_generated 플래그 추가
        
        # 특정 조건에 따라 하위 에이전트 선택 및 실행
        # Agent1. goal_chat_agent = input: 사용자 발화 / output: csv파일을 참조해서 가야할 목적지 list + 이 list가 맞는지 대답생성
        # Agent2. goal_json_agent = input: Agent1의 out인 list / output: goal.json
        # Agent3. goal_verify_agent = input: 챗 히스토리 / output: 알겠습니다 대답생성 or 다시 서비스를 생성하겠습니다 후 Agent1 라우팅 
        # Agent4
        # Agent5
        # Agent6
        # self.goal_json 
        
        # Agent1 실행
        '''
        if self.current_agent == "goal_chat_agent":
            # Step 1: Agent1 실행 - 사용자 대화 처리 및 POI 리스트 생성
            poi_list, respond_goal_chat, goal_generated = self.respond_goal_chat_agent(user_input, self.ro_x, self.ro_y, session_id)
            self.poi_list = poi_list  # 다음 에이전트 호출 시 사용하기 위해 저장     
            
            if not goal_generated: # goal이 아직 완성되지 않거나, 일반 대화 대답일 때 
                return self.current_agent, respond_goal_chat
        '''

        while not goal_generated:
            # 1. 채팅 에이전트 실행
            if self.current_agent == "goal_chat_agent":
                respond_goal_chat = self.respond_goal_chat_agent(user_input, session_id)

                # 챗 히스토리 저장
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, respond_goal_chat, self.current_agent)
                
                # 채팅 응답을 반환하고 다음 에이전트로 넘어감
                self.current_agent = "generate_poi_list_agent"
            
            # 2. POI 리스트 생성 에이전트 실행
            if self.current_agent == "generate_poi_list_agent":
                
                # 챗 히스토리 다시 로드
                self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                self.poi_list = self.respond_generate_poi_list_agent(self.ro_x, self.ro_y, self.chat_history)
                print(f"POI List: {self.poi_list}")

                # 목표 완료 확인 에이전트로 넘어감
                self.current_agent = "goal_done_check_agent"

            # 3. 목표 완료 확인 에이전트 실행
            if self.current_agent == "goal_done_check_agent":
                # 챗 히스토리 다시 로드
                self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                goal_done = self.respond_goal_done_check_agent(self.poi_list, self.chat_history)
                print("========================================")

                if goal_done:
                    # 목표가 완료되었으면 Summary 에이전트로 이동
                    self.current_agent = "summary_agent"
                    print("GOAL DONE: TRUE")
                    
                else:
                    # 목표가 완료되지 않았으면 해당 기록 저장하고 다시 채팅 에이전트로 돌아감
                    # 에이전트 응답 결과 저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    
                    # 채팅에이전트로 라우팅
                    self.current_agent = "goal_chat_agent"
                    print("GOAL DONE: FALSE")
                    return self.current_agent , respond_goal_chat  # 서버로 채팅 응답 전송 후 루프 계속
            
            # 4. Summary 에이전트 실행 (목표 완료 후)
            if self.current_agent == "summary_agent":
                respond_goal_chat, goal_generated = self.respond_summary_agent(self.poi_list)
                print(f"Summary Output: {respond_goal_chat}")

                if not goal_generated:
                    # 목표가 완성되지 않았으면 다시 채팅 에이전트로 돌아감
                    self.current_agent = "goal_chat_agent"
                    return respond_goal_chat  # 루프 계속 진행
                
                # goal_generated가 True면 루프 종료
                respond_goal_chat = "안내를 시작하겠습니다."
                print("Goal Generated! Exiting loop.")
                return respond_goal_chat
        
        # Step 2: goal이 완성 되면, Agent2 실행
        goal_json = self.respond_goal_json_agent(self.poi_list, session_id)
            
        # Step 3: Agent3 실행 - 최종 서비스 실행 여부 질문
        final_response = self.respond_goal_verify_agent(goal_json)
        self.current_agent = "goal_verify_agent"
            
        return self.current_agent, final_response



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
