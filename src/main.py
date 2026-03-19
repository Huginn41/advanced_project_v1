import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import init_models
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield


app = FastAPI(
    title="Twitter Clone API",
    description="Microblogging service API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
