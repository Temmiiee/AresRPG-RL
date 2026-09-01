import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .bridge import AresBridge
from .scenarios import ScenarioGenerator

class AresFightEnv(gym.Env):
    MAX_ACTIONS=4096
    OBS_SIZE=256
    def __init__(self,seed=12345):
        super().__init__(); self.bridge=AresBridge(); self.gen=ScenarioGenerator(seed)
        self.observation_space=spaces.Box(-1,1,(self.OBS_SIZE,),dtype=np.float32)
        self.action_space=spaces.Discrete(self.MAX_ACTIONS)
    def _obs(self,s):
        x=np.zeros(self.OBS_SIZE,dtype=np.float32); k=0
        for f in s["fighters"][:16]:
            for v in (f["team"],f["level"]/100,f["cell"]/196,
                      f["hp"]/max(1,f["hp"]+1),f["ap"]/20,f["mp"]/10,float(f["dead"]),
                      f["effects"]/10,f["cooldowns"]/10):
                if k<self.OBS_SIZE: x[k]=np.clip(float(v)*2-1,-1,1); k+=1
        if k<self.OBS_SIZE: x[k]=np.clip(s["round"]/100*2-1,-1,1); k+=1
        return x
    def _mask(self):
        m=np.zeros(self.MAX_ACTIONS,dtype=bool); m[:min(len(self.actions),self.MAX_ACTIONS)]=True; return m
    def reset(self,seed=None,options=None):
        super().reset(seed=seed)
        r=self.bridge.request({"op":"reset","setup":self.gen.setup(),
                               "seed":int(self.np_random.integers(1,2**31))})
        if not r["ok"]: raise RuntimeError(r)
        self.state=r["state"]; self.actions=r["actions"]
        return self._obs(self.state),{}
    def step(self,a):
        if a>=len(self.actions):
            return self._obs(self.state),-2,False,False,{"invalid":True}
        r=self.bridge.request({"op":"step","action":self.actions[a]})
        if not r["ok"]:
            self.state=r["state"]; self.actions=r["actions"]
            return self._obs(self.state),-2,False,False,{"invalid":True}
        self.state=r["state"]; self.actions=r["actions"]
        reward=0.
        for e in r.get("events",[]):
            p=e.get("payload",{})
            if e["type"]=="damage_number":
                reward += (float(p.get("amount",0))/100
                           if p.get("target",-1)>=4 and p.get("source",-1)<4
                           else -float(p.get("amount",0))/150)
            elif e["type"]=="fighter_died":
                reward += 2 if p.get("fighter",-1)>=4 else -3
        done=bool(self.state["ended"])
        if done: reward += 100 if self.state["winner"]==0 else -100
        return self._obs(self.state),reward,done,False,{"action":self.actions[a]}
    def action_masks(self): return self._mask()
    def close(self): self.bridge.close()
