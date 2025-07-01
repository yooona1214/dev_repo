###### 기본 정보 설정 단계 #######
from fastapi import Request, FastAPI
import openai
import threading
import time
import queue as q
import os


from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores.chroma import Chroma
import streamlit as st
import time
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.chat_models import ChatOpenAI
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory

from loader import Loader_Rag , Loader_Voc

##################
FLAG_RAG = False
FLAG_VOC = True
Cause_list = 0
##################

if FLAG_RAG: 
    # ChatGPT엔진 메모리 할당
    loader_mem = Loader_Rag()
    loader_mem.load_all()

if FLAG_VOC:
    loader_mem = Loader_Voc()
    loader_mem.load_all()

# OpenAI API KEY
API_KEY = "sk-"
# client = openai.OpenAI(api_key = API_KEY)


###### 서버 생성 단계 #######
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "kakaoTest"}

@app.post("/chat/")
async def chat(request: Request):
    kakaorequest = await request.json()
    # print(kakaorequest)
    # return
    return mainChat(kakaorequest)



###### 카카오톡 응답 함수 ######
# 메세지 전송
def textResponseFormat(bot_response):
    response = {'version': '2.0', 'template': {
    'outputs': [{"simpleText": {"text": bot_response}}], 'quickReplies': []}}
    return response

# 응답 초과시 답변
def timeover():
    response = {"version":"2.0","template":{
      "outputs":[
         {
            "simpleText":{
               "text":"아직 제가 생각이 끝나지 않았어요🙏🙏\n잠시후 아래 말풍선을 눌러주세요👆"
            }
         }
      ],
      "quickReplies":[
         {
            "action":"message",
            "label":"생각 다 끝났나요?🙋",
            "messageText":"생각 다 끝났나요?"
         }]}}
    return response

# 텍스트파일 초기화
def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")


# ChatGPT에게 질문/답변 받기 #yna: 이걸 상흠전임님 코드로 수정해야함
def getTextFromGPT(messages):
    message = loader_mem.chagwithGPT(messages)
    return message

def getCauseFromGPT(messages):
    Cause_list = loader_mem.find_cause(messages)
    return Cause_list

###### 메인 함수 단계 #######

# 메인 함수
def mainChat(kakaorequest):

    run_flag = False
    start_time = time.time()

    # 응답 결과를 저장하기 위한 텍스트 파일 생성
    cwd = os.getcwd()
    filename = cwd + '/botlog.txt'
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
    else:
        print("File Exists")    

    # 답변 생성 함수 실행
    response_queue = q.Queue()
    request_respond = threading.Thread(target=responseOpenAI,
                                        args=(kakaorequest, response_queue,filename))
    request_respond.start()

    # 답변 생성 시간 체크
    while (time.time() - start_time < 3.5):
        if not response_queue.empty():
            # 3.5초 안에 답변이 완성되면 바로 값 리턴
            response = response_queue.get()
            run_flag= True
            break
        # 안정적인 구동을 위한 딜레이 타임 설정
        time.sleep(0.01)

    # 3.5초 내 답변이 생성되지 않을 경우
    if run_flag== False:     
        response = timeover()

    return response


# 답변/사진 요청 및 응답 확인 함수
def responseOpenAI(request,response_queue,filename):
    
    if FLAG_VOC:

        # 사용자다 버튼을 클릭하여 답변 완성 여부를 다시 봤을 시
        if '생각 다 끝났나요?' in request["userRequest"]["utterance"]:
            # 텍스트 파일 열기
            with open(filename) as f:
                last_update = f.read()
            # 텍스트 파일 내 저장된 정보가 있을 경우
            if len(last_update.split())>1:
                kind = last_update.split()[0]  
                if kind == "img":
                    print("kkk")
                else:
                    bot_res = last_update[4:]
                    response_queue.put(textResponseFormat(bot_res))
                dbReset(filename)

            
        #ChatGPT 답변을 요청한 경우
        else:
            dbReset(filename)

            #VOC 문의 첫 메세지 - 원인 분석
            if len(Cause_list)==0: 
            # if '문의' in request["userRequest"]["utterance"]:
                Cause_list = getCauseFromGPT(request["userRequest"]["utterance"])
                bot_res = Loader_Voc.findCausewithGPT(Cause_list, 0)
                response_queue.put(textResponseFormat(bot_res))
                index = 1
            
            else:
                bot_res = Loader_Voc.findCausewithGPT(Cause_list, index)
                response_queue.put(textResponseFormat(bot_res))
                index += 1

                # bot_res = getTextFromGPT(request["userRequest"]["utterance"])
                # response_queue.put(textResponseFormat(bot_res))

                # save_log = "ask"+ " " + str(bot_res)
                # with open(filename, 'w') as f:
                #     f.write(save_log)

    if FLAG_RAG:
        # 사용자다 버튼을 클릭하여 답변 완성 여부를 다시 봤을 시
        if '생각 다 끝났나요?' in request["userRequest"]["utterance"]:
            # 텍스트 파일 열기
            with open(filename) as f:
                last_update = f.read()
            # 텍스트 파일 내 저장된 정보가 있을 경우
            if len(last_update.split())>1:
                kind = last_update.split()[0]  
                if kind == "img":
                    print("kkk")
                else:
                    bot_res = last_update[4:]
                    response_queue.put(textResponseFormat(bot_res))
                dbReset(filename)

            
        #ChatGPT 답변을 요청한 경우
        else:
            # # 기본 response 값
            # base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}
            # response_queue.put(base_response)
            dbReset(filename)

            bot_res = getTextFromGPT(request["userRequest"]["utterance"])
            response_queue.put(textResponseFormat(bot_res))

            save_log = "ask"+ " " + str(bot_res)
            with open(filename, 'w') as f:
                f.write(save_log)