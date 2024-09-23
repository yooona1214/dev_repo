import json
import redis
import os
import shutil
import importlib.resources as pkg_resources
import ast
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
    create_openai_functions_agent_with_history_query
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
#llm_4_o = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
llm_4_o = ChatOpenAI(model="gpt-4o-2024-08-06")
llm_4_o_m = ChatOpenAI(model="gpt-4o-mini")
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125")

llm_google = llm_4_t
llm_goal_builder = llm_4_o
llm_reply_question = llm_4_t
llm_summary = llm_4_t

# path
csv_path2 = pkg_resources.files("robot_info").joinpath("floor_description_240912.csv")



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
        self.current_agent = "intent_agent" # 맨처음엔 goal_chat한테 가게 설정해야함
        self.ro_x = None
        self.ro_y = None
        self.goal_json = None
        self.summary_flag = False
    
        
        # 체인버전
        self.goal_builder_chain = (
            goal_builder_prompt | llm_goal_builder | StrOutputParser()
        )

        # Agent 1: 대화 및 csv를 통한 list 생성, tool 사용 에이전트 버전
        
        rag_robot_info2 = create_vector_store_as_retriever2(
            csv_path=csv_path2,
            str1="KT_floor_Information_fot_Docent_Robot",
            str2="This is a data containing space or artwork name, position and description for space and artworks.",
        )

        # GraphTool을 생성하고 다른 도구들과 함께 에이전트에 통합
        #graph_tool = create_graph_tool()

        # 기존 리트리버 도구들과 함께 tool 리스트에 GraphTool 추가
        #tool_robot_info = [rag_robot_info2, graph_tool]
        
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
        
        # Agent 0: 일반과 작품설명 분류 에이전트 정의
        intent_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, intent_prompt
        )
        self.intent_executor = AgentExecutor(
            agent=intent_agent, tools=tool_robot_info, verbose=True
        )
        
        # Agent 1: 채팅 에이전트 정의
        goal_chat_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_chat_prompt
        )
        self.goal_chat_executor = AgentExecutor(
            agent=goal_chat_agent, tools=tool_robot_info, verbose=True
        )

        # Agent 2: POI 리스트 생성 에이전트 정의
        generate_poi_list_agent = create_openai_functions_agent_with_history_query(
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
        
        # Agent 3: 목표 완료 확인 에이전트 정의
        goal_validation_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_validation_prompt
        )
        self.goal_validation_executor = AgentExecutor(
            agent=goal_validation_agent, tools=tool_robot_info, verbose=True
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
    
    def restart_service(self):
        """세션 초기화"""
        self.chat_history = []
        self.poi_list = []
        self.new_service = False
        self.robot_id = None
        self.session_id = None
        self.goal_generated = None
        self.current_agent = "intent_agent" 
        self.ro_x = None
        self.ro_y = None
        self.goal_json = None
        
        
    def intent_agent(self, user_input, session_id):
        """채팅 에이전트 - 사용자 입력 처리"""
        response = self.intent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })

        # 불필요한 ```json 제거 및 JSON 디코딩
        intent = response["output"]
        
        return intent
    
    def respond_goal_chat_agent(self, user_input, session_id):
        """채팅 에이전트 - 사용자 입력 처리"""
        response = self.goal_chat_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })

        # 불필요한 ```json 제거 및 JSON 디코딩
        respond_goal_chat = response["output"]
        print("###respond_goal_chat_agent: ", respond_goal_chat)

        return respond_goal_chat
    
    def respond_generate_poi_list_agent(self, robot_x, robot_y, chat_history):
        """POI 리스트 생성 에이전트 - POI 이름, BGM 타입, LED 색상 및 제어 정보 포함"""
        response = self.generate_poi_list_executor.invoke({
            "robot_x": robot_x,
            "robot_y": robot_y,
            "chat_history": chat_history
        })
        

        # 불필요한 ```json 제거 및 JSON 디코딩
        output_data_cleaned = response['output']
        print("###respond_generate_poi_list_agent: ", output_data_cleaned)
        
        poi_list = output_data_cleaned

        return poi_list

    def respond_goal_done_check_agent(self, poi_list, chat_history):
        """목표 완료 확인 에이전트"""
        goal_done = False
        response = self.goal_done_check_executor.invoke({
            "poi_list": poi_list,
            "chat_history":chat_history
        })
        output_data_cleaned = response['output']
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^: ", output_data_cleaned)
        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()
        output_data_cleaned = json.loads(output_data_cleaned)
        output_data_cleaned = output_data_cleaned["goal_done"]
        

        try:
            print("###respond_goal_done_check_agent: ", output_data_cleaned)
            goal_done = output_data_cleaned

        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류3: {e}")

        return goal_done
    
    
    def response_goal_validation_agent(self, poi_list, chat_history):
        """목표 완료 확인 에이전트"""
        response = self.goal_validation_executor.invoke({
            "poi_list": poi_list,
            "chat_history":chat_history
            
        })

        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()
        print("###response_goal_validation_agent: ", output_data_cleaned)
        poi_list = output_data_cleaned

        return poi_list

    def respond_summary_agent(self,user_input, poi_list, chat_history):
        """요약 에이전트 - 최종 요약 응답 생성"""
        goal_generated = False
        response = self.summary_executor.invoke({
            "input": user_input,
            "poi_list": poi_list,
            "chat_history": chat_history
        })
        print("###respond_summary_agent: ", response)
        output_data_cleaned = ast.literal_eval(response["output"])


        try:
            respond_goal_chat = output_data_cleaned[0][1]
            goal_generated = output_data_cleaned[1][1]

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
        ### 여기서 바꿔주자
        self.poi_list = ast.literal_eval(self.poi_list)
        goal_json_poi_list = self.poi_list
        only_poi_list = [sublist[0] for sublist in list(self.poi_list)]
        print(goal_json_poi_list, only_poi_list)
        return goal_json_poi_list, only_poi_list
        
    def route(self, user_input, robot_x, robot_y, session_id):
        print("****************************************************")
        print("****************************************************")
        

        # 챗 히스토리 로드
        self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  

        # 로봇 x,y좌표 초기화
        self.ro_x = robot_x
        self.ro_y = robot_y
        
        # 라우팅값 초기화
        intent = 0
        goal_done = False  # 목표 완료 여부를 추적
        self.goal_generated_flag = False
        
        while self.current_agent != "summary_agent":
            # Agent1: 의도파악 에이전트 실행
            intent = self.intent_agent(user_input, session_id) #1:일반, 2:작품설명
            if intent == str(2):
                """작품설명이어서 로봇으로 바로 값 전송"""
                respond_goal_chat = "작품 설명 완료"
                
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id, time_stamp, user_input, respond_goal_chat, self.current_agent)
                
                print(f"의도2(미들웨어) : ", intent)
                print(f"respond_goal_chat : ", respond_goal_chat)
                return self.current_agent, respond_goal_chat, intent
            else:
                """골 추론 에이전트 돌릴 경우"""
                self.current_agent = "goal_chat_agent"
                print(f"의도1(우리) : ", intent)
            

            # 1. 채팅 에이전트 실행
            if self.current_agent == "goal_chat_agent":
                respond_goal_chat = self.respond_goal_chat_agent(user_input, session_id)
                # 챗 히스토리 저장
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, respond_goal_chat, self.current_agent)
                
                print("111111111111111111111111111111111111111111111111111111111111111111111")
                # 채팅 응답을 반환하고 다음 에이전트로 넘어감
                self.current_agent = "generate_poi_list_agent"
            
            # 2. POI 리스트 생성 에이전트 실행
            if self.current_agent == "generate_poi_list_agent":
                
                # 채팅 에이전트가 남긴 챗 히스토리 다시 로드
                self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                self.poi_list = self.respond_generate_poi_list_agent(self.ro_x, self.ro_y, self.chat_history)
                print("22222222222222222222222222222222222222222222222222222222222222222222222")
                # 목표 완료 확인 에이전트로 넘어감
                self.current_agent = "goal_done_check_agent"

            # 3. 목표 완료 확인 에이전트 실행
            if self.current_agent == "goal_done_check_agent":
                # poi 리스트 생성 에이전트가 남긴 챗 히스토리 다시 로드
                self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                goal_done = self.respond_goal_done_check_agent(self.poi_list, self.chat_history)

                print("33333333333333333333333333333333333333333333333333333333333")
 
                

                if goal_done:
                    # 목표가 완료되었으면 Summary 에이전트로 이동
                    self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                    self.poi_list = self.response_goal_validation_agent(self.poi_list, self.chat_history)                    
                    self.current_agent = "summary_agent"
                    print("GOAL DONE: TRUE")
                    print("44444444444444444444444444444444444444444444444444444444444444444444")
                    
                else:
                    # 목표가 완료되지 않았으면 해당 기록 저장하고 다시 채팅 에이전트로 돌아감
                    # 에이전트 응답 결과 저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    print("55555555555555555555555555555555555555555555555555555555555555")
                    
                    # 채팅에이전트로 라우팅
                    self.current_agent = "goal_chat_agent"
                    print("GOAL DONE: FALSE")
                    intent = 1
                    return self.current_agent , respond_goal_chat, intent  # 서버로 채팅 응답 전송 후 루프 계속

        # 4. Summary 에이전트 실행 (목표 완료 후)
        if self.current_agent == "summary_agent":
            self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)

            # 1단계: Summary 에이전트 실행 후 요약 질문 반환
            respond_goal_chat, goal_generated = self.respond_summary_agent(user_input, self.poi_list, self.chat_history)
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            
            if not self.summary_flag: # False 처음 서머리 에이전트가 탈 경우
                # 첫 번째 단계에서는 goal_generated를 아직 체크하지 않고 요약 질문을 사용자에게 보냄 (None)
                self.current_agent = "summary_agent"
                self.summary_flag = True
                print("@@@@@@@@@@@@써머리처음")
                
                #db저장
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                return self.current_agent, respond_goal_chat, intent

            else:
                if goal_generated == False:
                # goal_generated가 False면 다시 대화 에이전트로 돌아감
                    respond_goal_chat = "기존 계획을 초기화 하겠습니다. 안내받고 싶은신 장소를 다시 처음부터 말씀해주세요."
                    print("~~~~~~~~~~~~~~~써머리두번째 부정적 답변받은 상황")

                    self.current_agent = "goal_chat_agent"
                    self.summary_flag = False
                    #db저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    self.restart_service()
                    return self.current_agent, respond_goal_chat, intent  # intent = 1: 다시 채팅으로 돌아감


                else: # True
                    # goal_generated가 True면 안내를 시작하는 응답 반환
                    respond_goal_chat = "안내를 시작하겠습니다."
                    print("===============써머리두번째 긍정적 답변받은 상황")
                    self.current_agent = "END"
                    self.summary_flag = False
                    intent = 3
                    #db저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    return self.current_agent, respond_goal_chat, intent  # intent = 3: 안내 시작

