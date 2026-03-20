

from fastapi import APIRouter, Depends, Header, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from handlers import (
    build_user_profile,
    create_tweet,
    delete_tweet,
    follow_user,
    get_feed,
    get_user_by_api_key,
    get_user_by_id,
    like_tweet,
    unfollow_user,
    unlike_tweet,
    upload_media,
)
from models import User
from schemas.base import ResultResponse
from schemas.tweets import (
    MediaUploadResponse,
    TweetCreateRequest,
    TweetCreateResponse,
    TweetFeedResponse,
)
from schemas.users import UserResponse

router = APIRouter(prefix="/api")


async def current_user(
        api_key: str = Header(alias="api-key"),
        session: AsyncSession = Depends(get_session),
) -> User:

    return await get_user_by_api_key(api_key, session)


@router.get("/users/me", response_model=UserResponse)
async def get_me(user: User = Depends(current_user)) -> UserResponse:

    return UserResponse(user=build_user_profile(user))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_session),
) -> UserResponse:

    user = await get_user_by_id(user_id, session)
    return UserResponse(user=build_user_profile(user))


@router.post("/users/{user_id}/follow", response_model=ResultResponse)
async def follow(
        user_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> ResultResponse:

    await follow_user(user, user_id, session)
    return ResultResponse()


@router.delete("/users/{user_id}/follow", response_model=ResultResponse)
async def unfollow(
        user_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> ResultResponse:

    await unfollow_user(user, user_id, session)
    return ResultResponse()


@router.get("/tweets", response_model=TweetFeedResponse)
async def get_tweets(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> TweetFeedResponse:

    tweets = await get_feed(user, session)
    return TweetFeedResponse(tweets=tweets)


@router.post("/tweets", response_model=TweetCreateResponse)
async def post_tweet(
        body: TweetCreateRequest,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> TweetCreateResponse:

    tweet_id = await create_tweet(user, body.tweet_data, body.tweet_media_ids, session)
    return TweetCreateResponse(tweet_id=tweet_id)


@router.delete("/tweets/{tweet_id}", response_model=ResultResponse)
async def remove_tweet(
        tweet_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> ResultResponse:

    await delete_tweet(user, tweet_id, session)
    return ResultResponse()


@router.post("/tweets/{tweet_id}/likes", response_model=ResultResponse)
async def add_like(
        tweet_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> ResultResponse:

    await like_tweet(user, tweet_id, session)
    return ResultResponse()


@router.delete("/tweets/{tweet_id}/likes", response_model=ResultResponse)
async def remove_like(
        tweet_id: int,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> ResultResponse:

    await unlike_tweet(user, tweet_id, session)
    return ResultResponse()


@router.post("/medias", response_model=MediaUploadResponse)
async def post_media(
        file: UploadFile = File(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_session),
) -> MediaUploadResponse:

    media_id = await upload_media(file, session)
    return MediaUploadResponse(media_id=media_id)
