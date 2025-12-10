
import json, sys, math, hashlib, os

def load(path):
    with open(path) as f: return json.load(f)

def lcm(a,b):
    import math
    return abs(a*b)//math.gcd(a,b) if a and b else max(a,b)

def main():
    if len(sys.argv) < 4:
        print("usage: compile_phon.py phon_program.json phon_profile.json out.json")
        sys.exit(1)
    prog = load(sys.argv[1])
    prof = load(sys.argv[2])
    # Determine base n from meter
    n = 4
    bpm = 120.0
    stresses = []
    phonemes = []
    for op in prog["program"]:
        if op["op"] == "meter":
            num = op["numerator"]
            if num in (3,6,12): n = lcm(n,12)
            elif num == 4: n = lcm(n,4)
        if op["op"] == "tempo":
            bpm = op["bpm"]
        if op["op"] == "stress":
            stresses.append((op["beat"], op["level"]))
        if op["op"] == "phoneme":
            phonemes.append(op)
    # Voicing parity: if mix of V and UV exists, promote parity by lcm with 8
    seen_v = any(p.get("voicing")=="V" for p in phonemes)
    seen_uv = any(p.get("voicing")=="UV" for p in phonemes)
    if seen_v and seen_uv:
        n = lcm(n,8)
    # Build taps at stressed beats (convert beat index to phase on ring)
    # For a 3/4 bar, evenly space phases by 2π/3; generalize by modulo numerator if present
    numerators = [op["numerator"] for op in prog["program"] if op["op"]=="meter"]
    num = numerators[0] if numerators else 4
    taps = sorted(set(((b % num)/num)*2*math.pi for (b,lev) in stresses))
    if not taps:
        taps = [0.0]
    # Delay from first stress phase; add small tempo term
    phase0 = taps[0]
    dtau = (prof["kappa"]["beat"] * (phase0/(2*math.pi))) + (prof["kappa"]["tempo"] * (60.0/max(bpm,1.0)))
    # Weight from average SPL
    spl_max = max(1.0, prof.get("spl_max", 85.0))
    spls = [p.get("spl", spl_max*0.8) for p in phonemes]
    weight = min(1.0, max(0.1, (sum(spls)/max(len(spls),1))/spl_max))
    # Build controls: one from meter baseline, one from stress
    controls = [
        {"source_index":0, "n": int(n), "dtau": float(dtau), "taps_rad": [float(t) for t in taps], "weight": float(weight)}
    ]
    out = {"profile_hash":"demo_profile_hash_psi", "controls": controls}
    with open(sys.argv[3], "w") as f: json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
