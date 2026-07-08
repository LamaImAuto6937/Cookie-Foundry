from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/cookies")
def get_cookies(request: Request):
    return {"cookies": request.app.state.cookie_foundry.get_cookies()}

@router.get("/ping")
def say_pong():
    return {"status": "pong"}