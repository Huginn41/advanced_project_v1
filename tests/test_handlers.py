
import pytest
from fastapi import HTTPException

from handlers import (
    create_tweet,
    delete_tweet,
    follow_user,
    get_feed,
    get_user_by_api_key,
    get_user_by_id,
    like_tweet,
    unfollow_user,
    unlike_tweet,
)


class TestGetUserByApiKey:

    async def test_returns_user_for_valid_key(self, session, users):

        user = await get_user_by_api_key("test", session)
        assert user.name == "Alice"

    async def test_raises_403_for_invalid_key(self, session, users):

        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_api_key("wrong_key", session)
        assert exc_info.value.status_code == 403


class TestGetUserById:

    async def test_returns_user_for_valid_id(self, session, users):
        alice = users["alice"]
        user = await get_user_by_id(alice.id, session)
        assert user.name == "Alice"

    async def test_raises_404_for_missing_id(self, session, users):

        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_id(99999, session)
        assert exc_info.value.status_code == 404


class TestCreateTweet:

    async def test_creates_tweet_and_returns_id(self, session, users):

        alice = users["alice"]
        tweet_id = await create_tweet(alice, "Hello world!", None, session)
        assert isinstance(tweet_id, int)
        assert tweet_id > 0

    async def test_tweet_appears_in_feed(self, session, users):

        alice = users["alice"]
        await create_tweet(alice, "Feed me!", None, session)
        feed = await get_feed(alice, session)
        contents = [t.content for t in feed]
        assert "Feed me!" in contents


class TestDeleteTweet:

    async def test_author_can_delete_own_tweet(self, session, users):

        alice = users["alice"]
        tweet_id = await create_tweet(alice, "Delete me", None, session)
        await delete_tweet(alice, tweet_id, session)

        feed = await get_feed(alice, session)
        contents = [t.content for t in feed]
        assert "Delete me" not in contents

    async def test_raises_404_for_missing_tweet(self, session, users):

        alice = users["alice"]
        with pytest.raises(HTTPException) as exc_info:
            await delete_tweet(alice, 99999, session)
        assert exc_info.value.status_code == 404

    async def test_raises_403_when_not_author(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        tweet_id = await create_tweet(alice, "Alice's tweet", None, session)

        with pytest.raises(HTTPException) as exc_info:
            await delete_tweet(bob, tweet_id, session)
        assert exc_info.value.status_code == 403


class TestLikes:

    async def test_can_like_tweet(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        tweet_id = await create_tweet(alice, "Like me", None, session)
        await like_tweet(bob, tweet_id, session)

    async def test_duplicate_like_raises_400(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        tweet_id = await create_tweet(alice, "Only once", None, session)
        await like_tweet(bob, tweet_id, session)

        with pytest.raises(HTTPException) as exc_info:
            await like_tweet(bob, tweet_id, session)
        assert exc_info.value.status_code == 400

    async def test_like_missing_tweet_raises_404(self, session, users):

        alice = users["alice"]
        with pytest.raises(HTTPException) as exc_info:
            await like_tweet(alice, 99999, session)
        assert exc_info.value.status_code == 404

    async def test_unlike_removes_like(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        tweet_id = await create_tweet(alice, "Unlike me", None, session)
        await like_tweet(bob, tweet_id, session)
        await unlike_tweet(bob, tweet_id, session)

    async def test_unlike_missing_like_raises_404(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        tweet_id = await create_tweet(alice, "No like here", None, session)

        with pytest.raises(HTTPException) as exc_info:
            await unlike_tweet(bob, tweet_id, session)
        assert exc_info.value.status_code == 404


class TestGetFeed:

    async def test_feed_sorted_by_likes_descending(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        charlie = users["charlie"]

        popular_id = await create_tweet(alice, "Popular", None, session)
        await create_tweet(alice, "Boring", None, session)


        await like_tweet(bob, popular_id, session)
        await like_tweet(charlie, popular_id, session)

        feed = await get_feed(alice, session)
        assert feed[0].content == "Popular"

    async def test_empty_feed_returns_empty_list(self, session, users):

        alice = users["alice"]
        feed = await get_feed(alice, session)
        assert feed == []


class TestFollows:

    async def test_can_follow_user(self, session, users):

        bob = users["bob"]
        charlie = users["charlie"]
        await follow_user(bob, charlie.id, session)

    async def test_cannot_follow_yourself(self, session, users):

        alice = users["alice"]
        with pytest.raises(HTTPException) as exc_info:
            await follow_user(alice, alice.id, session)
        assert exc_info.value.status_code == 400

    async def test_duplicate_follow_raises_400(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        with pytest.raises(HTTPException) as exc_info:
            await follow_user(alice, bob.id, session)
        assert exc_info.value.status_code == 400

    async def test_follow_missing_user_raises_404(self, session, users):

        alice = users["alice"]
        with pytest.raises(HTTPException) as exc_info:
            await follow_user(alice, 99999, session)
        assert exc_info.value.status_code == 404

    async def test_can_unfollow_user(self, session, users):

        alice = users["alice"]
        bob = users["bob"]
        await unfollow_user(alice, bob.id, session)

    async def test_unfollow_not_following_raises_404(self, session, users):

        bob = users["bob"]
        charlie = users["charlie"]
        with pytest.raises(HTTPException) as exc_info:
            await unfollow_user(bob, charlie.id, session)
        assert exc_info.value.status_code == 404