
import json, sys, math, hashlib, os

def load(path):
    with open(path) as f: return json.load(f)

def nearest_in_set(x, S):
    return min(S, key=lambda s: abs(s-x))

def lcm(a,b):
    import math
    return abs(a*b)//math.gcd(a,b) if a and b else max(a,b)

def main():
    if len(sys.argv) < 4:
        print("usage: compile_glyph.py glyph_program.json glyph_profile.json out.json")
        sys.exit(1)
    prog = load(sys.argv[1])
    prof = load(sys.argv[2])
    # Heuristic: infer rotational periodicity from rune count in group / operator classes
    n = 4
    rune_count = sum(1 for op in prog["program"] if op["op"]=="rune")
    has_group = any(op["op"]=="group" for op in prog["program"])
    has_matrix = any(op.get("node_type")=="matrix" for op in prog["program"] if op["op"]=="ast")
    has_fraction = any(op.get("node_type")=="fraction" for op in prog["program"] if op["op"]=="ast")
    if has_group or has_matrix:
        n = lcm(n,12)
    if has_fraction:
        n = lcm(n,8)
    # Taps: place at quarter points if many crossings/operators, else at rune indices
    m = max(1, rune_count)
    taps = [ (i/m)*2*math.pi for i in range(m) ]
    # Delay: from stroke_dtau times rune_count modulo small cap
    kappa = prof.get("kappa", {}).get("stroke_dtau", 0.01)
    dtau = (kappa * rune_count) % 1.0
    # Weight: proportional to rune_count but capped
    weight = min(1.0, 0.3 + 0.05 * rune_count)
    controls = [
        {"source_index":0, "n": int(n), "dtau": float(dtau), "taps_rad": [float(t) for t in taps[:8]], "weight": float(weight)}
    ]
    out = {"profile_hash":"demo_profile_hash_gamma", "controls": controls}
    with open(sys.argv[3], "w") as f: json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
