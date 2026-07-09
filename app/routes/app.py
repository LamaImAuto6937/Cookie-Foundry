from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/cookies")
def get_cookies(request: Request):
    return {"cookies": request.app.state.cookie_foundry.get_cookies()}

@router.get("/clicker/start")
def start_clicker(request: Request):
    request.app.state.cookie_foundry.start_mode("auto_clicker", request.app.state.cookie_foundry.auto_clicker, 60)
    return {"status" : "started"}

@router.get("/clicker/stop")
def stop_clicker(request: Request):
    request.app.state.cookie_foundry.stop_mode("auto_clicker")
    return {"status" : "stopped"}

@router.post("/shimmer/start")
def start_shimmer(request: Request, delay: float = 2):
    request.app.state.cookie_foundry.start_mode("golden_cookie_watcher", request.app.state.cookie_foundry.golden_cookie_watcher, delay / 1000)
    return {"status": "started"}

@router.post("/shimmer/stop")
def stop_shimmer(request: Request):
    request.app.state.cookie_foundry.stop_mode("golden_cookie_watcher")
    return {"status": "stopped"}

@router.get("/ping")
def say_pong():
    return {"status": "pong"}