# Project specification

## Final objective

Build an AI research system for AresRPG combat, not merely a game-playing bot.

The system has two major outputs:

1. **Composition analysis**
   - determine which 4-character compositions are strongest;
   - measure them over a broad distribution of enemy groups, levels, maps and random seeds;
   - identify generalist and specialist compositions;
   - produce statistically meaningful rankings.

2. **Exact fight solver**
   - accept one concrete fight state;
   - estimate the probability of victory;
   - recommend the best immediate action;
   - search for a strong sequence of actions;
   - explain the recommended line;
   - provide alternatives and their estimated outcomes.

The final architecture should combine a learned policy/value model with exact simulation and search.

## Core principle

Never reimplement AresRPG combat rules in Python when the real `@aresrpg/fight` engine can be called.

Python owns:
- RL;
- scenario generation;
- datasets;
- evaluation;
- search orchestration.

Bun/TypeScript owns:
- the authoritative fight simulation;
- exact legality;
- state transitions;
- combat events.

## Target combat distribution

Primary target:
- exactly 4 player characters;
- different classes should be strongly represented;
- levels can differ substantially;
- enemy total level should usually be close to or above the player team's total level.

Initial enemy level ratio:
`enemy_total_level / team_total_level = 0.90 ... 1.25`

Later expand beyond that range for curriculum and challenge tests.

## Success criteria

The agent is not considered professional because it has a high training win rate.

It should generalize to:
- unseen seeds;
- unseen enemy combinations;
- unseen level distributions;
- unseen boards;
- unusual team compositions;
- hard fights;
- enemy power above team power.

All benchmark results must be produced on held-out scenarios.
