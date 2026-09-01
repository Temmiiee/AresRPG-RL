"""Planned exact solver.

Final implementation:
1. load policy/value network;
2. enumerate legal actions;
3. clone the exact AresRPG simulator;
4. use policy-guided Beam Search or MCTS;
5. return best line, alternatives, win probability and explanation.
"""

def solve_fight(*args, **kwargs):
    raise NotImplementedError("Solver is the next phase; the exact simulator bridge is ready.")
