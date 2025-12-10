#!/usr/bin/env python3
import json, re, zipfile
from pathlib import Path
REG = Path(r"/mnt/data/SNAP_tool/snaps/registry.jsonl")
OUT = Path("/mnt/data/rehydrated_repo"); OUT.mkdir(parents=True, exist_ok=True)
def parse_ref(ref:str):
    m=re.match(r"zip://([^:]+)::(.+)", ref)
    return ((Path("/mnt/data")/m.group(1)), m.group(2)) if m else (None,None)
def main():
    count=0
    for line in REG.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        o=json.loads(line); name=o.get("name",""); refs=o.get("embeddings",{}).get("refs",[])
        if not (name.endswith(".py") or "py" in [t.lower() for t in o.get("tags",[])]): continue
        for r in refs:
            zp,ip=parse_ref(r)
            if zp and ip and zp.exists():
                with zipfile.ZipFile(zp,'r') as z:
                    try: data=z.read(ip)
                    except KeyError: continue
                    out=OUT/zp.stem/ip; out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
                    count+=1; break
    print("Rehydrated", count, "python files into", OUT)
if __name__=="__main__": main()
