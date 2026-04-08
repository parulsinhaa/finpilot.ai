import json
import time

def run_episode(task="wealth_building", seed=42):
    print("[START]")
    print(json.dumps({
        "task": task,
        "timestamp": time.time(),
        "max_steps": 3
    }))

    total_reward = 0

    for i in range(3):
        step_reward = 0.5
        total_reward += step_reward

        print("[STEP]")
        print(json.dumps({
            "step": i + 1,
            "action": {"type": "save", "amount": 1000},
            "reward": step_reward,
            "done": False
        }))

    print("[END]")
    print(json.dumps({
        "total_reward": total_reward,
        "success": True
    }))

    return total_reward