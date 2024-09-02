import redis
import psycopg2
import json
from datetime import datetime

class DBManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.db_config = {
            'dbname': 'postgres',  # 기본 데이터베이스로 연결하기 위해 postgres 설정
            'user': 'postgres',
            'password': 'rbrain!',
            'host': 'localhost'
        }
        self.target_db = 'raa_db'  # 실제 사용할 데이터베이스 이름
        self.filtered_turns = None

    def add_turn(self, session_id, user_text, agent_text, agent_id):
        turn = {
            "user": user_text,
            "agent": agent_text,
            "agent_id": agent_id,
            "timestamp": str(datetime.now())
        }
        self.redis_client.rpush(session_id, json.dumps(turn))  # 세션 ID를 키로 사용하여 리스트에 추가

    def get_session_id(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")
    
    def clear_redis_cache(self):
        """Redis 데이터베이스를 비우는 함수"""
        self.save_conversations_to_postgresql()
        self.redis_client.flushdb()
        print("Redis 캐시가 비워졌습니다.")

    def create_database_if_not_exists(self):
        """PostgreSQL 데이터베이스가 존재하지 않으면 생성하는 함수"""
        conn = None
        cursor = None
        try:
            # 기본 데이터베이스로 연결
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True  # 데이터베이스 생성 쿼리 실행을 위해 자동 커밋 설정
            cursor = conn.cursor()
            
            # 데이터베이스 생성 쿼리
            cursor.execute("""
                SELECT 1 FROM pg_database WHERE datname = %s
            """, (self.target_db,))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.target_db}")
                print(f"데이터베이스 '{self.target_db}'가 생성되었습니다.")
            else:
                print(f"데이터베이스 '{self.target_db}'가 이미 존재합니다.")

        except psycopg2.Error as err:
            print(f"PostgreSQL Error: {err}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Error closing cursor: {e}")
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")

    def save_conversations_to_postgresql(self):
        """Redis 데이터베이스의 대화 내용을 PostgreSQL에 저장하는 함수"""
        conn = None
        cursor = None
        try:
            # 데이터베이스가 존재하지 않을 경우 생성
            self.create_database_if_not_exists()
            
            # PostgreSQL 연결 (생성된 데이터베이스로 연결)
            self.db_config['dbname'] = self.target_db  # 실제 사용할 데이터베이스로 변경
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # 대화 테이블이 존재하지 않으면 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    user_input TEXT,
                    agent_response TEXT,
                    agent_id VARCHAR(255),
                    timestamp TIMESTAMP
                )
            """)

            # 모든 세션 ID 가져오기
            session_ids = self.redis_client.keys()

            for session_id in session_ids:
                session_id_str = session_id.decode('utf-8')
                all_turns = self.redis_client.lrange(session_id, 0, -1)

                for turn in all_turns:
                    turn_data = json.loads(turn)
                    cursor.execute("""
                        INSERT INTO conversations (session_id, user_input, agent_response, agent_id, timestamp)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (session_id_str, turn_data['user'], turn_data['agent'], turn_data['agent_id'], turn_data['timestamp']))

            conn.commit()
            print("Redis 데이터가 PostgreSQL에 저장되었습니다.")

        except psycopg2.Error as err:
            print(f"PostgreSQL Error: {err}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Error closing cursor: {e}")
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")
                    
    def get_conversation_history(self, session_id, agent_id_filter):
        """특정 세션과 에이전트 ID에 해당하는 대화 히스토리를 가져오는 함수"""
        all_turns = self.redis_client.lrange(session_id, 0, -1)
        filtered_turns = []
        for turn in all_turns:
            turn_data = json.loads(turn)
            if turn_data['agent_id'] == agent_id_filter:
                filtered_turns.append(turn_data)
        self.filtered_turns = filtered_turns
        return filtered_turns
    
