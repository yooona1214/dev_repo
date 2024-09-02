import socket


# TCP Socket Module
class BotServer:
    def __init__(self, srv_port, listen_num): 
        
        # 소켓 포트 번호
        self.port = srv_port 
        # 동시 접속 클라이언트 수
        self.listen = listen_num
        self.mySock = None
    

    # TCP/IP 소켓 생성, 지정 서버 포트로 설정한 수만큼 클라이언트 연결 수락
    def create_socket(self):
        
        self.mySock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 소켓 닫아도 바로 사용가능하게 설정
        self.mySock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mySock.bind(("0.0.0.0", int(self.port)))
        self.mySock.listen(int(self.listen))

        return self.mySock
    
    # 챗봇 client 연결 대기 및 수락
    def ready_for_client(self):
        return self.mySock.accept()
    
    # 현재 생성된 서버 소켓 반환
    def get_sock(self):
        return self.mySock