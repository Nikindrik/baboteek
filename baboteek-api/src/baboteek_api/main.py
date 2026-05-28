from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from baboteek_api import auth, compiler
from baboteek_api.config import settings
from baboteek_api.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth.router)
app.include_router(compiler.router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
