
#!/usr/bin/env python3
import argparse, base64, io, json, os, sys, time, zipfile, hashlib
from pathlib import Path
from string import Template

DEFAULT_EXTS = [".py", ".pyi", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
                ".md", ".txt", ".csv", ".tsv", ".rst"]

def iter_files(roots, include_ext, follow_archives=True):
    seen = set()
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        if root.is_file() and root.suffix.lower()==".zip" and follow_archives:
            with zipfile.ZipFile(root, "r") as z:
                for info in z.infolist():
                    if info.is_dir():
                        continue
                    name = info.filename
                    ext = Path(name).suffix.lower()
                    if include_ext and ext not in include_ext:
                        continue
                    data = z.read(info.filename)
                    vpath = f"{root.name}::{name}"
                    if vpath not in seen:
                        seen.add(vpath)
                        yield vpath, data
            continue
        if root.is_dir():
            for path in root.rglob("*"):
                if path.is_dir(): continue
                ext = path.suffix.lower()
                if include_ext and ext not in include_ext:
                    continue
                try:
                    data = path.read_bytes()
                except Exception:
                    continue
                vrel = path.relative_to(root).as_posix()
                vpath = f"{root.name}/{vrel}"
                if vpath not in seen:
                    seen.add(vpath)
                    yield vpath, data
        else:
            ext = root.suffix.lower()
            if include_ext and ext not in include_ext:
                continue
            try:
                data = root.read_bytes()
            except Exception:
                data = b""
            vpath = root.name
            if vpath not in seen:
                seen.add(vpath)
                yield vpath, data

def make_zip_bytes(items, compress=True):
    mem = io.BytesIO()
    mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    manifest = []
    with zipfile.ZipFile(mem, "w", compression=mode) as z:
        for vpath, data in items:
            z.writestr(vpath, data)
            h = hashlib.sha256(data).hexdigest()
            manifest.append({"path": vpath, "sha256": h, "size": len(data)})
    return mem.getvalue(), manifest

MONOLITH_TEMPLATE = Template(r"""
# AUTO-GENERATED MONOLITH (do not edit by hand)
# Created: $TS
# Files: $COUNT | ZIP bytes: $ZIPSZ

import sys, io, base64, zipfile, importlib.abc, importlib.util, hashlib, json

_EMBED_ZIP_B64 = '''$B64'''
_MANIFEST = $MANIFEST_JSON
_MONOLITH_NAME = "$NAME"
_VERSION = "$VERSION"

def manifest():
    return {"name": _MONOLITH_NAME, "version": _VERSION, "files": _MANIFEST, "zip_b64_len": len(_EMBED_ZIP_B64)}

def _zipfile():
    raw = base64.b64decode(_EMBED_ZIP_B64.encode("ascii"))
    return zipfile.ZipFile(io.BytesIO(raw), "r")

def list(prefix=""):
    with _zipfile() as z:
        return [n for n in z.namelist() if n.startswith(prefix)]

def read(path: str) -> bytes:
    with _zipfile() as z:
        return z.read(path)

def extract_to(dst_dir: str):
    with _zipfile() as z:
        z.extractall(dst_dir)

class _MonolithLoader(importlib.abc.InspectLoader):
    def __init__(self, z, fullname, path):
        self.z = z; self.fullname = fullname; self.path = path
    def get_source(self, fullname):
        try: data = self.z.read(self.path)
        except KeyError: return None
        return data.decode("utf-8", errors="replace")
    def get_code(self, fullname):
        src = self.get_source(fullname)
        if src is None: return None
        return compile(src, f"<{_MONOLITH_NAME}:{self.path}>", "exec")
    def is_package(self, fullname): return self.path.endswith("__init__.py")
    def get_filename(self, fullname): return f"<{_MONOLITH_NAME}:{self.path}>"

class _MonolithFinder(importlib.abc.MetaPathFinder):
    def __init__(self):
        raw = base64.b64decode(_EMBED_ZIP_B64.encode("ascii"))
        self.z = zipfile.ZipFile(io.BytesIO(raw), "r")
        self.names = set(self.z.namelist())
    def find_spec(self, fullname, path, target=None):
        p = fullname.replace(".", "/")
        for c in (f"{p}.py", f"{p}/__init__.py"):
            if c in self.names:
                loader = _MonolithLoader(self.z, fullname, c)
                is_pkg = c.endswith("__init__.py")
                return importlib.util.spec_from_loader(fullname, loader, origin=loader.get_filename(fullname), is_package=is_pkg)
        return None

_finder = None
def install():
    global _finder
    if _finder is None:
        _finder = _MonolithFinder()
        sys.meta_path.insert(0, _finder)
    return True

def verify_integrity():
    with _zipfile() as z:
        for e in _MANIFEST:
            if hashlib.sha256(z.read(e["path"])).hexdigest() != e["sha256"]:
                return False, e["path"]
    return True, None
""")

def write_monolith(py_out: Path, zip_bytes: bytes, manifest: list, name: str, version: str):
    b64 = base64.b64encode(zip_bytes).decode("ascii")
    txt = MONOLITH_TEMPLATE.substitute(
        TS=time.strftime("%Y-%m-%d %H:%M:%S"),
        COUNT=len(manifest),
        ZIPSZ=len(zip_bytes),
        B64=b64,
        MANIFEST_JSON=json.dumps(manifest, indent=2),
        NAME=name,
        VERSION=version
    )
    py_out.write_text(txt, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", default=["."], help="Directories or .zip files to include")
    ap.add_argument("--out", default="aletheia_monolith.py", help="Output .py filename")
    ap.add_argument("--include-ext", default=",".join(DEFAULT_EXTS), help="Comma list of file extensions to include")
    ap.add_argument("--monolith-name", default="AletheiaMonolith", help="Logical name for the monolith")
    ap.add_argument("--version", default="1.0.0", help="Version string to embed")
    ap.add_argument("--max-bytes", type=int, default=50_000_000, help="Max total raw bytes to include (0=no cap)")
    args = ap.parse_args()

    include_ext = [e.strip().lower() for e in args.include_ext.split(",") if e.strip()]
    items, total = [], 0
    for vpath, data in iter_files(args.roots, include_ext):
        total += len(data)
        if args.max_bytes and total > args.max_bytes:
            print(f"[forge] size cap reached at {total} bytes; truncating.")
            break
        items.append((vpath, data))

    zip_bytes, manifest = make_zip_bytes(items, compress=True)
    write_monolith(Path(args.out), zip_bytes, manifest, args.monolith_name, args.version)
    print(f"[forge] wrote {args.out} with {len(manifest)} files; zip={len(zip_bytes)} bytes")

if __name__ == "__main__":
    main()
