from fastapi import Request, FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from aiosqlite import connect
from cachetools import Cache, LRUCache

from kakaomessage import *
from tool import *
import csv
import pandas as pd
import os

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

# 캐쉬 메모리 생성
UserCacheDict= UserCacheManager() 




async def classify_issue(utterance: str) -> IssueClassificationResult:

    """
    여기에 llm 추가
    """
    issue_category = "Something?????"
    return IssueClassificationResult(category=issue_category)

async def preprocess_user_message(csv_path, classification_result: IssueClassificationResult):

    ## csv 불러와서 데이터 전처리
    issue = classification_result.category


    df = pd.read_csv(csv_path)
    selected_rows = df[df['이슈분류'] == issue]

    # 원인을 탐색하고 각 원인이 얼마나 발생했는지 정규화하여 저장
    issue_counts = selected_rows['원인(원인별명)'].value_counts(normalize=True)

    # 각 원인에 대한 '고객조치가능여부' 값 가져오기
    customer_actions = selected_rows.groupby('원인(원인별명)')['고객조치가능여부'].first()
    detail_actions = selected_rows.groupby('원인(원인별명)')['조치 방법'].first()

    # DataFrame으로 변환
    result_df = pd.DataFrame({
        '원인': issue_counts.index,
        '고객조치가능여부': customer_actions.loc[issue_counts.index].values,
        '빈도': issue_counts.values,
        '조치 방법': detail_actions.loc[issue_counts.index].values
    })   

    result_df = result_df.sort_values(by=['고객조치가능여부', '빈도'], ascending=[False, False])
    
    # 가공된 pd 프레임 데이터를 반환
    return result_df


async def csv_to_cache(csv_path, classification_result: IssueClassificationResult):
    
    pd_frame = await preprocess_user_message(csv_path, classification_result)



async def initialize_database(user_db_path):

    async with connect(user_db_path) as db:
        
        # 유저 데이터 db 없다면 생성 및 초기화
        if not os.path.exists(user_db_path):
            await db.execute('''
                    CREATE TABLE IF NOT EXISTS chatbot_data (
                        이슈분류 TEXT,
                        원인 TEXT,
                        고객조치가능여부 TEXT,
                        조치방법 TEXT,
                        답변체크여부 TEXT
                            )
                    ''')
                            
            await db.commit()
        
        # 있으면 그냥 load
        else:
            pass



@app.on_event("startup")
async def on_startup():
    print("Server Loaded")

@app.get("/")
async def root():
    return {"message": "kakaoTest"}


@app.post("/chat/", response_model=KakaoAPI)
async def chat(content: KakaoAPI):
    """
    캐쉬 메모리가 없으면, 처음 문제제기 발화임.
    
    캐쉬 메모리 none 이면 classification
    캐쉬메모리가 존재하면 순서대로 질문
    """

    user_id = content.userRequest.user.id
    user_db_path =  './userdata/' +user_id + 'kakaobot.db' 
    csv_path = './data/주행관련VOC테스트_이슈-원인0123.csv'
    
    # 유저별 db 생성
    await initialize_database(user_db_path)

    try: ##### 여기부터 고치기
        if user_id not in UserCacheDict.user_caches:
            # 사용자 발화 이슈분류 
            classification_result = await classify_issue(content.userRequest.utterance)
            
            # 이슈 원인 데이터 load, db로 저장
            something = await csv_to_cache(csv_path, classification_result)

            # first question

            # issue clarified no 
            return response = kako(json)

        else:
            # get_user_cache with user id

            # 2nd question --- nth 


            if check_condition:

                return 
            

            pass #############
            
            

    except Exception as e:
        return JSONResponse(content={"response": f"에러 발생: {str(e)}"}, status_code=500)


