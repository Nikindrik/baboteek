from baboteek_api import auth, compiler
from fastapi import FastAPI
import uvicorn
from baboteek_api.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(auth.router)
app.include_router(compiler.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
