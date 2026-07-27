from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.modules.bot import CookieFoundry
from app.routes.app import router as cookie_router
from fastapi.middleware.cors import CORSMiddleware


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cookie_router)

