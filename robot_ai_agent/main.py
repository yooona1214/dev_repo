import numpy as np
import pandas as pd
import os
import redis
import atexit
from dotenv import load_dotenv

from modules.agents import *
from modules.router import *
from modules.db_manager import *

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)

# Goal.json 파일 경로
GOAL_JSON_PATH = 'data/goal.json'

# DB manager 생성
dbmanger = DBManager(r)

# Router 생성
router = Router(encoder=OpenAIEncoder())

# multi agents 선언
agents = get_multi_agents(dbmanger, GOAL_JSON_PATH)

# 종료 시 Redis 캐시를 비우도록 atexit에 등록
atexit.register(dbmanger.clear_redis_cache)

# 대화 main loop
START = False
while True:

    user_input = input("입력: ")
    if not START:
        # 현재 날짜와 시간을 세션 ID로 설정
        session_id = dbmanger.get_session_id()
        START = True
    
    # 모든 대화가 로봇 컨트롤임.
    route_name = "robot_control"
    current_agent = route_name

    response = current_agent.route(user_input, session_id)
    
    # agent_response = response['output']
    agent_response = response
    
    dbmanger.add_turn(session_id, user_input, agent_response, route_name)





    ###############
    # user_input = input("입력: ")
    # if not START:
    #     # 현재 날짜와 시간을 세션 ID로 설정
    #     session_id = dbmanger.get_session_id()
    #     START = True

    # route_name = router.route(user_input)
    # print("Route: ", route_name)
    # current_agent = agents[route_name]
    # # 라우팅
    # if route_name == "robot_control": # 로봇 컨트롤
    #     response = current_agent.route(user_input, session_id)
    
    # else: # 일반 대화
    #     response = current_agent.respond(user_input,session_id)

    # # agent_response = response['output']
    # agent_response = response
    
    # dbmanger.add_turn(session_id, user_input, agent_response, route_name)
    
    #################
    # # 라우팅
    # if route_name == "robot_control": # 로봇 컨트롤
    #     # response = current_agent.route(user_input, session_id)
    #     agent_response = "골추론 에이전트 개발 중"
    
    # else: # 일반 대화
    #     response = current_agent.respond(user_input,session_id)
    #     agent_response = response['output']
    
    # dbmanger.add_turn(session_id, user_input, agent_response, route_name)
    
    
    