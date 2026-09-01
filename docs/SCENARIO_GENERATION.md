# Scenario generation

## Main rule

For a team:

```text
team_total = level_1 + level_2 + level_3 + level_4
```

Generate an enemy total:

```text
enemy_total = team_total * difficulty_ratio
```

Initial ratio:
`0.90 <= ratio <= 1.25`

## Do not confuse total level with combat power

Two groups with the same total level can have very different difficulty.

Therefore later introduce a difficulty score using:
- number of enemies;
- enemy archetypes;
- damage;
- durability;
- range;
- control;
- healing;
- resistances;
- mobility;
- synergies;
- boss mechanics;
- board geometry.

The level ratio remains a useful sampling constraint, not the final definition of difficulty.

## Team distributions

Generate:
- four distinct classes;
- duplicate classes;
- balanced teams;
- double-DPS;
- double-support;
- no-healer;
- no-frontline;
- control-heavy;
- extreme level differences.

Example:
`50 / 45 / 35 / 20`

must be as valid a target as:
`40 / 40 / 40 / 40`.

## Enemy distributions

Generate:
- one strong enemy;
- many weak enemies;
- mixed levels;
- repeated mobs;
- bosses;
- ranged groups;
- melee groups;
- control-heavy groups;
- mixed archetypes.

## Dataset split

Never benchmark on scenarios used for training.

Maintain:
- train distribution;
- validation distribution;
- held-out test distribution;
- challenge distribution.

Use deterministic seeds to make benchmark runs reproducible.
