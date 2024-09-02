from fastapi import Request, FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from aiosqlite import connect
from cachetools import Cache, LRUCache
import queue as q

from kakaomessage import *
from tool import *
import csv
import pandas as pd
import os
import time
import threading
import json
from dev.chat_processor import ChatProdCons

# async def save_to_database(key: str, value: IssueClassificationResult):
#     async with connect("kakaobot.db") as db: # 데이터 베이스 연결과 같은 리소스 관리를 할때 with를 씀
#         await db.execute("INSERT INTO cache (key, value) VALUES (?, ?)", (key, value.category))
#         await db.commit()


# async def load_from_database(key: str) :
#     async with connect("kakaobot.db") as db:
#         cursor = await db.execute("SELECT value FROM cache WHERE key = ?", (key,))
#         result = await cursor.fetchone()
#         return IssueClassificationResult(category=result[0]) if result else None


# FastAPI 서버 연결
app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("Server Loaded")


@app.get("/")
async def root():
    return {"message": "kakaoTest"}


@app.post("/chat/")
async def chat(request: Request):
    kakaorequest = await request.json()
    return mainChat(kakaorequest)


# 메세지 전송
def textResponseFormat(bot_response):
    response = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": bot_response}}],
            "quickReplies": [],
        },
    }
    return response


# 응답 초과시 답변
def timeover():
    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "아직 제가 생각이 끝나지 않았어요🙏🙏\n잠시후 아래 말풍선을 눌러주세요👆"
                    }
                }
            ],
            "quickReplies": [
                {
                    "action": "message",
                    "label": "생각 다 끝났나요?🙋",
                    "messageText": "?",
                }
            ],
        },
    }
    print("time is over")
    return response


# 텍스트파일 초기화
def dbReset(filename):
    with open(filename, "w") as f:
        f.write("")


# ChatGPT에게 질문/답변 받기 #yna: 이걸 상흠전임님 코드로 수정해야함
def getTextFromGPT(messages, data):
    print("메시지:", messages)
    print("데이터:", data)
    user_id = data["user_id"]

    print(type(messages))
    print(type(data))
    RMQ = ChatProdCons()
    RMQ.initialize_response()
    RMQ.sender(messages, user_id)
    message = RMQ.return_response()
    print("getTxt", message)
    return message


###### 메인 함수 단계 #######


# 메인 함수
def mainChat(kakaorequest):

    run_flag = False
    start_time = time.time()

    # 응답 결과를 저장하기 위한 텍스트 파일 생성
    # user_id = kakaorequest["userRequest"]["user"]["id"]
    # cwd = os.getcwd()
    # filename = cwd +'/'+ user_id + '_botlog.txt'
    # if not os.path.exists(filename):
    #     with open(filename, "w") as f:
    #         f.write("")
    # else:
    #     print("File Exists")

    # 답변 생성 함수 실행
    response_queue = q.Queue()
    request_respond = threading.Thread(
        target=responseOpenAI, args=(kakaorequest, response_queue)
    )
    request_respond.start()
    response = response_queue.get()

    # 답변 생성 시간 체크
    while time.time() - start_time < 4:
        if not response_queue.empty():
            # 3.5초 안에 답변이 완성되면 바로 값 리턴
            response = response_queue.get()
            run_flag = True
            break
        # 안정적인 구동을 위한 딜레이 타임 설정
        time.sleep(0.01)

    # 3.5초 내 답변이 생성되지 않을 경우
    if run_flag == False:
        response = timeover()
        # response = response_queue.get()

    return response


def responseOpenAI(request, response_queue):

    # # 사용자다 버튼을 클릭하여 답변 완성 여부를 다시 봤을 시
    # if '생각 다 끝났나요?' in request["userRequest"]["utterance"]:
    #     # 텍스트 파일 열기
    #     with open(filename) as f:
    #         last_update = f.read()
    #     # 텍스트 파일 내 저장된 정보가 있을 경우
    #     if len(last_update.split())>1:
    #         kind = last_update.split()[0]
    #         if kind == "img":
    #             print("kkk")
    #         else:
    #             bot_res = last_update[4:]
    #             response_queue.put(textResponseFormat(bot_res))
    #         dbReset(filename)

    # ChatGPT 답변을 요청한 경우
    # else:
    # # 기본 response 값
    # base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}
    # response_queue.put(base_response)
    user_id = request["userRequest"]["user"]["id"]
    message = request["userRequest"]["utterance"]

    # 딕셔너리 데이터
    data = {"user_id": user_id, "message": message}

    # 데이터를 JSON 문자열로 직렬화
    msg = json.dumps(data)

    bot_res = getTextFromGPT(msg, data)
    response_queue.put(textResponseFormat(bot_res))
