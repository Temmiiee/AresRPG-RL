import argparse, importlib.util
from pathlib import Path
from sb3_contrib import MaskablePPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from .env import AresFightEnv

INFO_KEYWORDS = ("win", "damage_dealt", "damage_taken", "kills", "deaths", "rounds")

def _make_env(rank, seed, log_dir, override_existing):
    # Each worker gets its own AresFightEnv -> AresBridge -> Bun subprocess, and (with
    # --workers > 1) its own OS process via SubprocVecEnv: the simulator is one Bun
    # process per env talking JSON over a pipe, so true parallelism needs separate
    # processes, not just separate objects in one Python process.
    def _init():
        env = AresFightEnv(seed=seed + rank)
        log_path = str(Path(log_dir) / f"{rank}.monitor.csv") if log_dir else None
        return Monitor(env, filename=log_path, override_existing=override_existing, info_keywords=INFO_KEYWORDS)
    return _init

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=100000)
    p.add_argument("--out", default="models/ppo_ares")
    p.add_argument("--resume", default=None, help="path to an existing .zip checkpoint to continue training from")
    p.add_argument("--log", default="runs/monitor",
                   help="directory of per-worker episode-stats CSVs, read by tools/dashboard.py")
    p.add_argument("--workers", type=int, default=1,
                   help="parallel simulator processes (each spawns its own Bun subprocess)")
    p.add_argument("--seed", type=int, default=12345, help="base scenario-generator seed; worker i uses seed+i")
    a = p.parse_args()

    if a.log:
        Path(a.log).mkdir(parents=True, exist_ok=True)
    env_fns = [_make_env(i, a.seed, a.log, override_existing=not a.resume) for i in range(a.workers)]
    env = DummyVecEnv(env_fns) if a.workers == 1 else SubprocVecEnv(env_fns)

    # tensorboard is not in requirements.txt (see ROADMAP.md: optional logging) — degrade
    # to no logging instead of crashing when it isn't installed.
    tb_log = "runs/" if importlib.util.find_spec("tensorboard") else None
    if a.resume:
        model = MaskablePPO.load(a.resume, env=env, tensorboard_log=tb_log, device="auto")
    else:
        model = MaskablePPO("MlpPolicy", env, verbose=1, learning_rate=3e-4, n_steps=1024,
                            batch_size=256, gamma=.995, gae_lambda=.95, ent_coef=.01,
                            tensorboard_log=tb_log, device="auto")
    model.learn(total_timesteps=a.steps, reset_num_timesteps=a.resume is None)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    model.save(a.out)
    env.close()

# SubprocVecEnv uses multiprocessing, which on Windows (spawn start method) re-imports
# this module in every worker process — without this guard, each worker would parse
# argv and spin up its own sub-workers recursively.
if __name__ == "__main__":
    main()
