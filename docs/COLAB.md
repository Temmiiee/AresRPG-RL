# Google Colab

Colab is the recommended first remote environment because the whole project can be controlled from a phone.

## 1. Get the repository

In a Colab cell:

```bash
!git clone https://github.com/YOUR_USERNAME/aresrpg-combat-ai.git
%cd aresrpg-combat-ai
```

## 2. Run the bootstrap

```bash
!bash notebooks/colab_setup.sh
```

The script:
- installs Python dependencies;
- installs Bun;
- adds Bun to PATH;
- checks Bun;
- clones/updates AresRPG if configured;
- installs AresRPG dependencies.

## 3. Set the AresRPG location

```python
import os
os.environ["ARES_RPG_ROOT"] = "/content/aresrpg"
```

## 4. Smoke test

```bash
!python tools/smoke_test.py
```

Expected result is a JSON response with `ok: true`.

## 5. Train

```bash
!python -m rl.train --steps 100000
```

Start small. Only move to millions of steps after the environment passes correctness tests.

## 6. Persist checkpoints

Colab runtimes are temporary. Mount Google Drive if you want checkpoints to survive runtime resets.

Example:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Then use an output path under `/content/drive/MyDrive/aresrpg-ai/`.

## Important

A GPU does not automatically make the whole pipeline faster. The fight simulator is CPU-side. The scalable design should use multiple simulator workers and benchmark simulator steps/second before buying or selecting a large GPU.
