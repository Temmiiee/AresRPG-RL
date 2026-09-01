import json, os, subprocess
from pathlib import Path

class AresBridge:
    def __init__(self):
        root=os.environ.get("ARES_RPG_ROOT")
        if not root: raise RuntimeError("Set ARES_RPG_ROOT first.")
        script=Path(__file__).resolve().parents[1]/"bridge"/"server.ts"
        self.p=subprocess.Popen(["bun","run",str(script)],cwd=root,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,bufsize=1)
    def request(self,x):
        self.p.stdin.write(json.dumps(x)+"\n"); self.p.stdin.flush()
        line=self.p.stdout.readline()
        if not line: raise RuntimeError(self.p.stderr.read())
        return json.loads(line)
    def close(self):
        if self.p.poll() is None: self.p.terminate()
