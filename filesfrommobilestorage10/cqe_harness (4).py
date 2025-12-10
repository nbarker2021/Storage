
#!/usr/bin/env python3
# -- coding: utf-8 --
"""
CQE Harness — Minimal Runnable v0.1
See inline comments for operator order and receipts.
"""
import os, json, csv, math, time, random, hashlib, argparse
from dataclasses import dataclass
from typing import List, Tuple

def now_stamp():
    import time
    return time.strftime("%Y%m%d_%H%M%S")

# -------- Structures --------
@dataclass
class View:
    grid: List[List[int]]  # 4x4 bits

@dataclass
class E8State:
    x: List[float]
    root: List[float]
    res2: float

@dataclass
class LeechState:
    v24: List[int]
    code: str
    ok: bool

@dataclass
class Datum:
    uid: str
    tick: int
    views: List[View]
    triads: List[Tuple[int,int,int]]
    e8: E8State
    leech: LeechState
    kissing_dev: float
    receipt_nibble: str

# -------- Embedding --------
def _e8_family_A_candidate(x):
    idx = sorted(range(8), key=lambda i: abs(x[i]), reverse=True)[:2]
    cand = [0.0]*8
    for i in idx:
        cand[i] = 1.0 if x[i] >= 0 else -1.0
    return cand

def _e8_family_B_candidate(x):
    cand, neg = [], 0
    for xi in x:
        s = -0.5 if xi < 0 else 0.5
        if s < 0: neg += 1
        cand.append(s)
    if neg % 2 == 1:
        j = min(range(8), key=lambda i: abs(x[i]))
        cand[j] = -cand[j]
    return cand

def e8_quantize(x):
    def r2(a,b): return sum((ai-bi)**2 for ai,bi in zip(a,b))
    A, B = _e8_family_A_candidate(x), _e8_family_B_candidate(x)
    return (A, r2(x,A)) if r2(x,A) <= r2(x,B) else (B, r2(x,B))

def leech_bind(v24_bits):
    ok = True
    for g in range(4):
        if sum(v24_bits[g*6:(g+1)*6]) % 2 != 0:
            ok = False
    return "H8", ok

# -------- Φ --------
def parity_defects(view: View):
    rows = cols = 0
    G = view.grid
    for r in range(4):
        for c in range(2):
            if G[r][c] != G[r][3-c]: rows += 1
    for c in range(4):
        for r in range(2):
            if G[r][c] != G[3-r][c]: cols += 1
    return rows, cols

def sparsity(triads): return sum(1 for t in triads if any(t))
def kissing_dev(root):
    import math
    L = math.sqrt(sum(x*x for x in root))
    return abs(L - math.sqrt(2.0))

def phi(d: Datum):
    pr = sum(parity_defects(v)[0] for v in d.views)
    pc = sum(parity_defects(v)[1] for v in d.views)
    k  = d.kissing_dev
    s  = sparsity(d.triads)
    return 1.0*pr + 1.0*pc + 0.5*k + 0.1*s

# -------- Ops --------
def op_mirror(d: Datum):
    for v in d.views:
        for r in range(4):
            v.grid[r][3] = v.grid[r][0]
            v.grid[r][2] = v.grid[r][1]
    return d

def op_delta(d: Datum):
    base = phi(d); best = base; best_pos=None
    for vi, v in enumerate(d.views):
        for r in range(4):
            for c in range(4):
                v.grid[r][c] ^= 1
                tmp = phi(d)
                if tmp < best:
                    best = tmp; best_pos=(vi,r,c)
                v.grid[r][c] ^= 1
    if best_pos: 
        vi,r,c = best_pos
        d.views[vi].grid[r][c] ^= 1
    return d

def op_snap(d: Datum):
    feat = []
    for v in d.views:
        ones = sum(sum(row) for row in v.grid)
        rp = sum(row[0]^row[3] for row in v.grid)
        feat.append( (ones + rp) / 16.0 )
    x8 = [float(feat[i]) for i in range(8)]
    root, res2 = e8_quantize(x8)
    d.e8 = E8State(x=x8, root=root, res2=res2)
    d.kissing_dev = kissing_dev(root)
    scaled = []
    for val in x8[:3]:
        bits = [(1 if val > t else 0) for t in [0.125,0.25,0.375,0.5,0.625,0.75]]
        scaled.extend(bits)
    while len(scaled) < 24: scaled.append(0)
    code, ok = leech_bind(scaled[:24])
    d.leech = LeechState(v24=scaled[:24], code=code, ok=ok)
    return d

