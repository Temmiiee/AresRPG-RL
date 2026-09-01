# Composition analysis

## Objective

Find strong 4-character compositions, not merely a policy that wins with one fixed team.

## Evaluation

For every candidate composition, sample many independent scenarios.

Record:
- win rate;
- confidence interval;
- average turns;
- ally deaths;
- remaining HP;
- damage dealt/taken;
- performance by enemy archetype;
- performance by difficulty ratio;
- performance by level distribution;
- performance on unseen seeds.

## Ranking

Never rank only by raw win rate when sample counts differ.

At minimum store:
- number of fights;
- wins/losses;
- confidence interval;
- scenario distribution.

A Bayesian or Wilson interval can be used for ranking uncertainty.

## Generalist vs specialist

A composition can be:
- best overall;
- best against melee;
- best against bosses;
- best on open maps;
- best with large level disparities.

The report should show these separately.

## Search strategy

Do not enumerate every possible build immediately.

Start with:
1. broad random sampling;
2. keep promising compositions;
3. mutation/crossover or bandit-style allocation;
4. intensive evaluation of candidates;
5. final exhaustive evaluation of the shortlist.

This makes the system practical while preserving a path toward exhaustive research.
