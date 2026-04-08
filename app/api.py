"""
FinPilot AI — OpenEnv REST API
Exposes POST /reset, POST /step, GET /state for hackathon validator.
Runs alongside Streamlit on port 8000 (proxied via nginx or run separately).

The hackathon validator pings these endpoints to verify OpenEnv compliance.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Any
import uvicorn

from app.environment import FinPilotEnv
from app.graders import get_grader

app = FastAPI(
    title="FinPilot AI — OpenEnv API",
    description="Financial simulation environment implementing OpenEnv spec.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance (one per server — sufficient for validation)
_env: Optional[FinPilotEnv] = None
_task: str = "wealth_building"


# ─── Pydantic models ──────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task: str = Field(default="wealth_building",
                      description="Task name: budget_balance | debt_payoff | wealth_building")
    seed: Optional[int] = Field(default=42)
    currency: Optional[str] = Field(default="INR")
    language: Optional[str] = Field(default="English")


class ActionParams(BaseModel):
    amount: Optional[float] = Field(default=5000.0)
    fund_type: Optional[str] = Field(default="equity_index")
    category: Optional[str] = Field(default=None)
    new_amount: Optional[float] = Field(default=None)
    interest_rate: Optional[float] = Field(default=12.0)


class StepRequest(BaseModel):
    action_type: str = Field(
        description="save | invest_sip | repay_debt | build_emergency_fund | adjust_expenses | take_loan"
    )
    params: ActionParams = Field(default_factory=ActionParams)


class StepResponse(BaseModel):
    state: dict
    reward: float
    done: bool
    life_event: str
    ai_insights: dict


class StateResponse(BaseModel):
    state: dict
    task: str
    step_count: int


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", summary="Health check")
def root():
    """Health check — returns 200 if the server is running."""
    return {
        "status": "ok",
        "service": "FinPilot AI — OpenEnv Environment",
        "version": "1.0.0",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/docs"],
    }


@app.get("/health", summary="Health check alias")
def health():
    return {"status": "healthy", "environment_ready": _env is not None}


@app.post("/reset", summary="Reset environment to initial state")
def reset(body: ResetRequest = None):
    """
    Reset the environment to its initial state.
    Returns the initial observation/state.
    """
    global _env, _task

    if body is None:
        body = ResetRequest()

    _task = body.task
    _env  = FinPilotEnv(
        task=body.task,
        seed=body.seed,
        currency=body.currency or "INR",
        language=body.language or "English",
    )
    initial_state = _env.reset()

    return {
        "state":       initial_state,
        "task":        body.task,
        "max_steps":   _env.task_config["max_steps"],
        "description": _env.task_config["description"],
        "reset":       True,
    }


@app.post("/step", summary="Execute one simulation step", response_model=StepResponse)
def step(body: StepRequest):
    """
    Execute one month of financial simulation with the given action.
    Returns new state, reward [0.0-1.0], done flag, and life event.
    """
    global _env

    if _env is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialised. Call POST /reset first."
        )

    action = {
        "type":   body.action_type,
        "params": body.params.dict(exclude_none=True),
    }

    try:
        result = _env.step(action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")

    return StepResponse(
        state       = result["state"],
        reward      = round(result["reward"], 6),
        done        = result["done"],
        life_event  = result.get("life_event", "none"),
        ai_insights = result.get("ai_insights", {}),
    )


@app.get("/state", summary="Get current environment state", response_model=StateResponse)
def get_state():
    """
    Return the current environment state without advancing simulation.
    """
    global _env

    if _env is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialised. Call POST /reset first."
        )

    return StateResponse(
        state      = _env.state(),
        task       = _task,
        step_count = _env._step_count,
    )


@app.get("/tasks", summary="List all available tasks")
def list_tasks():
    """List all tasks with their configuration and grader info."""
    from app.environment import TASK_CONFIGS
    return {
        "tasks": [
            {
                "name":        name,
                "difficulty":  "easy" if name == "budget_balance" else
                               "medium" if name == "debt_payoff" else "hard",
                "max_steps":   cfg["max_steps"],
                "description": cfg["description"],
                "reward_range": [0.0, 1.0],
            }
            for name, cfg in TASK_CONFIGS.items()
        ]
    }


@app.post("/grade", summary="Grade current episode")
def grade():
    """Run grader on current state and return episode reward."""
    global _env, _task

    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialised.")

    grader     = get_grader(_task)
    state      = _env.state()
    history    = _env.history()
    ep_reward  = grader.episode_reward(state, history)
    success    = grader.is_success(state)
    summary    = grader.summary(state, history)

    return {
        "reward":           round(ep_reward, 6),
        "success":          success,
        "summary":          summary,
        "reward_range":     [0.0, 1.0],
        "steps_taken":      len(history),
    }


@app.get("/openenv.yaml", summary="Serve openenv.yaml spec")
def serve_openenv_yaml():
    """Serve the openenv.yaml specification file."""
    import yaml
    yaml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "openenv.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path) as f:
            content = yaml.safe_load(f)
        return content
    raise HTTPException(status_code=404, detail="openenv.yaml not found")


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("app.api:app", host="0.0.0.0", port=port, reload=False)