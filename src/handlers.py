import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Like, Media, Subs, Tweet, User
from schemas.tweets import LikeInfo, TweetOut
from schemas.users import UserProfile, UserShort


def build_user_profile(user: User) -> UserProfile:
    followers = [
        UserShort(id=sub.follower.id, name=sub.follower.name)
        for sub in user.followers
    ]
    following = [
        UserShort(id=sub.following.id, name=sub.following.name)
        for sub in user.followings
    ]
    return UserProfile(id=user.id, name=user.name, followers=followers, following=following)


def build_tweet_out(tweet: Tweet) -> TweetOut:
    return TweetOut(
        id=tweet.id,
        content=tweet.content,
        attachments=[media.name for media in tweet.attachments],
        author=UserShort(id=tweet.author.id, name=tweet.author.name),
        likes=[
            LikeInfo(user_id=like.user_id, name=like.author.name)
            for like in tweet.likes
        ],
    )


def _user_options():
    return [
        selectinload(User.followers).selectinload(Subs.follower),
        selectinload(User.followings).selectinload(Subs.following),
    ]


async def get_user_by_api_key(api_key: str, session: AsyncSession) -> User:
    result = await session.execute(
        select(User).where(User.api_key == api_key).options(*_user_options())
    )
    user = result.unique().scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return user


async def get_user_by_id(user_id: int, session: AsyncSession) -> User:
    result = await session.execute(
        select(User).where(User.id == user_id).options(*_user_options())
    )
    user = result.unique().scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def create_tweet(
        user: User,
        tweet_data: str,
        media_ids: list[int] | None,
        session: AsyncSession,
) -> int:
    tweet = Tweet(content=tweet_data, author_id=user.id)
    session.add(tweet)
    await session.flush()

    if media_ids:
        medias = await session.execute(
            select(Media).where(Media.id.in_(media_ids))
        )
        for media in medias.scalars().unique().all():
            media.tweet_id = tweet.id

    await session.commit()
    return tweet.id


async def delete_tweet(user: User, tweet_id: int, session: AsyncSession) -> None:
    result = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
    tweet = result.unique().scalar_one_or_none()
    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")
    if tweet.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not your tweet")
    await session.delete(tweet)
    await session.commit()


async def get_feed(user: User, session: AsyncSession) -> list[TweetOut]:
    result = await session.execute(select(Tweet))
    tweets = list(result.scalars().unique().all())
    tweets.sort(key=lambda t: len(t.likes), reverse=True)
    return [build_tweet_out(t) for t in tweets]


async def like_tweet(user: User, tweet_id: int, session: AsyncSession) -> None:
    tweet = await session.get(Tweet, tweet_id)
    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    existing = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already liked")

    session.add(Like(tweet_id=tweet_id, user_id=user.id))
    await session.commit()


async def unlike_tweet(user: User, tweet_id: int, session: AsyncSession) -> None:
    result = await session.execute(
        select(Like).where(Like.tweet_id == tweet_id, Like.user_id == user.id)
    )
    like = result.scalar_one_or_none()
    if like is None:
        raise HTTPException(status_code=404, detail="Like not found")
    await session.delete(like)
    await session.commit()


async def follow_user(user: User, target_id: int, session: AsyncSession) -> None:
    if user.id == target_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target = await session.get(User, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await session.execute(
        select(Subs).where(Subs.follower_id == user.id, Subs.following_id == target_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already following")

    session.add(Subs(follower_id=user.id, following_id=target_id))
    await session.commit()


async def unfollow_user(user: User, target_id: int, session: AsyncSession) -> None:
    result = await session.execute(
        select(Subs).where(Subs.follower_id == user.id, Subs.following_id == target_id)
    )
    sub = result.scalar_one_or_none()
    if sub is None:
        raise HTTPException(status_code=404, detail="Not following")
    await session.delete(sub)
    await session.commit()


UPLOAD_DIR = Path("/home/static/images")


async def upload_media(file: UploadFile, session: AsyncSession) -> int:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix if file.filename else ""
    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(await file.read())

    media = Media(name=f"/images/{filename}")
    session.add(media)
    await session.commit()
    return media.id
