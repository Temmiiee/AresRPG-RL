import argparse, importlib.util
from pathlib import Path
from sb3_contrib import MaskablePPO
from stable_baselines3.common.monitor import Monitor
from .env import AresFightEnv

p=argparse.ArgumentParser()
p.add_argument("--steps",type=int,default=100000)
p.add_argument("--out",default="models/ppo_ares")
p.add_argument("--resume",default=None,help="path to an existing .zip checkpoint to continue training from")
p.add_argument("--log",default="runs/monitor.csv",help="per-episode stats CSV, read by tools/dashboard.py")
a=p.parse_args()
Path(a.log).parent.mkdir(parents=True,exist_ok=True)
env=Monitor(AresFightEnv(),filename=a.log,override_existing=not a.resume,
           info_keywords=("win","damage_dealt","damage_taken","kills","deaths","rounds"))
# tensorboard is not in requirements.txt (see ROADMAP.md: optional logging) — degrade
# to no logging instead of crashing when it isn't installed.
tb_log = "runs/" if importlib.util.find_spec("tensorboard") else None
if a.resume:
    model=MaskablePPO.load(a.resume,env=env,tensorboard_log=tb_log,device="auto")
else:
    model=MaskablePPO("MlpPolicy",env,verbose=1,learning_rate=3e-4,n_steps=1024,
                      batch_size=256,gamma=.995,gae_lambda=.95,ent_coef=.01,
                      tensorboard_log=tb_log,device="auto")
model.learn(total_timesteps=a.steps,reset_num_timesteps=a.resume is None)
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
model.save(a.out)
env.close()
