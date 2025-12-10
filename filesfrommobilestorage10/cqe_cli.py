#!/usr/bin/env python3
"""CQE Master CLI"""
import sys
from pathlib import Path

PACKAGES_DIR = Path("/mnt/user-data/outputs/cqe_packages")

def list_packages():
    print("\n📦 CQE Packages\n")
    for pkg in sorted(PACKAGES_DIR.iterdir()):
        if pkg.is_dir():
            mods = len(list((pkg / pkg.name).glob('*.py')))
            print(f"{pkg.name:20} ({mods} modules)")

def show_info(name):
    pkg = PACKAGES_DIR / name
    if not pkg.exists():
        print(f"Package not found: {name}")
        return
    print(f"\n{name}\n")
    readme = pkg / 'README.md'
    if readme.exists():
        print(readme.read_text())

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'list':
        list_packages()
    elif sys.argv[1] == 'info' and len(sys.argv) > 2:
        show_info(sys.argv[2])
