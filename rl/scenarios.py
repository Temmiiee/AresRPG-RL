import json, random
from pathlib import Path

class ScenarioGenerator:
    def __init__(self, seed=12345):
        self.r=random.Random(seed)
        p=Path(__file__).resolve().parents[1]/"data"/"archetypes.json"
        self.d=json.loads(p.read_text())
    def setup(self):
        classes=self.r.sample(self.d["classes"],4)
        base=self.r.randint(10,60)
        levels=[max(1,base+self.r.randint(-20,20)) for _ in range(4)]
        team_total=sum(levels)
        ratio=self.r.uniform(.90,1.25)
        total=max(4,round(team_total*ratio))
        n=self.r.randint(1,4)
        levels_m=[1]*n
        for _ in range(total-n): levels_m[self.r.randrange(n)]+=1
        players=[]
        for i,(c,lvl) in enumerate(zip(classes,levels)):
            players.append({
                "character":f"0xc{i+1}","owner":f"0xa{i+1}",
                "team":0,"ready":True,"hp":100+10*lvl,
                "source":{"name":f"c{i+1}","classe":c["id"],"level":f"{lvl}n",
                  "strength":"100n","intelligence":"100n","chance":"100n",
                  "agility":"100n","wisdom":"100n","vitality":"0n",
                  "experience":"0n","spell_levels":{},"folded_stats":{},"weapon":None}
            })
        mt=self.d["mob_templates"][0]
        mobs=[]
        for i,lvl in enumerate(levels_m):
            mobs.append({"team":1,"scalar":"100n",
              "template":{"mob_type":mt["id"],"level_min":f"{lvl}n","level_max":f"{lvl}n",
                "hp":f'{mt["hp"]}n',"ap":f'{mt["ap"]}n',"mp":f'{mt["mp"]}n',
                "agility":f'{mt["agility"]}n',"wisdom":f'{mt["wisdom"]}n',
                "earth_res":f'{mt["earth_res"]}n',"fire_res":f'{mt["fire_res"]}n',
                "water_res":f'{mt["water_res"]}n',"air_res":f'{mt["air_res"]}n',
                "spells":[],"xp":f'{mt["xp"]}n',"loot":[]}})
        return {"fight_id":"rl","world":"local","board_seed":self.r.randint(1,1000000),
                "players":players,"mobs":mobs,"spells":{}}
