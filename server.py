from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# 🔥 MAIN FIX (Hackathon required)
@app.post("/openenv/reset")
def openenv_reset():
    try:
        from inference import run_episode
        reward = run_episode()
        return {"status": "success", "reward": reward}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# optional
@app.post("/openenv/reset")
def openenv_reset():
    from inference import run_episode
    reward = run_episode()
    return {"status": "success", "reward": reward}