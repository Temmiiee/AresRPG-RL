# Roadmap

## Phase 0 — bootstrap
- [x] Python/Bun bridge skeleton
- [x] Gymnasium environment skeleton
- [x] Maskable PPO training skeleton
- [x] scenario generator skeleton
- [x] documentation
- [x] Colab bootstrap

## Phase 1 — make the simulator interface exact
- [ ] verify every FightSetup field against the current AresRPG commit
- [ ] exact player/content catalog
- [ ] exact mob catalog
- [ ] exact spell catalog
- [ ] exact legal-action enumeration
- [ ] exact movement/path enumeration
- [ ] robust state encoder
- [ ] simulator cloning/checkpoint support for search

## Phase 2 — first serious RL
- [ ] vectorized simulator workers
- [ ] curriculum
- [ ] hard-fight replay
- [ ] held-out benchmarks
- [ ] checkpoint management
- [ ] TensorBoard/W&B optional logging

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