import json
import redis
import os
import shutil
import importlib.resources as pkg_resources
import ast
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
    create_openai_functions_agent_with_history_query
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
csv_path2 = pkg_resources.files("robot_info").joinpath("floor_description_240912.csv")


class ReplanningAgent:
    _instances = {}
    
    def __init__(self, robot_id, db_manager, goal_json_path):
        """
        Replanning 에이전트 클래스 초기화
        """
        self.db_manager = db_manager
        self.base_goal_json_path = goal_json_path
        
        # 기본 로봇 셋팅
        self.chat_history = []
        self.poi_list = []
        self.new_service = False
        self.robot_id = robot_id
        self.session_id = None
        self.goal_generated = None
        self.current_agent = "intent_agent" # 맨처음엔 goal_chat한테 가게 설정해야함
        self.ro_x = None
        self.ro_y = None
        self.goal_json = None
        self.summary_flag = False
    
        
        # 체인버전
        self.goal_builder_chain = (
            goal_builder_prompt | llm_goal_builder | StrOutputParser()
        )

        # RAG
        rag_robot_info2 = create_vector_store_as_retriever2(
            csv_path=csv_path2,
            str1="KT_floor_Information_fot_Docent_Robot",
            str2="This is a data containing space or artwork name, position and description for space and artworks.",
        )
        
        tool_robot_info2 = [rag_robot_info2]
        tool_robot_info = tool_robot_info2

        
        # Agent 0: 일반과 작품설명 분류 에이전트 정의
        intent_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, intent_prompt
        )
        self.intent_executor = AgentExecutor(
            agent=intent_agent, tools=tool_robot_info, verbose=True
        )
        
        # Agent 1: 채팅 에이전트 정의
        replanning_chat_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, replanning_chat_prompt
        )
        self.replanning_chat_executor = AgentExecutor(
            agent=replanning_chat_agent, tools=tool_robot_info, verbose=True
        )

        # Agent 2: POI 리스트 생성 에이전트 정의
        replanning_generate_poi_list_agent = create_openai_functions_agent_with_history_query(
            llm_goal_builder, tool_robot_info, replanning_generate_poi_list_prompt
        )
        self.replanning_generate_poi_list_executor = AgentExecutor(
            agent=replanning_generate_poi_list_agent, tools=tool_robot_info, verbose=True
        )

        # Agent 3: 목표 완료 확인 에이전트 정의
        goal_done_check_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_done_check_prompt
        )
        self.goal_done_check_executor = AgentExecutor(
            agent=goal_done_check_agent, tools=tool_robot_info, verbose=True
        )
        
        # Agent 3: 목표 완료 확인 에이전트 정의
        goal_validation_agent = create_openai_functions_agent_with_history(
            llm_goal_builder, tool_robot_info, goal_validation_prompt
        )
        self.goal_validation_executor = AgentExecutor(
            agent=goal_validation_agent, tools=tool_robot_info, verbose=True
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
    
    @classmethod
    def get_instance(cls, robot_id, db_manager, goal_json_path):
        """
        주어진 robot_id에 대한 ReplanningAgent 인스턴스를 반환합니다.
        :param robot_id: 로봇의 ID
        :return: ReplanningAgent 인스턴스
        """
        if robot_id not in cls._instances:
            # 새로운 인스턴스 생성 후 딕셔너리에 저장
            cls._instances[robot_id] = ReplanningAgent(robot_id, db_manager, goal_json_path)
        return cls._instances[robot_id]


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
    
    def restart_service(self):
        """세션 초기화"""
        self.chat_history = []
        self.poi_list = []
        self.new_service = False
        self.robot_id = None
        self.session_id = None
        self.goal_generated = None
        self.current_agent = "intent_agent" 
        self.ro_x = None
        self.ro_y = None
        self.goal_json = None
        
        
    def intent_replanning_agent(self, user_input, session_id):
        """채팅 에이전트 - 사용자 입력 처리"""
        response = self.intent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })

        # 불필요한 ```json 제거 및 JSON 디코딩
        intent = response["output"]
        
        return intent
    
    def respond_replanning_chat_agent(self, user_input, previous_poi_list):
        """채팅 에이전트 - 사용자 입력 처리"""
        response = self.replanning_chat_executor.invoke({
            "input": user_input,
            "previous_poi_list" : previous_poi_list, 
            "chat_history": self.chat_history
        })

        # 불필요한 ```json 제거 및 JSON 디코딩
        respond_goal_chat = response["output"]
        print("###respond_replanning_chat_agent: ", respond_goal_chat)

        return respond_goal_chat
    
    def respond_replanning_generate_poi_list_agent(self, previous_poi_list, robot_x, robot_y, chat_history):
        """POI 리스트 생성 에이전트 - POI 이름, BGM 타입, LED 색상 및 제어 정보 포함"""
        response = self.replanning_generate_poi_list_executor.invoke({
            "previous_poi_list": previous_poi_list,
            "robot_x": robot_x,
            "robot_y": robot_y,
            "chat_history": chat_history
        })
        

        # 불필요한 ```json 제거 및 JSON 디코딩
        output_data_cleaned = response['output']
        print("###respond_replanning_generate_poi_list_agent: ", output_data_cleaned)
        
        poi_list = output_data_cleaned

        return poi_list

    def respond_goal_done_check_agent(self, poi_list, chat_history):
        """목표 완료 확인 에이전트"""
        goal_done = False
        response = self.goal_done_check_executor.invoke({
            "poi_list": poi_list,
            "chat_history":chat_history
        })
        output_data_cleaned = response['output']
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^: ", output_data_cleaned)
        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()
        output_data_cleaned = json.loads(output_data_cleaned)
        output_data_cleaned = output_data_cleaned["goal_done"]
        

        try:
            print("###respond_goal_done_check_agent: ", output_data_cleaned)
            goal_done = output_data_cleaned

        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류3: {e}")

        return goal_done
    
    
    def response_goal_validation_agent(self, poi_list, chat_history):
        """목표 완료 확인 에이전트"""
        response = self.goal_validation_executor.invoke({
            "poi_list": poi_list,
            "chat_history":chat_history
            
        })

        output_data_cleaned = response['output'].replace("```json", "").replace("```", "").strip()
        print("###response_goal_validation_agent: ", output_data_cleaned)
        poi_list = output_data_cleaned

        return poi_list

    def respond_summary_agent(self,user_input, poi_list, chat_history):
        """요약 에이전트 - 최종 요약 응답 생성"""
        goal_generated = False
        response = self.summary_executor.invoke({
            "input": user_input,
            "poi_list": poi_list,
            "chat_history": chat_history
        })
        print("###respond_summary_agent: ", response)
        output_data_cleaned = ast.literal_eval(response["output"])


        try:
            respond_goal_chat = output_data_cleaned[0][1]
            goal_generated = output_data_cleaned[1][1]

        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류4: {e}")
            respond_goal_chat = "Summary not available."

        return respond_goal_chat, goal_generated
        
    
    def respond_goal_verify_agent(self, user_input):    
        ## 프롬프트 수정해서 에이전트 만들어야 함##
        
        return 
    
    
    def get_poi_list(self):
        ### 여기서 바꿔주자
        self.poi_list = ast.literal_eval(self.poi_list)
        goal_json_poi_list = self.poi_list
        only_poi_list = [sublist[0] for sublist in list(self.poi_list)]
        print(goal_json_poi_list, only_poi_list)
        return goal_json_poi_list, only_poi_list
        
    def route(self, user_input, previous_poi_list, robot_x, robot_y, session_id):
        print("****************REPLANNING STARTED*************************")
        print("***********************************************************")
        

        # 챗 히스토리 로드
        self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  

        # 로봇 x,y좌표 초기화
        self.ro_x = robot_x
        self.ro_y = robot_y
        
        # 라우팅값 초기화
        intent = 0
        goal_done = False  # 목표 완료 여부를 추적
        self.goal_generated_flag = False
        
        while self.current_agent != "summary_agent":
            # Agent1: 의도파악 에이전트 실행
            intent = self.intent_replanning_agent(user_input, session_id) #1:일반, 2:작품설명
            if intent == str(2):
                """작품설명이어서 로봇으로 바로 값 전송"""
                respond_goal_chat = "작품 설명 완료"
                
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id, time_stamp, user_input, respond_goal_chat, self.current_agent)
                
                print(f"의도2(미들웨어) : ", intent)
                print(f"respond_goal_chat : ", respond_goal_chat)
                return self.current_agent, respond_goal_chat, intent
            else:
                """골 추론 에이전트 돌릴 경우"""
                self.current_agent = "goal_chat_agent"
                print(f"의도1(우리) : ", intent)
            

            # 1. 채팅 에이전트 실행
            if self.current_agent == "goal_chat_agent":
                respond_goal_chat = self.respond_replanning_chat_agent(user_input, previous_poi_list)
                # 챗 히스토리 저장
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, respond_goal_chat, self.current_agent)
                
                print("111111111111111111111111111111111111111111111111111111111111111111111")
                # 채팅 응답을 반환하고 다음 에이전트로 넘어감
                self.current_agent = "generate_poi_list_agent"
            
            # 2. POI 리스트 생성 에이전트 실행
            if self.current_agent == "generate_poi_list_agent":
                
                # 채팅 에이전트가 남긴 챗 히스토리 다시 로드
                self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                self.poi_list = self.respond_replanning_generate_poi_list_agent(previous_poi_list, self.ro_x, self.ro_y, self.chat_history)
                print("22222222222222222222222222222222222222222222222222222222222222222222222")
                # 목표 완료 확인 에이전트로 넘어감
                self.current_agent = "goal_done_check_agent"

            # 3. 목표 완료 확인 에이전트 실행
            if self.current_agent == "goal_done_check_agent":
                # poi 리스트 생성 에이전트가 남긴 챗 히스토리 다시 로드
                self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                goal_done = self.respond_goal_done_check_agent(self.poi_list, self.chat_history)

                print("33333333333333333333333333333333333333333333333333333333333")
 
                

                if goal_done:
                    # 목표가 완료되었으면 Summary 에이전트로 이동
                    self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)  
                    self.poi_list = self.response_goal_validation_agent(self.poi_list, self.chat_history)                    
                    self.current_agent = "summary_agent"
                    print("GOAL DONE: TRUE")
                    print("44444444444444444444444444444444444444444444444444444444444444444444")
                    
                else:
                    # 목표가 완료되지 않았으면 해당 기록 저장하고 다시 채팅 에이전트로 돌아감
                    # 에이전트 응답 결과 저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    print("55555555555555555555555555555555555555555555555555555555555555")
                    
                    # 채팅에이전트로 라우팅
                    self.current_agent = "goal_chat_agent"
                    print("GOAL DONE: FALSE")
                    intent = 1
                    return self.current_agent , respond_goal_chat, intent  # 서버로 채팅 응답 전송 후 루프 계속

        # 4. Summary 에이전트 실행 (목표 완료 후)
        if self.current_agent == "summary_agent":
            self.chat_history = self.db_manager.get_conversation_history(self.robot_id, session_id)

            # 1단계: Summary 에이전트 실행 후 요약 질문 반환
            respond_goal_chat, goal_generated = self.respond_summary_agent(user_input, self.poi_list, self.chat_history)
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            
            if not self.summary_flag: # False 처음 서머리 에이전트가 탈 경우
                # 첫 번째 단계에서는 goal_generated를 아직 체크하지 않고 요약 질문을 사용자에게 보냄 (None)
                self.current_agent = "summary_agent"
                self.summary_flag = True
                print("@@@@@@@@@@@@써머리처음")
                
                #db저장
                time_stamp = str(datetime.now())
                self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                return self.current_agent, respond_goal_chat, intent

            else:
                if goal_generated == False:
                # goal_generated가 False면 다시 대화 에이전트로 돌아감
                    respond_goal_chat = "기존 계획을 초기화 하겠습니다. 안내받고 싶은신 장소를 다시 처음부터 말씀해주세요."
                    print("~~~~~~~~~~~~~~~써머리두번째 부정적 답변받은 상황")

                    self.current_agent = "goal_chat_agent"
                    self.summary_flag = False
                    #db저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    self.restart_service()
                    return self.current_agent, respond_goal_chat, intent  # intent = 1: 다시 채팅으로 돌아감


                else: # True
                    # goal_generated가 True면 안내를 시작하는 응답 반환
                    respond_goal_chat = "안내를 시작하겠습니다."
                    print("===============써머리두번째 긍정적 답변받은 상황")
                    self.current_agent = "END"
                    self.summary_flag = False
                    intent = 3
                    #db저장
                    time_stamp = str(datetime.now())
                    self.db_manager.add_turn(self.robot_id, self.session_id,time_stamp, user_input, goal_done, self.current_agent)
                    return self.current_agent, respond_goal_chat, intent  # intent = 3: 안내 시작