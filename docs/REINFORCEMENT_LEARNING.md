# Reinforcement learning plan

## Baseline

Start with Maskable PPO.

Why:
- discrete/structured actions;
- illegal actions can be masked;
- stable baseline;
- easy evaluation;
- easy parallelization.

The first model is intentionally simple. Do not optimize hyperparameters before the environment is correct.

## Observation

The model should eventually see all strategically relevant observable information:

- all fighters;
- class;
- level;
- HP/max HP;
- AP/MP;
- position;
- alive/dead;
- effects;
- cooldowns;
- spells and their levels;
- relevant stats;
- weapon;
- enemy information;
- board geometry;
- traps/glyphs/zones;
- current round;
- current actor;
- turn order;
- remaining resources.

The observation encoder must be deterministic and versioned.

## Action space

Do not use a giant unrestricted action list.

Represent actions as structured commands:

- `end_turn(fighter)`
- `move_to(fighter, path)`
- `cast_spell(fighter, spell, target_cell)`
- `weapon_strike(fighter, target_cell)`

Generate legal candidates from the current state and mask everything else.

Eventually expose exact reachable paths instead of the prototype's simplified movement representation.

## Reward

The terminal objective is winning the fight.

Use small shaping rewards only to accelerate learning.

Example:
- large positive reward for victory;
- large negative reward for defeat;
- positive reward for killing an enemy;
- negative reward for losing an ally;
- small damage/heal/positioning signals.

Continuously test for reward hacking.

A policy that farms damage, healing or movement without increasing win probability is not successful.

## Curriculum

Start easy and increase difficulty:

1. small fights;
2. 1v1;
3. 2v2;
4. 4-player teams;
5. multiple enemy compositions;
6. heterogeneous player levels;
7. enemy total level near team total;
8. enemy total above team total;
9. hard-fight replay pool;
10. unseen compositions and seeds.

The curriculum should be adaptive: increase difficulty when the agent reaches a target success rate.

## Hard-fight pool

Store fights where:
- the agent loses;
- win probability is low;
- the result is unexpectedly close;
- multiple policies disagree.

Replay these scenarios more often.

## Self-play / policy pool

Do not depend on self-play initially. The environment is already challenging.

Later maintain checkpoints:
- current policy;
- previous strong policies;
- specialist policies.

Use them for robustness tests and potentially self-play experiments.
