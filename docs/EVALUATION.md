# Evaluation protocol

## Training metrics are not benchmark metrics

Training win rate can be misleading.

Maintain a frozen benchmark suite.

## Benchmark groups

1. balanced teams;
2. heterogeneous levels;
3. enemy level near team level;
4. enemy level above team level;
5. unseen enemy groups;
6. unseen seeds;
7. unusual compositions;
8. challenge/hard fights.

## Report

For every model checkpoint report:

```text
checkpoint
episodes
winrate
95% interval
average turns
average deaths
average HP remaining
invalid-action rate
```

Also report results by scenario category.

A new model is better only if it improves the held-out benchmark, not merely the training reward.
