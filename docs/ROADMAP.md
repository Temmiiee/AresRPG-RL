# Roadmap

## Phase 0 — bootstrap
- [x] Python/Bun bridge skeleton
- [x] Gymnasium environment skeleton
- [x] Maskable PPO training skeleton
- [x] scenario generator skeleton
- [x] documentation
- [x] Colab bootstrap

## Phase 1 — make the simulator interface exact
- [x] verify every FightSetup field against the current AresRPG commit
- [x] exact player/content catalog — real classes, real HP formula. Stat allocation and
      spell levels now scale with class/level too, via `_stat_block`/`_spell_levels` in
      `rl/scenarios.py` — but these are a deliberate simplification, not the real
      leveling system: the actual per-class capital-point cost ladders live in AresRPG's
      `characteristic_costs.move` and weren't replicated (see the comment above
      `_stat_block` in `rl/scenarios.py` for what was simplified and why)
- [x] exact mob catalog — `tools/build_content.py` pulls real mob templates from
      `seed/content/mobs.json`; a curated subset (12 by default, tune `--mob-count`) rather
      than the full ~280-entry catalog
- [x] exact spell catalog — `tools/build_content.py` pulls the full real spell list from
      `seed/content/spells.json` into `data/spells.json`
- [x] exact legal-action enumeration — `candidates()` now calls the engine's own
      `spell_target_cells`/`weapon_target_cells` (real cast_legality: AP, range, line of
      sight/launch, cooldowns, cast caps), instead of every board cell
- [x] exact movement/path enumeration — `move_to` actions are generated from
      `reachable_fight_cells`/`fight_path_to`
- [x] robust state encoder — `rl/env.py`'s `_obs()` had two real bugs, both fixed:
      `f["hp"]/(f["hp"]+1)` isn't a health fraction (it converges to ~1 for any hp>0
      regardless of how hurt the fighter is — `max_hp` wasn't even in the wire summary to
      compute the real fraction), and `cell/196` normalized position against neither the
      real fixed combat grid (20×19=380 cells, `CONTRACT_CONSTANTS.grid_w/h`) nor the
      per-fight board bounding box. `bridge/server.ts`'s summary now reports `max_hp` and
      `grid_w`/`grid_h`; the encoder uses real hp fraction, grid-relative x/y, and adds an
      is-this-fighter-currently-acting flag that wasn't present at all before.
- [ ] simulator cloning/checkpoint support for search — deferred to Phase 4 (needed for
      the solver's beam/MCTS search, not for RL training itself)

Content provenance: `data/archetypes.json` and `data/spells.json` were generated from
AresRPG commit `d25d9d7bb7affb1f163cf8947dcdf569748e1d42` (branch `edge`, 2026-08-31) via
`python tools/build_content.py --root <AresRPG checkout>`. Re-run it and commit the
diff whenever the AresRPG content pack changes.

### Critical bridge bugs fixed (2026-09-01)

Before this pass, **no action had ever succeeded through the bridge** — not even
`end_turn`. Two root causes, both confirmed by direct reproduction against a real
AresRPG checkout:

1. `candidates()` sent `fighter`/`target_cell` as plain JS numbers. The engine compares
   them against bigint queue/cell values with strict `===`, which is always `false`
   across types (`1n === 1` is `false` in JS) — every action silently lost to
   `not_your_fighter` instead of an obvious crash.
2. `bridge/server.ts` passed the same hardcoded `observed_ms` to every `apply()` call.
   `end_turn` is gated by a 3-second anti-spam rule (`turn_min_ms`, meant for live
   play) measured against that same clock, so it always read as "too soon."

Fixed by using real `BigInt` fields in `candidates()` and a monotonic virtual clock in
`server.ts`. Two more bugs surfaced once actions actually started succeeding (both were
previously unreachable, since almost nothing got far enough to trigger them):
`rl/env.py`'s `step()` indexed the *post-step* action list with the *pre-step* index,
and its reward shaping read bigint-suffixed event-payload strings (e.g. `"4n"`) as if
they were plain ints. Verified end-to-end: full random-policy episodes now run to
completion (~130 steps/sec, 0 invalid actions) and `python -m rl.train` trains a
MaskablePPO policy without error.

## Phase 2 — first serious RL
- [x] vectorized simulator workers — `rl/train.py --workers N` runs N envs (each its
      own Bun subprocess) in N OS processes via SB3's `SubprocVecEnv`; measured ~2.3x
      throughput at 4 workers on a 1 machine (87 -> 200 env steps/sec), not linear
      (CPU contention) but a real gain. Each worker gets a distinct scenario-generator
      seed (`--seed`) and its own Monitor CSV under `--log` (a directory now, not a
      single file — `tools/dashboard.py` merges all workers' CSVs automatically)
- [ ] curriculum
- [ ] hard-fight replay
- [ ] held-out benchmarks
- [ ] checkpoint management — `python -m rl.train --resume <ckpt.zip>` now continues
      training an existing checkpoint; no versioning/auto-resume-latest yet
- [x] TensorBoard/W&B optional logging — `rl/train.py` degrades to no logging instead of
      crashing when tensorboard isn't installed (it's intentionally not in requirements.txt)
- [x] training dashboard — `rl/train.py --log` writes a per-episode Monitor CSV
      (win/loss, damage dealt/taken, kills/deaths, rounds); `tools/dashboard.py` renders
      it as a static HTML report (win rate, reward, episode length, damage trends)

## Phase 3 — composition research
- [ ] composition generator
- [ ] statistical ranking
- [ ] enemy archetype matrix
- [ ] specialist/generalist reports
- [ ] large-scale simulations

## Phase 4 — solver
- [ ] value network
- [ ] Beam Search
- [ ] MCTS experiment
- [ ] win probability calibration
- [ ] tactical explanation engine

## Phase 5 — interface
- [ ] upload/enter fight
- [ ] visual board
- [ ] best move
- [ ] full recommended line
- [ ] alternatives
- [ ] composition optimizer
