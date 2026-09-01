# Bridge setup (quick)

This project uses a JS/TS bridge (bridge/server.ts) to host the authoritative fight simulator. To run the bridge locally:

1. Install Bun (recommended): https://bun.sh

2. From the bridge/ directory:

```bash
bun install
bun run server.ts
```

Smoke test (from repo root)

```bash
export ARES_RPG_ROOT="$(pwd)"
python -m rl.smoke_test
```

Notes
-----
- The bridge and smoke test assume Bun is installed and the `bun` executable is on PATH.
- The bridge uses @aresrpg/fight; the bridge/package.json contains a dependency placeholder. Pin the version if you have a specific AresRPG commit/version you want to match.
