"""카카오톡 FAST API LLM Agent 서버와 연동 모듈"""

import time
import json
import logging

import requests

from fastapi import Request, FastAPI, BackgroundTasks
from dev.chat_processor import ChatProdCons

# FastAPI 서버 연결
app = FastAPI()


@app.get("/")
async def root():
    """get user messages"""
    return {"message": "kakaoTest"}


@app.post("/chat/")
async def chat(request: Request, background_tasks: BackgroundTasks):
    """post"""

    kakaorequest = await request.json()

    background_tasks.add_task(response_agent, request=kakaorequest)

    # response_chat = response_chat(request=kakaorequest)
    # return response_chat
    return {"version": "2.0", "useCallback": True}


# ChatGPT에게 질문/답변 받기
def get_text_from_gpt(messages, data):
    """ChatGPT에게 질문/답변 받기"""

    logging.info("메시지: %s", messages)
    logging.info("데이터: %s", data)
    user_id = data["user_id"]
    logging.info(type(messages))
    logging.info(type(data))
    rmq = ChatProdCons()
    rmq.initialize_response()
    rmq.sender(messages, user_id)
    message = rmq.return_response()
    logging.info("getTxt %s", message)
    return message


def response_agent(request):
    """콜백 기반 LLM 응답(최대 1분)"""

    user_id = request["userRequest"]["user"]["id"]
    message = request["userRequest"]["utterance"]
    callback_url = request["userRequest"]["callbackUrl"]

    # 딕셔너리 데이터
    data = {"user_id": user_id, "message": message}

    # 데이터를 JSON 문자열로 직렬화
    msg = json.dumps(data)

    gpt_res = get_text_from_gpt(msg, data)
    logging.info("gpt_res: %s", gpt_res)

    res_kakao = {
        "version": "2.0",
        "template": {"outputs": [{"simpleText": {"text": gpt_res}}]},
    }

    response = requests.post(url=callback_url, json=res_kakao, timeout=15)

    return response


def response_chat(request):
    """콜백 없이 디폴트 설정(5초 뒤 응답 사라짐)"""
    user_id = request["userRequest"]["user"]["id"]
    message = request["userRequest"]["utterance"]

    # 딕셔너리 데이터
    data = {"user_id": user_id, "message": message}

    start_time = time.time()
    gpt_res = None

    logging.info("1st_time %s", round(time.time() - start_time))

    # 데이터를 JSON 문자열로 직렬화
    msg = json.dumps(data)

    gpt_res = get_text_from_gpt(msg, data)

    res_kakao = {
        "version": "2.0",
        "template": {"outputs": [{"simpleText": {"text": gpt_res}}]},
    }

    return res_kakao
