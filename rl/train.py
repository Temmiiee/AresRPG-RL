import argparse
from pathlib import Path
from sb3_contrib import MaskablePPO
from .env import AresFightEnv

p=argparse.ArgumentParser()
p.add_argument("--steps",type=int,default=100000)
p.add_argument("--out",default="models/ppo_ares")
a=p.parse_args()
env=AresFightEnv()
model=MaskablePPO("MlpPolicy",env,verbose=1,learning_rate=3e-4,n_steps=1024,
                  batch_size=256,gamma=.995,gae_lambda=.95,ent_coef=.01,
                  tensorboard_log="runs/",device="auto")
model.learn(total_timesteps=a.steps)
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
model.save(a.out)
env.close()
