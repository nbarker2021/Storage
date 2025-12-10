#!/usr/bin/env python3
import json, time, subprocess, sys
from pathlib import Path

def run(cmd):
    t0=time.time()
    p=subprocess.run(cmd, shell=True, capture_output=True, text=True)
    dt=time.time()-t0
    return p.returncode, p.stdout, p.stderr, dt

def append_receipt(snap_path, sectors, delta_phi):
    o=json.loads(Path(snap_path).read_text(encoding="utf-8"))
    o.setdefault("receipts", []).append({
        "kind":"build_step",
        "sectors": sectors,
        "delta_phi": delta_phi,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    Path(snap_path).write_text(json.dumps(o, indent=2), encoding="utf-8")

if __name__ == "__main__":
    # usage: shim.py "<command>" /path/to/SNAP.json
    cmd = sys.argv[1]; snap = sys.argv[2]
    rc, out, err, dt = run(cmd)
    sectors = {"dNoether": 0.0, "dShannon": -0.0005*len(out.splitlines()), "dLandauer": 0.0}
    delta_phi = sum(sectors.values())
    append_receipt(snap, sectors, delta_phi)
    print(out, end="")
    print(err, end="", file=sys.stderr)
    sys.exit(rc)
