

'''
DB: Dynamic DB []

(Flow)
카카오톡 유저 채팅
-> 카카오톡API로 전달
-> Dynamic DB 에서 유저마다 step state 확인
-> router에서 step state에 맞는 스크립트(step_n.py) 실행
-> step_n.py 실행
-> 다시 카카오톡API로 답변 전송

''' 

def main():

    # subscribe the STEP of user
    user_id, user_step = get.DBfrom~~
    
    # run followed step script




    return


if __name__ == '__main__':
    main()