def op_braid(d: Datum):
    d.triads.sort()
    return d

def strict_ok(pre: Datum, post: Datum): return phi(post) <= phi(pre)

# -------- Engine --------
ALTS = list(range(7))

def random_view():
    import random
    return View([[random.randint(0,1) for _ in range(4)] for __ in range(4)])

def random_datum(uid, tick):
    import random
    views = [random_view() for _ in range(8)]
    triads = [(random.randint(0,1), random.randint(0,1), random.randint(0,1)) for _ in range(12)]
    return Datum(uid=uid, tick=tick, views=views, triads=triads,
                 e8=E8State(x=[0.0]*8, root=[0.0]*8, res2=0.0),
                 leech=LeechState(v24=[0]*24, code="H8", ok=False),
                 kissing_dev=0.0, receipt_nibble="0000")

def receipt(pre: Datum, post: Datum, op: str):
    nibble = [
        1 if all(parity_defects(v)[0]==0 and parity_defects(v)[1]==0 for v in post.views) else 0,
        1,  # braid_ok (accepted after op_braid)
        1 if post.leech.ok else 0,
        1 if strict_ok(pre, post) else 0,
    ]
    payload = {
        "uid": post.uid, "tick": post.tick, "op": op,
        "phi_pre": phi(pre), "phi_post": phi(post),
        "nibble": "".join(map(str,nibble)),
        "e8_res2": post.e8.res2, "kissing_dev": post.kissing_dev,
        "leech_code": post.leech.code, "leech_ok": post.leech.ok
    }
    s = json.dumps(payload, sort_keys=True)
    payload["merkle"] = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return payload

def step_once(active, outdir, tick):
    os.makedirs(outdir, exist_ok=True)
    L = open(os.path.join(outdir,"ledger.jsonl"), "a", encoding="utf-8")
    C = open(os.path.join(outdir,"lpc.csv"), "a", newline="", encoding="utf-8")
    import csv as _csv
    cw = _csv.writer(C)
    if C.tell() == 0: cw.writerow(["uid","tick","phi","nibble","e8_res2","kissing_dev","leech_ok","merkle"])
    for alt in ALTS:
        for d in active:
            for op in ["MIRROR","DELTA","SNAP","BRAID"]:
                pre = json.loads(json.dumps(d, default=lambda o:o.__dict__))
                def build(s):
                    views = [View(grid=[row[:] for row in v['grid']]) for v in s['views']]
                    e8 = E8State(x=s['e8']['x'], root=s['e8']['root'], res2=s['e8']['res2'])
                    leech = LeechState(v24=s['leech']['v24'], code=s['leech']['code'], ok=s['leech']['ok'])
                    return Datum(uid=s['uid'], tick=s['tick'], views=views, triads=[tuple(t) for t in s['triads']],
                                 e8=e8, leech=leech, kissing_dev=s.get('kissing_dev',0.0), receipt_nibble=s.get('receipt_nibble','0000'))
                preD = build(pre)
                if op == "MIRROR": d = op_mirror(d)
                elif op == "DELTA": d = op_delta(d)
                elif op == "SNAP": d = op_snap(d)
                elif op == "BRAID": d = op_braid(d)
                rec = receipt(preD, d, op)
                L.write(json.dumps(rec)+"\n")
                cw.writerow([d.uid, d.tick, f"{phi(d):.6f}", rec["nibble"], f"{d.e8.res2:.6f}", f"{d.kissing_dev:.6f}", int(d.leech.ok), rec["merkle"]])
    L.close(); C.close()
    # summary
    lines = sum(1 for _ in open(os.path.join(outdir,"ledger.jsonl"),"r",encoding="utf-8"))
    okc = sum(int(r.split(",")[-2]) for i,r in enumerate(open(os.path.join(outdir,"lpc.csv"),"r",encoding="utf-8")) if i>0)
    with open(os.path.join(outdir,"summary.txt"),"w",encoding="utf-8") as S:
        S.write(f"CQE Harness run @ {now_stamp()}\n")
        S.write(f"Datums: {len(active)}  Alternates: {len(ALTS)}  Ledger entries: {lines}\n")
        S.write(f"Leech receipt OK count: {okc}\n")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()
    outdir = args.out or os.path.join("runs", now_stamp())
    active = [ random_datum("d0",0), random_datum("d1",0) ]
    step_once(active, outdir, 0)
    print("OUTDIR", outdir)

if __name__ == "__main__":
    main()
