from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.modules.bot import CookieFoundry
from app.routes.app import router as cookie_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Gets Executed before FastAPI starts
    try:
        app.state.cookie_foundry = CookieFoundry()
    except Exception as e:
        print(
f"""
Cookie Foundry couldnt be built!
Error-Msg: {str(e)}
"""
)
    
    yield
    # Gets Executed after FastAPI quits

app = FastAPI(lifespan=lifespan)
app.include_router(cookie_router)

