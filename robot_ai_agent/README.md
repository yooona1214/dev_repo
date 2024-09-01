# Robot AI Agent

메인 파일
- main.py
- 입력값 받은 후 라우터 전달
- 디비 매니저의 턴 메세지 저장을 통해 매 대화 턴을 캐쉬메모리에 저장

모니터링
- monitor_redis.py
- 캐쉬 메모리 모니터링하는 파일

라우터
- modules/router.py
- semantic router를 사용하여 입력발화의 context에 따른 라우팅

디비 매니저
- modules/db_manager.py
- 턴별 대화 redis 캐쉬메모리 저장 및 관리
- 세션 종료 후 캐쉬메모리 장기메모리에 저장 
- postgreSQL db 확인 후, 없으면 생성
- 있으면 해당 db에 대화 세션별로 redis 메모리 저장
- 세션 종료 후 대화 redis 메모리 삭제

멀티 에이전트 
- modules/agents.py
- 실제 실행할 프롬프트기반 챗지피티들
-
