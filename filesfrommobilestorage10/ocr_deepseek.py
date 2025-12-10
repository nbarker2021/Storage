#!/usr/bin/env python3
import sys
print(">> ocr_deepseek: OCR pipeline via DeepSeek-OCR if present")
try:
    mod = __import__("adapters.ocr.deepseek", fromlist=["main"])
    fn = getattr(mod, "main", None)
    if callable(fn):
        rc = fn() if fn.__code__.co_argcount==0 else fn(*sys.argv[1:])
        sys.exit(0 if rc is None else int(rc))
    else:
        print("Module 'adapters.ocr.deepseek' has no callable 'main'. Skipping.")
except Exception as e:
    print("Warning: ocr_deepseek stub could not run target: ", e)
    sys.exit(0)
