from typing import List, Optional

from schemas.base import Base, ResultResponse
from schemas.users import UserShort


class LikeInfo(Base):
    user_id: int
    name: str


class TweetOut(Base):
    id: int
    content: str
    attachments: List[str]
    author: UserShort
    likes: List[LikeInfo]


class TweetFeedResponse(ResultResponse):
    tweets: List[TweetOut]


class TweetCreateRequest(Base):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class TweetCreateResponse(ResultResponse):
    tweet_id: int


class MediaUploadResponse(ResultResponse):
    media_id: int
