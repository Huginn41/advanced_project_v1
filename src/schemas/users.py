

from typing import List

from schemas.base import Base, ResultResponse


class UserShort(Base):

    id: int
    name: str


class UserProfile(Base):

    id: int
    name: str
    followers: List[UserShort]
    following: List[UserShort]


class UserResponse(ResultResponse):

    user: UserProfile
