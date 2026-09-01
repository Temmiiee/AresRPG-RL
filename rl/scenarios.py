import json, random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BASE_HP = 50       # CONTRACT_CONSTANTS.base_hp in @aresrpg/fight
HP_PER_LEVEL = 5   # CONTRACT_CONSTANTS.hp_per_level

# Characteristic points: the real per-class cost ladders live in AresRPG's
# characteristic_costs.move (e.g. an "ikari" spends 3-5 capital per strength point
# depending on how much it already has); replicating that plus its per-level capital
# grant is out of scope here. This is a simpler stand-in that still makes level and
# class visibly matter instead of every character sharing flat stats: `points_per_level`
# capital points a level, mostly poured into the class's primary_stat (see
# tools/build_content.py — derived from DECISIONS.md's element->stat primaries), some
# into wisdom (dodge), the rest spread across the remaining offensive stats.
STAT_BASE = 10
POINTS_PER_LEVEL = 5
PRIMARY_SHARE = 0.5
WISDOM_SHARE = 0.2

def _stat_block(primary_stat, level):
    points = POINTS_PER_LEVEL * max(0, level - 1)
    stats = {"strength": STAT_BASE, "intelligence": STAT_BASE, "chance": STAT_BASE,
              "agility": STAT_BASE, "wisdom": STAT_BASE}
    stats[primary_stat] += round(points * PRIMARY_SHARE)
    stats["wisdom"] += round(points * WISDOM_SHARE)
    others = [s for s in ("strength", "intelligence", "chance", "agility") if s != primary_stat]
    share = points * (1 - PRIMARY_SHARE - WISDOM_SHARE) / len(others)
    for s in others:
        stats[s] += round(share)
    return stats

def _spell_levels(class_spells, level):
    # DECISIONS.md (AresRPG repo, 2026-08-09): "1 spell point granted per character
    # level from 2; raising n->n+1 costs n points -- Dofus 1.29 exact". Points go to
    # the earliest-unlocked spells first, mirroring how a real character would have
    # had the most time to invest in those.
    points = max(0, level - 1)
    unlocked = sorted((s for s in class_spells if s["unlock_level"] <= level), key=lambda s: s["unlock_level"])
    levels = {}
    for spell in unlocked:
        cur, cap = 1, len(spell["levels"])
        while points >= cur and cur < cap:
            points -= cur
            cur += 1
        levels[spell["name"]] = cur
    return levels

def _bigintify(value):
    """Suffix every integer leaf with 'n' so bridge/server.ts decodes it as BigInt.
    Required for mob templates: create_mob_snapshot() does raw bigint arithmetic
    on them before the normal (number-tolerant) normalize_* pass runs."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return f"{value}n"
    if isinstance(value, list):
        return [_bigintify(v) for v in value]
    if isinstance(value, dict):
        return {k: _bigintify(v) for k, v in value.items()}
    return value

def _mob_scalar_for_level(template, requested_level):
    """Mirrors mob_scalar_for_level() in @aresrpg/fight create.ts."""
    low, high = template["level_min"], template["level_max"]
    level = min(max(requested_level, low), high)
    span = high - low
    if span == 0:
        return 0
    return ((level - low) * 100 + span - 1) // span

class ScenarioGenerator:
    # Curriculum bounds (docs/DESIGN_NOTES.md: "start easy... increase difficulty when
    # the agent reaches a target success rate"). difficulty=1.0 is PROJECT.md's actual
    # target distribution (ratio 0.90-1.25, up to 4 mobs); difficulty=0.0 is a much
    # softer fight (weaker enemies, usually solo) to bootstrap learning before that.
    EASY_RATIO = (0.5, 0.75)
    TARGET_RATIO = (0.90, 1.25)
    TARGET_MAX_MOBS = 4

    def __init__(self, seed=12345, difficulty=1.0):
        self.r = random.Random(seed)
        self.d = json.loads((DATA_DIR / "archetypes.json").read_text())
        self.spells = json.loads((DATA_DIR / "spells.json").read_text())
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty):
        self.difficulty = min(1.0, max(0.0, difficulty))

    def _pick_mob_template(self, level):
        templates = self.d["mob_templates"]
        overlapping = [t for t in templates if t["level_min"] <= level <= t["level_max"]]
        pool = overlapping or templates
        return min(pool, key=lambda t: abs(level - min(max(level, t["level_min"]), t["level_max"])))

    def _class_spells(self, classe):
        return [dict(sp, name=name) for name, sp in self.spells.items() if sp["classe"] == classe]

    def setup(self):
        d=self.difficulty
        lo=self.EASY_RATIO[0]+(self.TARGET_RATIO[0]-self.EASY_RATIO[0])*d
        hi=self.EASY_RATIO[1]+(self.TARGET_RATIO[1]-self.EASY_RATIO[1])*d
        max_mobs=max(1,round(1+(self.TARGET_MAX_MOBS-1)*d))
        classes=self.r.sample(self.d["classes"],4)
        class_ids={c["id"] for c in classes}
        base=self.r.randint(10,60)
        levels=[max(1,base+self.r.randint(-20,20)) for _ in range(4)]
        team_total=sum(levels)
        ratio=self.r.uniform(lo,hi)
        total=max(4,round(team_total*ratio))
        n=self.r.randint(1,max_mobs)
        levels_m=[1]*n
        for _ in range(total-n): levels_m[self.r.randrange(n)]+=1
        players=[]
        for i,(c,lvl) in enumerate(zip(classes,levels)):
            stats=_stat_block(c["primary_stat"],lvl)
            spell_levels=_spell_levels(self._class_spells(c["id"]),lvl)
            players.append({
                "character":f"0xc{i+1}","owner":f"0xa{i+1}",
                "team":0,"ready":True,"hp":f"{BASE_HP + HP_PER_LEVEL*lvl}n",
                "source":{"name":f"c{i+1}","classe":c["id"],"level":f"{lvl}n",
                  "strength":f"{stats['strength']}n","intelligence":f"{stats['intelligence']}n",
                  "chance":f"{stats['chance']}n","agility":f"{stats['agility']}n",
                  "wisdom":f"{stats['wisdom']}n","vitality":"0n",
                  "experience":"0n","spell_levels":{k:f"{v}n" for k,v in spell_levels.items()},
                  "folded_stats":{},"weapon":None}
            })
        mobs=[]
        for lvl in levels_m:
            template=self._pick_mob_template(lvl)
            scalar=_mob_scalar_for_level(template,lvl)
            wire_template=_bigintify({k:v for k,v in template.items() if k!="name"})
            mobs.append({"team":1,"scalar":f"{scalar}n","template":wire_template})
        spells={name:sp for name,sp in self.spells.items() if sp["classe"] in class_ids}
        return {"fight_id":"rl","world":"local","board_seed":self.r.randint(1,1000000),
                "players":players,"mobs":mobs,"spells":spells}
