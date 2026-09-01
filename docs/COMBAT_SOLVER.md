# Exact combat solver

## Goal

Given one exact AresRPG fight state:

```text
What should I do to maximize my chance of winning?
```

Return:

- best immediate action;
- recommended sequence;
- estimated win probability;
- expected casualties;
- alternative lines;
- tactical explanation.

## Why RL alone is not enough

A policy predicts a good action.

It does not necessarily find the best sequence for one unusual tactical position.

Therefore combine:

```text
Policy network
      +
Value network
      +
Beam Search or MCTS
      +
Exact AresRPG simulator
```

## Search

For every candidate action:
1. clone/snapshot the simulator state;
2. apply the candidate;
3. ask the policy for likely continuations;
4. evaluate resulting states;
5. continue for a limited horizon;
6. compare branches.

Use the exact simulator as the ground truth.

## Output example

```text
Win probability: 87.4%

Recommended:
1. Control: move to cell 83
2. Healer: shield Frontliner
3. Frontliner: attack Mob A
4. Ranged: finish Mob A

Reason:
Mob A becomes isolated, which prevents the enemy's
highest-value interaction on the next turn.

Alternative:
Focus Mob B first — estimated win probability 81.2%.
```

The explanation layer must be generated from simulator events and measurable state changes, not hallucinated game mechanics.
