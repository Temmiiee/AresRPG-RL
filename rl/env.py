import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .bridge import AresBridge
from .scenarios import ScenarioGenerator

def _int(v):
    """Event payload numbers arrive as bigint-suffixed strings (e.g. '4n'), unlike the
    already-Number()-converted fighter/state fields in summary()."""
    return int(v[:-1]) if isinstance(v, str) and v.endswith("n") else int(v)

class AresFightEnv(gym.Env):
    MAX_ACTIONS=4096
    OBS_SIZE=256
    MAX_FIGHTERS=8       # scenarios.py always builds 4 players + up to 4 mobs
    MAX_AP=12
    MAX_MP=6
    MAX_EPISODE_STEPS=1000
    def __init__(self,seed=12345):
        super().__init__(); self.bridge=AresBridge(); self.gen=ScenarioGenerator(seed)
        self.observation_space=spaces.Box(-1,1,(self.OBS_SIZE,),dtype=np.float32)
        self.action_space=spaces.Discrete(self.MAX_ACTIONS)
    def _obs(self,s):
        x=np.zeros(self.OBS_SIZE,dtype=np.float32); k=0
        board=s["board"]; turn=s["turn"]
        for f in s["fighters"][:self.MAX_FIGHTERS]:
            for v in (f["team"],float(f["id"]==turn),f["level"]/100,
                      (f["cell"]%board["grid_w"])/board["grid_w"],
                      (f["cell"]//board["grid_w"])/board["grid_h"],
                      f["hp"]/max(1,f["max_hp"]),f["ap"]/self.MAX_AP,f["mp"]/self.MAX_MP,
                      float(f["dead"]),f["effects"]/10,f["cooldowns"]/10):
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
        self._steps=0; self._dmg_dealt=0.; self._dmg_taken=0.; self._kills=0; self._deaths=0
        return self._obs(self.state),{}
    def step(self,a):
        if a>=len(self.actions):
            return self._obs(self.state),-2,False,False,{"invalid":True}
        chosen=self.actions[a]
        r=self.bridge.request({"op":"step","action":chosen})
        if not r["ok"]:
            self.state=r["state"]; self.actions=r["actions"]
            return self._obs(self.state),-2,False,False,{"invalid":True}
        self.state=r["state"]; self.actions=r["actions"]
        self._steps+=1
        reward=0.
        for e in r.get("events",[]):
            p=e.get("payload",{})
            if e["type"]=="damage_number":
                target,source,amount=_int(p.get("target",-1)),_int(p.get("source",-1)),_int(p.get("amount",0))
                ally_hit=target<4
                if ally_hit: self._dmg_taken+=amount
                else: self._dmg_dealt+=amount
                reward += -amount/150 if ally_hit else amount/100
            elif e["type"]=="fighter_died":
                fighter=_int(p.get("fighter",-1))
                if fighter>=4: self._kills+=1; reward+=2
                else: self._deaths+=1; reward-=3
        won=bool(self.state["ended"]) and self.state["winner"]==0
        done=bool(self.state["ended"])
        truncated=(not done) and self._steps>=self.MAX_EPISODE_STEPS
        if done: reward += 100 if won else -100
        info={"action":chosen}
        if done or truncated:
            info.update(win=int(won),damage_dealt=self._dmg_dealt,damage_taken=self._dmg_taken,
                        kills=self._kills,deaths=self._deaths,rounds=self.state["round"])
        return self._obs(self.state),reward,done,truncated,info
    def action_masks(self): return self._mask()
    def set_difficulty(self,d): self.gen.set_difficulty(d)
    def close(self): self.bridge.close()
