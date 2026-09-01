# AresRPG Combat AI Lab

Research prototype for building an RL agent and exact combat solver around the real AresRPG fight simulator.

## Final goal

This project is **not only a bot**.

It should eventually:
1. learn to play a 4-character AresRPG team;
2. determine which team compositions are strongest across broad combat distributions;
3. analyze a specific fight and return the best practical way to win it.

The intended final solver is:

```text
RL policy + value network + Beam Search/MCTS + exact AresRPG simulator
```

## Read this first

- `docs/PROJECT.md` — complete objective and constraints
- `docs/ARCHITECTURE.md` — system architecture
- `docs/REINFORCEMENT_LEARNING.md` — RL strategy
- `docs/SCENARIO_GENERATION.md` — team/enemy generation
- `docs/COMPOSITION_ANALYSIS.md` — composition research
- `docs/COMBAT_SOLVER.md` — exact fight solver
- `docs/DATA_PIPELINE.md` — real AresRPG data integration
- `docs/EVALUATION.md` — benchmark methodology
- `docs/ROADMAP.md` — development plan
- `docs/COLAB.md` — phone + Google Colab workflow

## Quick start on Colab

```bash
!git clone https://github.com/Temmiiee/AresRPG-RL.git
%cd aresrpg-RL
!bash notebooks/colab_setup.sh
```

Then:

```python
import os
os.environ["ARES_RPG_ROOT"] = "/content/aresrpg"
```

Smoke test:

```bash
!python tools/smoke_test.py
```

Training prototype:

```bash
!python -m rl.train --steps 100000
```

## Local development

Requires Bun and Python 3.11+.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

Set `ARES_RPG_ROOT` to the AresRPG checkout, then run the smoke test.

## Current prototype status

The repository contains the end-to-end skeleton, but **the content adapter and action enumeration are deliberately incomplete**. The next engineering step is to connect the exact current AresRPG class/spell/mob data and make legal action generation exact.

Do not start a multi-million-step training run until Phase 1 in `docs/ROADMAP.md` is complete.

## Why Bun?

The AresRPG fight engine is TypeScript. Python should call the real simulator rather than reproduce its rules.

Bun runs on Linux and provides a standalone executable; the official installer is used by the Colab bootstrap.

## Reproducibility

Record:
- AresRPG git commit;
- project git commit;
- dataset version;
- random seeds;
- training configuration;
- benchmark version.

## License

This project is an experimental adapter. AresRPG's source and assets remain subject to their own license.
