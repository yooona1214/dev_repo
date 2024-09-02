from pydantic import BaseModel
from typing import Dict, List, Optional
from cachetools import Cache, LRUCache

class KakaoUser(BaseModel):
    id: str
    properties: Dict
    type: str


class KakaoUserRequest(BaseModel):
    block: Dict
    lang: Optional[str]
    params: Dict
    timezone: str
    user: KakaoUser
    utterance: str


class KakaoAction(BaseModel):
    clientExtra: Optional[Dict]
    detailParams: Dict
    id: str
    name: str
    params: Dict


class KakaoAPI(BaseModel):
    """Main Kakao JSON"""

    action: KakaoAction
    bot: Dict
    contexts: Optional[List]
    intent: Dict
    userRequest: KakaoUserRequest


class IssueClassificationResult(BaseModel):
    category: str
