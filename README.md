# AresRPG RL

A research system for [AresRPG](https://github.com/aresrpg/aresrpg) tactical combat — not
just a game-playing bot. Two intended outputs, neither built yet beyond the RL scaffolding
below:

1. **Composition analysis** — which 4-character team compositions are strongest, measured
   across a broad distribution of enemies, levels, maps and seeds; generalists vs.
   specialists, with statistically meaningful rankings.
2. **Exact fight solver** — given one concrete fight state, estimate win probability,
   recommend the best action (and a full line), explain why, and offer alternatives.

The eventual architecture combines a learned policy/value model with exact simulation and
search. See `docs/ROADMAP.md` for the phased plan and `docs/DESIGN_NOTES.md` for the
design principles behind phases 2-5.

## Core principle

**Never reimplement AresRPG combat rules in Python.** The real `@aresrpg/fight` engine
(TypeScript, in the AresRPG repo) is the only source of truth for legality, state
transitions, and combat math. Python owns RL, scenario generation, datasets, evaluation,
and search orchestration — it calls the engine, never re-derives it. See
`CONTRIBUTING.md` for the full list of rules this implies.

## Status

**Working today**: a real fight can be generated, trained against, won or lost, logged,
and visualized. Real AresRPG classes, spells, and mobs (pulled from the actual content
pack, not placeholders); an exact legal-action space (movement, spell casts, weapon
strikes — all filtered through the engine's own legality checks, not "every board cell
and hope"); a MaskablePPO training loop; a training dashboard.

**Not built yet**: curriculum, hard-fight replay, composition research, the exact
solver, and any UI. Character stat allocation is a simplified approximation, not the
real per-class leveling system — see `docs/ROADMAP.md` for exactly what's checked off
(Phase 1, making the simulator interface exact, is complete).

## Architecture

```text
AresRPG repo → @aresrpg/fight engine → Bun bridge (bridge/server.ts)
                                              │  NDJSON over stdin/stdout
                                              ▼
                                      Python (rl/, tools/)
                              scenario generator ─┬─ RL policy/value
                                                   ▼
                                          exact simulator (the bridge)
```

Full detail, including why the bridge imports the engine directly instead of via
`node_modules`, in `docs/ARCHITECTURE.md`.

## Repo layout

```
bridge/server.ts     the only place that talks to @aresrpg/fight — one long-lived Bun
                      process per training env, JSON-per-line protocol
rl/                   bridge.py (subprocess wrapper), env.py (Gymnasium env), scenarios.py
                      (random fight generator), train.py (MaskablePPO)
tools/
  build_content.py    pulls real classes/spells/mobs from an AresRPG checkout into data/
  dashboard.py        renders a training-stats HTML report from a Monitor CSV
  evaluate.py         held-out benchmark: win rate + CI, deaths, HP left, by difficulty
  smoke_test.py       one-shot bridge ping
  benchmark.py        rough episodes/win-rate check
  solve_fight.py       stub — Phase 4, not implemented
data/                 archetypes.json (classes, mobs), spells.json (full spell catalog) —
                      generated, not hand-authored; see "Content pipeline" below
docs/                 ARCHITECTURE.md, ROADMAP.md, DESIGN_NOTES.md, COLAB.md
```

## Quickstart

You need an AresRPG checkout (the real engine) alongside this repo — it's the only source
of truth for combat, so there's no "vendored" copy here.

```bash
git clone https://github.com/aresrpg/aresrpg.git --branch edge
export ARES_RPG_ROOT=$(pwd)/aresrpg   # point at that checkout

pip install -r requirements.txt
python tools/smoke_test.py            # expect {'ok': True}
```

No `bun install` needed — `bridge/server.ts` imports `@aresrpg/fight` straight from
`$ARES_RPG_ROOT`'s source (it's a private, unpublished package with zero runtime
dependencies of its own).

Never used Google Colab, or want to train without a local machine? `docs/COLAB.md` is a
full walkthrough, free-tier, no local setup at all.

### Generate the content pack

`data/archetypes.json` and `data/spells.json` are generated from a real AresRPG checkout,
not hand-written — regenerate them whenever that checkout's content pack changes:

```bash
python tools/build_content.py --root "$ARES_RPG_ROOT"
```

### Train

```bash
python -m rl.train --steps 200000 --workers 4 --out models/ppo_ares --log runs/monitor
```

`--workers N` runs N simulator processes in parallel, each its own Bun subprocess
(measured ~2.3x throughput at 4 workers on one machine — not linear, but real).
`--resume <checkpoint>.zip` continues training instead of starting over — see
`docs/COLAB.md` for using this across disconnected free-tier sessions.

### See how it's doing

```bash
python -m tools.dashboard --log runs/monitor --out runs/dashboard.html
```

`--log` is a directory — one CSV per worker — that `tools.dashboard` merges automatically.

Opens as a static HTML file (no server, no external dependencies) — win rate, reward,
episode length, and damage dealt/taken, each as a rolling average over training.

### Check it's actually generalizing

Training win rate isn't a benchmark — a model can look good by exploiting quirks of the
scenarios it trained on. Evaluate against a held-out scenario seed instead:

```bash
python -m tools.evaluate --model models/ppo_ares.zip --episodes 200
```

Win rate with a 95% confidence interval, average rounds/deaths/HP remaining, and
invalid-action rate — overall and broken down by enemy-vs-team difficulty. Defaults to
seed `999_999`, deliberately far from `rl.train`'s default (`12345`); if you trained with
a custom `--seed`, evaluate with a different one.

## Contributing

Read `CONTRIBUTING.md` first — in particular: never reimplement combat rules, pin the
AresRPG commit used for any experiment, separate training scenarios from held-out
evaluation, and don't commit model checkpoints to normal git history.
