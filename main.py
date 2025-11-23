from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is running")
    await init_db()
    yield
    print("Server is stopped")


app = FastAPI(title="ŞəfaTapp", lifespan=lifespan)


@app.get("/")
def root():
    return (
        "Salam Dostum Diyesen Sehv Yere giribsen. Buradan çıxmağınızı tövsiyə edirəm."
    )


app.include_router(api_router)
