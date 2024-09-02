

## history with llm
https://github.com/langchain-ai/langchain/issues/5890



## 프롬프트 후추 관련 자료
https://ncsoft.github.io/ncresearch/f4a00ed849299e3c91fb3244e74ea7f9b974ebb7

https://github.com/langchain-ai/langchain/issues/4044

https://jayhey.github.io/deep%20learning/2023/04/29/langchain-practice/

카카오톡, 챗봇 세션 연동 - 멀티스레드

사용자 기록 연동


## FastAPI로 로컬 서버 생성
python -m uvicorn kakaobot:app --reload


## ngrok 토큰 등록
ngrok config add-authtoken 2amxjrTAq8tsD02o2Ds4JqgCges_2hTjD1iZVStiwptCWpZfn


## Ngrok로 서버 접속 주소 생성 
ngrok http 8000


## Ngrok을 통해 로컬 서버를 외부에 공개한 주소
Forwarding 한 주소를 입력
얘는 ngrok 실행할 때마다 달라짐

https://580a-14-52-91-70.ngrok-free.app

 
## 해야될 것 
-사용자 별로 chat history 메모리 관리
agent는 냅두고
system message 추가 될때마다 메모리 추가
-응답이 5분이상없으면 메모리 해제하는 방법


#### 0123 해야할 것
- 같은 원인에 대해 조치방법이 여러개 일 수 있다.
- 그럴 때, sort 하는 방법
- (중요) 이걸 llm으로 상황 파악하며 해결책을 내놓아야한다!!!!!
- 이럴 때, 역질문 해야하는것같다
- 상황 파악이 되면, 마지막 답변을 내놓아 종결짓는다
- 이 방법 강구 강구
