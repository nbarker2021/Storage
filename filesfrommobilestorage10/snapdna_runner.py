#!/usr/bin/env python3
import sys
print(">> snapdna_runner: Run SNAPDNA/GTG workflows")
try:
    mod = __import__("snapdna.runner", fromlist=["main"])
    fn = getattr(mod, "main", None)
    if callable(fn):
        rc = fn() if fn.__code__.co_argcount==0 else fn(*sys.argv[1:])
        sys.exit(0 if rc is None else int(rc))
    else:
        print("Module 'snapdna.runner' has no callable 'main'. Skipping.")
except Exception as e:
    print("Warning: snapdna_runner stub could not run target: ", e)
    sys.exit(0)
