class TestGetMe:

    async def test_returns_200_with_valid_api_key(self, client):
        response = await client.get("/api/users/me", headers={"api-key": "test"})
        assert response.status_code == 200

    async def test_response_contains_user_data(self, client):
        response = await client.get("/api/users/me", headers={"api-key": "test"})
        data = response.json()
        assert data["result"] is True
        assert data["user"]["name"] == "Alice"

    async def test_returns_403_without_api_key(self, client):
        response = await client.get("/api/users/me")
        assert response.status_code in (403, 422)

    async def test_returns_403_with_wrong_api_key(self, client):
        response = await client.get("/api/users/me", headers={"api-key": "wrong"})
        assert response.status_code == 403


class TestTweetEndpoints:

    async def test_create_tweet_returns_201_or_200(self, client):
        response = await client.post(
            "/api/tweets",
            json={"tweet_data": "Hello from test!"},
            headers={"api-key": "test"},
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert "tweet_id" in data
        assert isinstance(data["tweet_id"], int)

    async def test_get_feed_returns_list(self, client):
        await client.post(
            "/api/tweets",
            json={"tweet_data": "Feed test"},
            headers={"api-key": "test"},
        )
        response = await client.get("/api/tweets", headers={"api-key": "test"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tweets"], list)

    async def test_delete_own_tweet(self, client):
        create_resp = await client.post(
            "/api/tweets",
            json={"tweet_data": "Delete me"},
            headers={"api-key": "test"},
        )
        tweet_id = create_resp.json()["tweet_id"]

        delete_resp = await client.delete(
            f"/api/tweets/{tweet_id}",
            headers={"api-key": "test"},
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["result"] is True

    async def test_delete_missing_tweet_returns_404(self, client):
        response = await client.delete(
            "/api/tweets/99999",
            headers={"api-key": "test"},
        )
        assert response.status_code == 404


class TestLikeEndpoints:

    async def test_like_and_unlike_tweet(self, client):
        create_resp = await client.post(
            "/api/tweets",
            json={"tweet_data": "Like me"},
            headers={"api-key": "test"},
        )
        tweet_id = create_resp.json()["tweet_id"]

        like_resp = await client.post(
            f"/api/tweets/{tweet_id}/likes",
            headers={"api-key": "test"},
        )
        assert like_resp.status_code == 200

        unlike_resp = await client.delete(
            f"/api/tweets/{tweet_id}/likes",
            headers={"api-key": "test"},
        )
        assert unlike_resp.status_code == 200
