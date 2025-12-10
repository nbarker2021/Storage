#!/usr/bin/env python3
import sys
print(">> graph_debruijn: Build De Bruijn graphs from corpus")
try:
    mod = __import__("tools.graph.debruijn", fromlist=["main"])
    fn = getattr(mod, "main", None)
    if callable(fn):
        rc = fn() if fn.__code__.co_argcount==0 else fn(*sys.argv[1:])
        sys.exit(0 if rc is None else int(rc))
    else:
        print("Module 'tools.graph.debruijn' has no callable 'main'. Skipping.")
except Exception as e:
    print("Warning: graph_debruijn stub could not run target: ", e)
    sys.exit(0)
