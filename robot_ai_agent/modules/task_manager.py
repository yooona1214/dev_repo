"""
2024.09.03

Task 생성 및 관리 모듈

def . 로봇 -> 서버 : poi_dic / 서버 -> 로봇 : Poi_dic

def2. 로봇 -> 서버 : current_service_start  /  서버 -> 로봇 : current_service_start

def3. 로봇 -> 서버 : Task_finished  /  서버 -> 로봇 : ok

def4. 로봇 -> 서버 : current_service_start  /  서버 -> 로봇 : current_service_start

def5. 로봇 -> 서버 : 리플래닝 요청 ("re_planning") / 서버 -> 로봇 : ok

"""
import requests
import json
from concurrent.futures import ThreadPoolExecutor

class TaskManager:
    def __init__(self, server_url):
        self.server_url = server_url
        self.poi_dict = {}  # POI 상태 관리 딕셔너리

    def initialize_poi_dict(self, goal_json):
        """goal.json을 받아 poi_dict를 초기화 후 반환"""
        task_list = goal_json["goal"]["task_list"]
        self.poi_dict = {
            task['POI']: 'not_done' for task in task_list
        }
        return self.poi_dict

    def send_poi_dict(self, poi_dict):
        """로봇 -> 서버 : poi_dict 전송 후 성공 여부 반환"""
        url = f"{self.server_url}/send_poi_dict"
        response = requests.post(url, json=poi_dict)
        if response.status_code == 200:
            print("POI Dict 전송 성공:", poi_dict)
            return True
        else:
            print("POI Dict 전송 실패:", response.status_code)
            return False

    def create_current_service_start(self, service_id, task):
        """goal.json의 task 정보를 기반으로 current_service_start 생성 후 반환"""
        current_service_start = {
            "service_id": service_id,
            "task_id": task['task_id'],
            "poi": task['POI'],
            "vel": task['task_detail']['vel'],
            "LED_effect": task['task_detail']['LED_effect']
        }
        return current_service_start

    def send_current_service_start(self, current_service_start):
        """로봇 -> 서버 : current_service_start 전송 후 성공 여부 반환"""
        url = f"{self.server_url}/send_current_service_start"
        response = requests.post(url, json=current_service_start)
        if response.status_code == 200:
            print("Current Service Start 전송 성공:", current_service_start)
            return True
        else:
            print("Current Service Start 전송 실패:", response.status_code)
            return False

    def update_poi_state(self, poi, state):
        """poi_dict의 특정 POI의 상태를 업데이트 후 상태 반환"""
        if poi in self.poi_dict:
            self.poi_dict[poi] = state
            print(f"POI '{poi}' 상태 업데이트: {state}")
            return self.poi_dict[poi]
        else:
            print(f"POI '{poi}' 상태 업데이트 실패: POI를 찾을 수 없음")
            return None

    def listen_for_task_status(self):
        """서버로부터 task_Status를 받아 처리 후 상태 반환 (여기서는 간단히 시뮬레이션)"""
        url = f"{self.server_url}/task_status"
        response = requests.get(url)
        if response.status_code == 200:
            task_status = response.json()
            poi = task_status.get('poi')
            status = task_status.get('status')
            if status == 'finished_Alarm':
                self.update_poi_state(poi, 'done')
            return task_status
        else:
            print("Task Status 수신 실패:", response.status_code)
            return None

    def reset_poi_dict(self):
        """poi_dict 초기화 후 초기화된 딕셔너리 반환"""
        self.poi_dict = {}
        print("POI Dict 초기화 완료")
        return self.poi_dict


def main():
    # TaskManager 인스턴스 생성
    task_manager = TaskManager("http://example.com/api")

    # goal.json 파일을 로드했다고 가정
    goal_json = {
        "goal": {
            "service_id": "service_1",
            "utterance": "Hello World",
            "task_num": 3,
            "task_list": [
                {
                    "task_id": "task_1",
                    "POI": "poi_1",
                    "task_detail": {
                        "TTS": "Task 1 initiated",
                        "vel": 1.0,
                        "LED": "red",
                        "LED_effect": "blink"
                    }
                },
                {
                    "task_id": "task_2",
                    "POI": "poi_2",
                    "task_detail": {
                        "TTS": "Task 2 initiated",
                        "vel": 1.2,
                        "LED": "blue",
                        "LED_effect": "steady"
                    }
                },
                {
                    "task_id": "task_3",
                    "POI": "poi_3",
                    "task_detail": {
                        "TTS": "Task 3 initiated",
                        "vel": 1.5,
                        "LED": "green",
                        "LED_effect": "off"
                    }
                }
            ],
            "global_condition": {
                "order": "sequential",
                "robot_pose": {"x": 0, "y": 0}
            },
            "goal_generated": True,
            "goal_verified": True
        }
    }

    # 1. goal.json을 받아 poi_dict 초기화
    poi_dict = task_manager.initialize_poi_dict(goal_json)
    
    # 2. poi_dict를 서버에 전송
    task_manager.send_poi_dict(poi_dict)
    
    service_id = goal_json["goal"]["service_id"]
    task_list = goal_json["goal"]["task_list"]

    # 6. POI 목록을 순회하며 작업 수행
    for task in task_list:
        poi = task['POI']

        if poi_dict[poi] == 'not_done':
            # 3. current_service_start 생성
            current_service_start = task_manager.create_current_service_start(service_id, task)
            
            # 4. current_service_start 서버 전송
            current_service_start_sent = task_manager.send_current_service_start(current_service_start)
            if current_service_start_sent:
                # 5. 전송 성공 시 poi_dict의 state를 'running'으로 변경
                task_manager.update_poi_state(poi, 'running')

            # 7. 작업 완료 여부 확인 및 상태 업데이트 (간단한 시뮬레이션)
            task_manager.listen_for_task_status()

    # 8. 모든 작업 완료 후 poi_dict 초기화
    if all(state == 'done' for state in poi_dict.values()):
        task_manager.reset_poi_dict()


# 사용 예시
if __name__ == "__main__":
    main()
