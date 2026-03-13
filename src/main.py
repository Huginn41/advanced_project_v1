import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/users/me")
async def get_info_me():
    return {
        "result": "true",
        "user": {
            "id": 1,
            "name": "Name Namenov",
            "following": [{"id": 2, "name": "Name2"}, {"id": 3, "name": "Name3"}],
            "followers": [{"id": 4, "name": "Name2"}, {"id": 5, "name": "Name3"}],
        },
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
