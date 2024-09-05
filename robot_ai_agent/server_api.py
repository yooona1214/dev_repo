"""FAST API LLM Agent 서버와 연동 모듈"""

import time
import json
import logging

import requests

from fastapi import Request, FastAPI, BackgroundTasks

import numpy as np
import pandas as pd
import os
import redis
import atexit
from dotenv import load_dotenv

from modules.agents import *
from modules.router import *
from modules.db_manager import *
from modules.task_manager import *

# FastAPI 서버 연결
app = FastAPI()

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)

# Goal.json 파일 경로
GOAL_JSON_PATH = 'data/goal.json'
 
# DB manager 생성
dbmanager = DBManager(r)

# task manager 선언
# task_manager = TaskManager()

###서비스가 끝나면 비워야 하는데 이건 좀 생각을 해보쟈####
# 종료 시 Redis 캐시를 비우도록 atexit에 등록
atexit.register(dbmanager.clear_redis_cache)


agents = {}



@app.get("/")
async def root():
    """get user messages"""
    return {"message": "ROBOT SERVER IS OPENED"}

# 1. 골 추론 요청
@app.post("/chat_goal/")
async def chat(request: Request):
    """post"""

    robotrequest = await request.json()
    response_chat = response_chat_goal(request=robotrequest)
    
    return response_chat

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
    # Agent1. goal_chat_agent = input: 사용자 발화 / output: csv파일을 참조해서 가야할 목적지 list + 이 list가 맞는지 대답생성
    # Agent2. goal_json_agent = input: Agent1의 out인 list / output: goal.json
    # Agent3. goal_verify_agent = input: 챗 히스토리 / output: 알겠습니다 대답생성 or 다시 서비스를 생성하겠습니다 후 Agent1 라우팅
    agent_id, agent_response = goal_infer_agent.route(user_input,robot_x, robot_y, session_id)
    logging.info("gpt_res: %s", agent_response)

    # 디비에 저장
    dbmanager.add_turn(robot_id, session_id, time_stamp, user_input, agent_response, agent_id)
    
    # 응답 보내기
    res_chat_goal = {"output": agent_response}

    return res_chat_goal


# 2. 골 추론 요청
@app.post("/chat_goal/")
async def chat(request: Request):
    """post"""

    robotrequest = await request.json()
    response_chat = response_chat_goal(request=robotrequest)
    
    return response_chat



# # poi_dict 요청
# @app.post("/poi_dict/")
# async def chat(request: Request):
#     """post"""

#     robotrequest = await request.json()
#     response_chat = response_chat_goal(request=robotrequest)
    
#     return response_chat

# def response_poi(request):



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)