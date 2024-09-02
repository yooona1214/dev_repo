from semantic_router.encoders import OpenAIEncoder
from semantic_router import Route
from semantic_router.layer import RouteLayer

# Router
general_chat = Route(
    name="general_chat",
    utterances=[
        "how's the weather today?",
        "how are things going?",
        "lovely weather today",
        "the weather is horrendous",
        "넌 누구니",
        "넌 무슨 로봇이야",
        "일반적인 대화",
        "안녕",
        "점심식사는 맛있게 했니?",
    ],
)

robot_data = Route(
    name="robot_data",
    utterances=[
        "안내로봇에 관련된 질문",
        "작품소개에 관한 질문",
        "로봇 기능에 관한 질문",
        "로봇 서비스 요청에 관련된 질문",
        "로봇 매뉴얼에 관한 질의",
        "로봇 고장 신고 문의",
        "1층에 있는 작품들을 설명해줘",
        "이 건물에 있는 작품들을 소개해줘",
        "내 로봇이 동작을 안해",
        "로봇이 충전이 안돼",
        "로봇이 멈춰",
    ],
)

routes = [general_chat, robot_data]


class Router:
    def __init__(self, encoder):
        self.rl = RouteLayer(encoder=encoder, routes=routes)

    def route(self, user_input):
        if user_input == "!다시":
            self.force_robot_control = False

        # 유저 입력을 인코딩하고 적절한 라우트를 선택
        route = self.rl(user_input).name

        return route
