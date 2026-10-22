#!/usr/bin/env python3
"""比较两个目录下同名文件的 SHA-256（用于复跑一致性核验）。"""
import hashlib
import sys
from pathlib import Path


def h(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv):
    a, b, *names = argv
    a, b = Path(a), Path(b)
    if not names:
        names = sorted(
            p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()
        )
    mismatches = []
    missing = []
    same = 0
    for name in names:
        pa, pb = a / name, b / name
        if not pa.is_file() or not pb.is_file():
            missing.append((name, pa.is_file(), pb.is_file()))
            continue
        if h(pa) == h(pb):
            same += 1
        else:
            mismatches.append((name, h(pa), h(pb)))
    print(f"compared={len(names)} identical={same} mismatched={len(mismatches)} missing={len(missing)}")
    for row in mismatches:
        print("  MISMATCH", row)
    for row in missing:
        print("  MISSING", row)
    return 0 if not mismatches and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))