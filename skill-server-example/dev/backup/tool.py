from cachetools import Cache, LRUCache


class UserCache(LRUCache):
    def __init__(self, maxsize, condition_function = False): ## 컨디션 설정해야함
        super().__init__(maxsize)
        self.condition_function = condition_function

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.check_condition()

    def check_condition(self):
        # 특정 조건이 만족되면 메모리에서 캐시 항목 제거 로직 추가
        if self.condition_function():
            # 예: 캐시 비우기
            self.clear()
            
class UserCacheManager:
    def __init__(self):
        self.user_caches = {}  # 사용자 ID에 대한 UserCache 인스턴스를 저장하는 딕셔너리

    def get_user_cache(self, user_id):
        # 주어진 사용자 ID에 대한 UserCache 인스턴스를 가져오거나 생성
        if user_id not in self.user_caches:
            self.user_caches[user_id] = UserCache(maxsize=100)
        return self.user_caches[user_id]
