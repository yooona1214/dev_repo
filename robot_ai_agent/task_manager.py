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
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


class TaskManager:
    # 모든 robot_id에 대한 TaskManager 인스턴스를 관리하는 딕셔너리
    _instances = {}
    
    def __init__(self, robot_id):
        """
        TaskManager 클래스 초기화.
        :param robot_id: 로봇의 ID (인스턴스 생성 시 사용)
        """
        self.robot_id = robot_id
        self.poi_state_dict = {}  # POI별 상태 관리 딕셔너리
        self.current_service_start = None  # 현재 시작할 서비스 정보
        self.current_goal_json = {}
        
    @classmethod
    def get_instance(cls, robot_id):
        """
        주어진 robot_id에 대한 TaskManager 인스턴스를 반환합니다.
        :param robot_id: 로봇의 ID
        :return: TaskManager 인스턴스
        """
        if robot_id not in cls._instances:
            # 새로운 인스턴스 생성 후 딕셔너리에 저장
            cls._instances[robot_id] = TaskManager(robot_id)
        return cls._instances[robot_id]
        
    

    def generate_goal_json(self, poi_arg_list):
        """
        주어진 POI 리스트를 사용하여 goal.json 형식의 딕셔너리를 생성합니다.
        :param poi_arg_list: 각 POI 이름과 해당 설정값을 포함하는 리스트, 형식: [[poi_name, service_id], ...]
        :return: goal.json 형식의 딕셔너리
        """
        csv_file_path = './robot_info/floor_description.csv'
        df = pd.read_csv(csv_file_path)
        
        
        goal_json = {}
        for poi_sublist in poi_arg_list:
            print(poi_sublist)
            poi_name, poi_arg1, poi_arg2, poi_arg3 = poi_sublist
            
            # csv에서 실제 poi 가져오기
            key_to_find = poi_name
            matching_row = df[df['Name'] == key_to_find]
            id_value = matching_row.iloc[0]['ID']
            map_id = matching_row.iloc[0]['Map_id']
            
            # led bgm effect
            poi_arg = poi_arg1 + poi_arg2 + poi_arg3
            
            # 각 POI를 키로 하고, 해당 POI에 대한 설정값을 포함하는 딕셔너리를 생성
            goal_json[poi_name] = {
                "service_id": poi_arg,  # POI에 대한 서비스 ID
                "goal_count": 1,  # 기본 goal_count는 1로 설정
                "task_list": [
                    {
                        "service_code": 103,  # 주어진 service_code
                        "task_id": 1,  # speed scale 인데 어떻게?
                        "tray_id": 1,  # 트레이 위치 tray_id는 기본적으로 1로 설정
                        "map_id": map_id,  # map_id 어떻게?
                        "goal_id": id_value,  # goal_id는 현재 POI 이름으로 설정
                        "seq": 0,  # seq는 기본적으로 1로 설정
                        "lock_option": 1  # lock_option은 기본적으로 1로 설정
                    }
                ]
            }
                
        # 현재 시간 기반 파일명 생성
        current_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"goal_{current_time_str}.json"

        # 파일 경로 생성
        folder_name = "data/"
        file_path = os.path.join(folder_name, file_name)

        # JSON 데이터를 파일에 저장
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(goal_json, f, ensure_ascii=False, indent=4)

        print(f"JSON 데이터가 '{file_path}' 파일로 저장되었습니다.")  

        return goal_json
    
    def initialize_poi_state_dict(self, goal_json):
        """
        goal.json 데이터를 기반으로 poi_state_dict를 생성합니다.
        각 POI의 상태는 'not_done'으로 초기화됩니다.
        
        :param goal_json: goal.json 형식의 딕셔너리 데이터
        :return: POI 상태를 나타내는 poi_state_dict 딕셔너리
        """
        self.current_goal_json = goal_json
        
        # POI 상태 딕셔너리 초기화
        self.poi_state_dict = {poi_name: 'not_done' for poi_name in goal_json.keys()}
        print("\n\n\n\n")
        print("*******************************")
        print("TASK MANAGER POI STATE is INITIALIZED: \n", self.poi_state_dict)
        print("*******************************")
        print("\n\n\n\n")
        
        
    def find_current_poi(self):
        # state_dict 에서 값이 not_done인 제일 첫번째 key 뽑기
        for key, value in self.poi_state_dict.items():
            if value == 'not_done':
                return key
        return None  

        
        
    def load_current_service_start(self, current_poi):
        """로봇 -> 서버 : current_service_start 전송 후 성공 여부 반환"""

        current_poi_ccs = self.current_goal_json[current_poi]
        
        return current_poi_ccs


    def update_poi_state_dict(self, poi, state):
        """poi_state_dict의 특정 POI의 상태를 업데이트 후 상태 반환"""
        if poi in self.poi_state_dict:
            self.poi_state_dict[poi] = state
            print("*******************************")
            print("TASK MANAGER POI STATE is UPDATED: \n")
            print(f"POI '{poi}' 상태 업데이트: {state}")   
            print(self.poi_state_dict)  
            print("*******************************")
            return self.poi_state_dict
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
                self.update_poi_state_dict(poi, 'done')
            return task_status
        else:
            print("Task Status 수신 실패:", response.status_code)
            return None

    def reset_poi_state_dict(self):
        """poi_state_dict 초기화 후 초기화된 딕셔너리 반환"""
        self.poi_state_dict = {}
        print("POI Dict 초기화 완료")
        return self.poi_state_dict


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

    # 1. goal.json을 받아 poi_state_dict 초기화
    poi_state_dict = task_manager.initialize_poi_state_dict(goal_json)
    

    service_id = goal_json["goal"]["service_id"]
    task_list = goal_json["goal"]["task_list"]

    # 6. POI 목록을 순회하며 작업 수행
    for task in task_list:
        poi = task['POI']

        if poi_state_dict[poi] == 'not_done':
            # 3. current_service_start 생성
            current_service_start = task_manager.create_current_service_start(service_id, task)
            
            # 4. current_service_start 서버 전송
            current_service_start_sent = task_manager.send_current_service_start(current_service_start)
            if current_service_start_sent:
                # 5. 전송 성공 시 poi_state_dict state를 'running'으로 변경
                task_manager.update_poi_state_dict(poi, 'running')

            # 7. 작업 완료 여부 확인 및 상태 업데이트 (간단한 시뮬레이션)
            task_manager.listen_for_task_status()

    # 8. 모든 작업 완료 후 poi_state_dict 초기화
    if all(state == 'done' for state in poi_state_dict.values()):
        task_manager.reset_poi_state_dict()


# 사용 예시
if __name__ == "__main__":
    main()
