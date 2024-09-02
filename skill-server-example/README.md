

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

 
{'bot': {'id': '659e3b4a7407e2205bf34eae', 'name': '로봇 매뉴얼 응답 챗봇'}, 'intent': {'id': '659e3b4a7407e2205bf34eb3', 'name': '폴백 블록', 'extra': {'reason': {'code': 1, 'message': 'OK'}}}, 'action': {'id': '659f4b72d8a38d4f4a8980b7', 'name': '워크스테이션 PC  연결', 'params': {}, 'detailParams': {}, 'clientExtra': {}}, 'userRequest': {'block': {'id': '659e3b4a7407e2205bf34eb3', 'name': '폴백 블록'}, 'user': {'id': 'b944c102c5e245c62d787f2bec4d3064d410a7a28782609f2fe2e625b94a35505d', 'type': 'botUserKey', 'properties': {'botUserKey': 'b944c102c5e245c62d787f2bec4d3064d410a7a28782609f2fe2e625b94a35505d', 'isFriend': True, 'plusfriendUserKey': 'eZv-U-Hibbbo', 'bot_user_key': 'b944c102c5e245c62d787f2bec4d3064d410a7a28782609f2fe2e625b94a35505d', 'plusfriend_user_key': 'eZv-U-Hibbbo'}}, 'utterance': '메롱', 'params': {'surface': 'Kakaotalk.plusfriend'}, 'lang': 'ko', 'timezone': 'Asia/Seoul'}, 'contexts': []}
INFO:     219.249.231.42:0 - "POST /chat/ HTTP/1.1" 200 OK
INFO:     219.249.231.42:0 - "POST /chat/ HTTP/1.1" 200 OK
{'bot': {'id': '659e3b4a7407e2205bf34eae', 'name': '로봇 매뉴얼 응답 챗봇'}, 'intent': {'id': '659e3b4a7407e2205bf34eb3', 'name': '폴백 블록', 'extra': {'reason': {'code': 1, 'message': 'OK'}}}, 'action': {'id': '659f4b72d8a38d4f4a8980b7', 'name': '워크스테이션 PC  연결', 'params': {}, 'detailParams': {}, 'clientExtra': {}}, 'userRequest': {'block': {'id': '659e3b4a7407e2205bf34eb3', 'name': '폴백 블록'}, 'user': {'id': 'b944c102c5e245c62d787f2bec4d3064d410a7a28782609f2fe2e625b94a35505d', 'type': 'botUserKey', 'properties': {'botUserKey': 'b944c102c5e245c62d787f2bec4d3064d410a7a28782609f2fe2e625b94a35505d', 'isFriend': True, 'plusfriendUserKey': 'eZv-U-Hibbbo', 'bot_user_key': 'b944c102c5e245c62d787f2bec4d3064d410a7a28782609f2fe2e625b94a35505d', 'plusfriend_user_key': 'eZv-U-Hibbbo'}}, 'utterance': '어쩔', 'params': {'surface': 'Kakaotalk.plusfriend'}, 'lang': 'ko', 'timezone': 'Asia/Seoul'}, 'contexts': []}
INFO:     219.249.231.41:0 - "POST /chat/ HTTP/1.1" 200 OK
{'bot': {'id': '659e3b4a7407e2205bf34eae', 'name': '로봇 매뉴얼 응답 챗봇'}, 'intent': {'id': '659e3b4a7407e2205bf34eb3', 'name': '폴백 블록', 'extra': {'reason': {'code': 1, 'message': 'OK'}}}, 'action': {'id': '659f4b72d8a38d4f4a8980b7', 'name': '워크스테이션 PC  연결', 'params': {}, 'detailParams': {}, 'clientExtra': {}}, 'userRequest': {'block': {'id': '659e3b4a7407e2205bf34eb3', 'name': '폴백 블록'}, 'user': {'id': 'ee387209028435fb03855509db76b94eaf697c4fa88aecae44b37508e6d656ea50', 'type': 'botUserKey', 'properties': {'botUserKey': 'ee387209028435fb03855509db76b94eaf697c4fa88aecae44b37508e6d656ea50', 'isFriend': True, 'plusfriendUserKey': 'Rl43AjY2fX-L', 'bot_user_key': 'ee387209028435fb03855509db76b94eaf697c4fa88aecae44b37508e6d656ea50', 'plusfriend_user_key': 'Rl43AjY2fX-L'}}, 'utterance': '/ask ㅋㅋㅋ', 'params': {'surface': 'Kakaotalk.plusfriend'}, 'lang': 'ko', 'timezone': 'Asia/Seoul'}, 'contexts': []}
INFO:     219.249.231.41:0 - "POST /chat/ HTTP/1.1" 200 OK


사용자 별로 메모리 관리 - 파이썬

그 메모리를 나중에 래그에서 쓰게 캐쉬 저장하는것 - 랭체인