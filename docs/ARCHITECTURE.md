# Architecture

```text
                AresRPG repository
                       |
                       v
              @aresrpg/fight engine
                       |
                 Bun bridge
                       |
              NDJSON stdin/stdout
                       |
                       v
                Python environment
                       |
          +------------+-------------+
          |                          |
          v                          v
  Scenario generator          RL policy/value
          |                          |
          +------------+-------------+
                       |
                       v
                 Exact simulator
                       |
                       v
               Search / evaluation
                       |
          +------------+-------------+
          |                          |
          v                          v
  Composition ranking         Combat solver
```

## Runtime separation

The simulator process is a long-lived Bun process. Python sends one JSON request per line and receives one JSON response per line.

This avoids starting Bun for every action.

## Colab target

Google Colab is a convenient first remote training environment.

Bun has an official Linux installer and ships as a standalone executable. The official installation is:

```bash
apt-get update -y
apt-get install -y unzip
curl -fsSL https://bun.com/install | bash
export PATH="$HOME/.bun/bin:$PATH"
bun --version
```

The exact Colab runtime can change, so `notebooks/colab_setup.sh` verifies the installation instead of assuming a fixed environment.

## Scaling

The first prototype uses one simulator process.

The scalable version should use multiple independent simulator workers:

```text
worker 0 -> combat
worker 1 -> combat
worker 2 -> combat
...
worker N -> combat
```

A vectorized environment can collect experience from all workers.

For this project, simulator throughput can be more important than GPU size because each combat is a relatively small state machine.
