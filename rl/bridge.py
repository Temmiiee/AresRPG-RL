import json, os, shutil, subprocess
from pathlib import Path

def _bun_executable():
    # A shell that ran `curl bun.com/install | bash` (e.g. notebooks/colab_setup.sh)
    # only exports PATH into its own subprocess -- that doesn't reach whatever later
    # process spawns this one, so `bun` is very often "installed" but not resolvable
    # via shutil.which here. Fall back to the installer's own default location before
    # giving up, instead of a bare FileNotFoundError that doesn't say why.
    found = shutil.which("bun")
    if found: return found
    default_bin = Path(os.environ.get("BUN_INSTALL", Path.home() / ".bun")) / "bin"
    found = shutil.which("bun", path=str(default_bin))  # PATHEXT-aware: finds bun.exe on Windows too
    if found: return found
    raise RuntimeError(
        f"bun executable not found on PATH or in {default_bin}. Install it "
        "(see notebooks/colab_setup.sh) or add its bin/ directory to PATH."
    )

class AresBridge:
    def __init__(self):
        root=os.environ.get("ARES_RPG_ROOT")
        if not root: raise RuntimeError("Set ARES_RPG_ROOT first.")
        script=Path(__file__).resolve().parents[1]/"bridge"/"server.ts"
        self.p=subprocess.Popen([_bun_executable(),"run",str(script)],cwd=root,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,bufsize=1)
    def request(self,x):
        self.p.stdin.write(json.dumps(x)+"\n"); self.p.stdin.flush()
        line=self.p.stdout.readline()
        if not line: raise RuntimeError(self.p.stderr.read())
        return json.loads(line)
    def close(self):
        if self.p.poll() is None: self.p.terminate()
