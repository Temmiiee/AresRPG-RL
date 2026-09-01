import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run directly with `python tools/benchmark.py`
from rl.env import AresFightEnv
p=argparse.ArgumentParser(); p.add_argument("--episodes",type=int,default=100); a=p.parse_args()
e=AresFightEnv(); wins=0
try:
    for i in range(a.episodes):
        e.reset(); done=trunc=False
        while not (done or trunc):
            legal=e.action_masks().nonzero()[0]
            _,_,done,trunc,_=e.step(int(legal[0]))
        wins+=int(e.state["winner"]==0)
finally: e.close()
print("winrate",wins/a.episodes)
