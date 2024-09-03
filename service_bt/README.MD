# KT Behavior Tree

## 변경 이력

| 버전  |    날짜    | 변경내역                                                                                                                               |
| ----- | :--------: | :------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.0 | 2023-06-08 | Init, Idle, moving, elevator, manualdriving, tray_load(1,2),  tray_unload(1,2), tray_fail(1,2), tray_cancel(1,2),   |
| 2.0.0a | 2023-06-09 | 관리자 비번 check 및 유저 터치 응답 관련 알람 노드 일부 수정   |
| 2.0.1 | 2023-06-14 | 엘레베이터 탑승,하차 테스트 완료 버전. 서비스 이동 중 취소, 반송등 수정   |
| 2.0.1a | 2023-06-15 | 서비스 반복시, 비밀번호 해제 오류 수정   |
| 2.0.1b | 2023-06-15 | 충전서비스 테스트버전 반영   |
| 2.0.1c | 2023-06-20 | LED, 충전 서비스 1차 테스트 완료 버전 반영   |
| 2.0.2 | 2023-06-21 | 충전 도킹 에러 시나리오 테스트 및 부팅 시나리오 테스트 버전 반영 |
| 2.0.2a | 2023-06-22 | 주행 인터페이스 변경(set_nav_goal) 반영 버전 추가 -  테스트 필요 |
| 2.0.2b | 2023-06-23 | 주행 인터페이스 변경(set_nav_goal) 반영 버전 추가 -  테스트 필요2 |
| 2.0.3 | 2023-06-23 | 주행 인터페이스 변경(set_nav_goal) 반영 버전 추가 -  테스트 완료 |
| 2.0.3a | 2023-06-23 | 멀티 로봇 주행 대응 버전 반영  |
| 2.0.3b | 2023-06-25 | nav_status unset 이슈 해결 반영  |
| 2.0.4 | 2023-06-25 | 테스트 버전  |
| 2.0.4a | 2023-06-26 | manual uncontact 알람 수정  |
| 2.0.4b | 2023-06-27 | 충전시나리오 수정 버전 반영  |
| 2.0.4c | 2023-06-28 | 반송 기능 수정 버전 반영  |
| 2.0.5 | 2023-06-28 | EV 승하차 기능 수정 버전 반영  |
| 2.0.5a | 2023-06-28 | 테스트 일부기능 수정  |
| 2.0.5b | 2023-06-28 | 테스트 일부기능 수정   |
| 2.0.5c | 2023-06-28 | 테스트 일부기능 수정   |
| 2.0.6 | 2023-06-30 | 테스트 일부기능 수정   |
| 2.0.6a | 2023-06-30 | 테스트 일부기능 수정   |
| 2.0.6b | 2023-07-03 | 테스트 일부기능 수정   |
| 2.0.6c | 2023-07-04 | tts, led 디테일링 작업(진행중)   |
| 2.0.7 | 2023-07-05 | undocking fail 기능, 멀티배송 시 트레이 안닫힘 이슈 해소   |
| 2.0.7a | 2023-07-05 | test   |
| 2.0.7b | 2023-07-05 | docking, undocking fail 기능, tray fail 기능 이슈 해소  |
| 2.0.7c | 2023-07-06 | test  |
| 2.0.7d | 2023-07-06 | test  |
| 2.0.7e | 2023-07-10 | 입력 대기시간 로직 수정 및 개발  |
| 2.0.8 | 2023-07-11 | 입력 대기시간 로직 수정 및 개발 보완 및 테스트(완)   |
| 2.0.8a | 2023-07-12 | TTS인터페이스 수정, low battery 서비스 수정 및 개발   |
| 2.0.8b | 2023-07-14 | 신규TTS 반영(테스트필요 - MW), 수동충전시 트레이 회수 기능 개발(테스트필요 - UI)  |
| 2.0.8c | 2023-07-17 | test  |
| 2.0.8d | 2023-07-18 | tray_stuck 개발중  |
| 2.0.8e | 2023-07-19 | tray_stuck 개발중  |
| 2.0.9 | 2023-07-20 | tray_stuck 개발완료  |
| 2.0.9a | 2023-07-21 | 서비스매니저 액션노드 변경에 따른 수정(@@주의: 미들웨어 서비스매니저 업데이트 반영 버전 이후 사용 가능@@)  |
| 2.0.9b | 2023-07-24 | ros 인터페이스 exception 처리 개발(@@주의: 미들웨어 서비스매니저 업데이트 반영 버전 이후 사용 가능@@)  |
| 2.0.9c | 2023-07-26 | 트레이 비밀번호 3회 틀림 시나리오 수정  |
| 2.0.9d | 2023-07-27 | 수동운전시 수동충전 진입 이슈 해소 |
| 2.0.9e | 2023-07-27 | 경로탐색노드 실패 대응 등 방어로직 구현 |
| 2.0.9f | 2023-08-01 | 엘레베이터 탑승 시, 수동운전 진입 이후 경로탐색 기능 등 구현 |
| 2.0.9g | 2023-08-02 | 주행중 취소 및 일시정지 시 알람 개발, 에러상황에서 관리자 암호 및 트레이동작, 주행 실패 시 에러 처리 개발   |
| 2.0.9h | 2023-08-03 | 부팅이후 배터리 20% 체크 / 서비스 시작 전후 수동운전 진입 분기 개발  |
| 2.0.9i | 2023-08-04 | 엘리베이터 예외 케이스 개발 완료  |
| 2.0.9j | 2023-08-07 | Map Change / task_available / reserve / route_searching  |
| 2.0.9k | 2023-08-07 | cancel alarm 추가, low_battery tree enqueue 이슈  |
| 2.0.9l | 2023-08-07 | undocking idle config password issue  |
| 2.0.9m | 2023-08-09 | 서비스 취소시, 물품 회수 이슈 처리  |
| 2.0.9n | 2023-08-09 | 주행 실패시, idling 처리  |
| 2.0.9o | 2023-08-10 | major/critical error, cancel_return  |
| 2.0.9p | 2023-08-11 | cancel box open / ev zone checker / box_exception   |
| 2.0.9q | 2023-08-16 | low_battery_tree, tray_stuck at idle   |
| 2.0.9r | 2023-08-16 | tray_stuck : multi-tray   |
| 2.0.9s | 2023-08-22 | test   |
| 2.0.9t | 2023-08-25 | 끼임 보완, 충전 undocking 추가  |
| 2.0.9u | 2023-08-25 | unload1 - added task_finished, unload2 - tray_1 open, daegijangso - task_finished |
| 2.0.9v | 2023-08-30 | user_input_delayed alarm added (manual charging, low_battery) |                   
| 2.0.9w | 2023-09-01 | LED action node : service --> topic / TTS,BGM error process changed(4:major-->3:minor) / TTS added / cancel1 tree bug fixed |
| 2.0.9x | 2023-09-05 | manual charging tree : added tray_stuck before init / BB_init added(exception reset) after previous stucked (critical/low_battery/major/manual_charing/manualdriving) |
| 2.0.9y | 2023-09-07 | low battery tree item  |
| 2.0.9z | 2023-09-14 | z-original-11, user input time delay tts modified, manualdriving off check in major_error, za-13, tts play once, zb-14, meomchwi in fail2 |
| 2.1.0 | 2023-09-15 | new charging_status_alarm in undocking, meomchwi in tray_*2 |
| 2.1.0a | 2023-09-18 | low_battery, critical_error, manual_charging_tree tray_manual_par fixed for success / EV call_board_point unset added for multi floor|
| 2.1.0b | 2023-09-20 | EV unset for multi floor, user input delay alarm added|
| 2.1.0c | 2023-09-20 | poi success check initialized as None for preventing from route fail critical error|
| 2.1.0d | 2023-09-21 | low battery under 20 in idle added|
| 2.1.0e | 2023-09-26 | tts for stucks|
| 2.1.0f | 2023-10-16 | low battery tree task status 오류 해결|
| 2.1.0g | 2023-10-19 | SAT-1|
| 2.1.0h | 2023-10-23 | installation tree: BB_init service code, previous tree, low_battery idle |
| 2.1.0i | 2023-10-23 | installation tree: BB_init service code, previous tree, low_battery idle, no check service mode |
| 2.1.0j | 2023-10-25 | fail_2 tree BB init 수정 |
| 2.1.0k | 2023-11-06 | qr_result key added |
| 2.1.0l | 2023-11-14 | engineer mode / nav_failed modified |
| 2.1.0m | 2023-11-16 | bb_clear tree update - loosing message |
| 2.1.0n | 2023-11-20 | critical error tree bgm off |
| 2.1.0o | 2023-11-27 | decrypt |
| 2.1.0p | 2023-12-01 | decrypt added|
| 2.1.0q | 2024-02-16 | moving & ev - 충돌알람, 줄서기/양보 LED, 정지/취소 처리 결과 BB만 우선 추가 // emergency - 해제 후 init // 충전 - SW 에러 시 BB_clear|
| 2.1.0r | 2024-02-16 | moving - 정지명령 결과만 체크하도록 수정 // 수동충전이 끝난 뒤, ev/unknonw 지역 간적있을 경우 init tree / 금지구역상태일 경우 수동운전 on 후 수동운전트리로  |
| 2.1.0s | 2024-02-23 | check_installation_mode added on errortrees|
| 2.1.0t | 2024-02-26 | lineup recovery led changed|
| 2.1.0u | 2024-02-27 | seld_alarm, manualdriving keepout zone|
| 2.1.0v | 2024-02-27 | undocking fail count, manual charging tree init tree added|
| 2.1.0w | 2024-02-27 | chargingtree sw error battery 15 added|
| 2.1.0x | 2024-02-28 | charging tree hri, manual charging recovery, error trees-emergency|
| 2.1.0y | 2024-02-28 | charging_undocking tree - 도킹 에러 스테이트 확인 전 nav status통해 fail체크 먼저 실행|
| 2.1.0z | 2024-02-28 | 비상정지 시 bgm off|
| 2.1.1 | 2024-03-04 | map set added, error code 2 0 changed|
| 2.1.1a | 2024-03-05 | 비상정지 버튼 연속 활성화 대응, selector critical error2 added|
| 2.1.1b | 2024-03-05 | 멀티로봇 주행 상태 알람메세지 전송 요청사항 반영|
| 2.1.1c | 2024-03-05 | emergency tree button status edited|
| 2.1.1d | 2024-03-06 | emergency button status added, critical error emergency-alarm added, minor error emergency- switch to emergency tree|
| 2.1.1e | 2024-03-13 | moving tree, startnav & multirobotstatus switched|
| 2.1.1f | 2024-03-13 | 멀티로봇 엘리베이터 트리 task status 반영|
| 2.1.1g | 2024-05-02 | 멀티로봇 fleet모드 시 일시정지 후 led 색상 수정|
| 2.1.1h | 2024-05-14 | error 발생 시 nav cancel 명령 추가| 
| 2.1.1i | 2024-05-14 | critical/minor 에러트리에서 cancel goal 삭제, error 트리 진입 전 nav cancel 명령으로 수정, fleet모드에서 줄서기시 bgm off| 
| 2.1.1j | 2024-05-17 | moving tree 트레이 체크 방어로직 추가 |

