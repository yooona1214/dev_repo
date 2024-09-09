"""FAST API LLM Agent 서버와 연동 모듈"""

import time
import json
import logging
from datetime import datetime

import requests

from fastapi import Request, FastAPI, BackgroundTasks

import numpy as np
import pandas as pd
import os
import redis
import atexit
from dotenv import load_dotenv

from task_manager import *
from modules.agents2 import *
from modules.router import *
from modules.db_manager import *



# FastAPI 서버 연결
app = FastAPI()

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)

# Goal.json 파일 경로
GOAL_JSON_PATH = 'data/goal.json'
 
# DB manager 생성
dbmanager = DBManager(r)

###서비스가 끝나면 비워야 하는데 이건 좀 생각을 해보쟈####
# 종료 시 Redis 캐시를 비우도록 atexit에 등록
atexit.register(dbmanager.clear_redis_cache)


agents = {}

def get_or_create_agent(robot_id):
    if robot_id not in agents:
        # 에이전트가 없으면 생성 후 딕셔너리에 저장
        agent = GoalInferenceAgent(dbmanager, GOAL_JSON_PATH)
        agents[robot_id] = agent
        logging.info(f"Created new agent for robot_id: {robot_id}")
    else:
        agent = agents[robot_id]
        logging.info(f"Using existing agent for robot_id: {robot_id}")
    return agent

@app.get("/")
async def root():
    """get user messages"""
    return {"message": "ROBOT SERVER IS OPENED"}

# 1. 골 추론 요청
@app.post("/action_request/")
async def chat(request: Request):
    """post"""

    robotrequest = await request.json()
    response_chat = response_chat_goal(request=robotrequest)
    
    return response_chat


def response_chat_goal(request):
    """콜백 기반 LLM 응답"""

    # 로봇 데이터 파싱
    robot_id = request["robot_id"]
    user_input = request["user_query"]
    time_stamp = request["time_stamp"]
    robot_x = request["loc_x"]
    robot_y = request["loc_y"]
    
    # 로봇 id 별 에이전트 인스턴스 생성
    goal_infer_agent = get_or_create_agent(robot_id)
    
    # 첫 발화기준 로봇 세션 id 생성
    session_id = goal_infer_agent.check_new_service(robot_id)
    
    # 골 추론 에이전트 
    agent_id, agent_response = goal_infer_agent.route(user_input,robot_x, robot_y, session_id)
    logging.info("gpt_res: %s", agent_response)

    # 디비에 저장
    dbmanager.add_turn(robot_id, session_id, time_stamp, user_input, agent_response, agent_id)
    
    # 응답 보내기
    res_chat_goal = {"output": agent_response}

    return res_chat_goal


# 2. poi_list 요청 Task manager 실행
@app.post("/poi_list/{robot_id}")
async def chat(robot_id: str,request: Request):
    """
    골 추론 에이전트에서, poi_list가 뽑히고, goal.json이 모두 생성 된 후에 전송 될것
    Task manager 실행 """

    #### 여기는 책임님 코드 완료 되면 주석 해제
    # instance_goal_agent = goal_infer_agent(robot_id)
    # # 여기서 poi 리스트 뽑기전에, poi검증도 하고, goal.json 추출도 다 할것임
    # ### 다 됐다는 트리거 필요
    # # 여기서 poi 설정값 리스트 [[poi1, 103], [poi2, 100],''''] 요런식 나올것임
    # response_poi_arg_list = instance_goal_agent.get_poi_list()
    
    #### 그전까지 테스트
    done = False
    
    robotrequest = await request.json()
    response_poi_arg_list = response_poi_arg(request=robotrequest)
        


    # robot_id 별로 task manager 선언
    task_manager = TaskManager.get_instance(robot_id)
    
    # goal_agent에서 생성한 poi 설정값 리스트으로 current_service_start 서비스에 보낼 goal.json 생성
    goal_json = task_manager.generate_goal_json(response_poi_arg_list)
    
    # task manager에서 사용할 상태 테이블 생성
    task_manager.initialize_poi_state_dict(goal_json)
    done = True

    if done:
        return response_poi_arg_list

def response_poi_arg(request):
    return request['poi_arg_list']




# 3. current_service_start 요청
@app.post("/current_service_start/{robot_id}")
async def chat(robot_id: str,request: Request):
    """post"""
    robotrequest = await request.json()

    # robot_id 에 맞는 task_manager 인스턴스 로드
    task_manager =  TaskManager.get_instance(robot_id)
    
    # poi_state_dict를 보고 현재 not_done인 가장 빠른 poi의 정보를 불러오기
    task_manager.find_current_poi()
    
    # current_service_start 생성
    task_manager.send_current_service_start(service_id, task)
    return 


# task_finished 요청
@app.post("/task_finished/{robot_id}")
async def chat(request: Request):
    """post"""

    robotrequest = await request.json()

    return 


# replanning 요청
@app.post("/replanning/{robot_id}")
async def chat(request: Request):
    """post"""

    robotrequest = await request.json()

    return 



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)