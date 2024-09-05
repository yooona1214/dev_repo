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

# Redis 클라이언트 생성
r = redis.Redis(host='localhost', port=6379, db=0)

# Goal.json 파일 경로
GOAL_JSON_PATH = 'data/goal.json'
 
# DB manager 생성
dbmanager = DBManager(r)

# Router 생성
router = Router(encoder=OpenAIEncoder())

# multi agents 선언
goal_inference_agent = GoalInferenceAgent(dbmanager, GOAL_JSON_PATH)

# task manager 선언
task_manager = TaskManager()

###서비스가 끝나면 비워야 하는데 이건 좀 생각을 해보쟈####
# 종료 시 Redis 캐시를 비우도록 atexit에 등록
atexit.register(dbmanager.clear_redis_cache)



    