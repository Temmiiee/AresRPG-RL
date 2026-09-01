"""
Quick smoke test: start bridge, ping, reset and perform a single step.
Run from the repo root with ARES_RPG_ROOT set to the repo root (or rely on default).
"""
import os
from rl.bridge import AresBridge


def main():
    root = os.environ.get("ARES_RPG_ROOT", ".")
    print("Starting AresBridge (root=%s)..." % root)
    bridge = AresBridge(root=root, runtime_hint="bun")
    try:
        print("Ping ->", bridge.request({"op": "ping"}))
        print("Reset ->", bridge.request({"op": "reset", "seed": 1234}))
        # attempt a single step with a no-op action if supported (adjust if your bridge expects different action)
        step_req = {"op": "step", "action": {"type": "end_turn", "fighter": 0}}
        print("Step ->", bridge.request(step_req, timeout=10.0))
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
