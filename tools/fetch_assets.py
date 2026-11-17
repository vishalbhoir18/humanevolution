#!/usr/bin/env python3
"""Fetch the CC0 MakeHuman / MPFB2 base-mesh data used to build the models.

The data (base mesh hm08, morph targets, rigs, skin weights, UV masks) is
published by the MakeHuman community under CC0 1.0.  It is redistributed
unchanged inside the `anny` package on PyPI (NAVER LABS Europe, Apache-2.0
code), which is the copy this script downloads.  Only data files are
extracted; no code from the package is run.

    python tools/fetch_assets.py            # -> tools/.cache/mpfb2
"""
import os
import subprocess
import sys
import tempfile
import zipfile

VERSION = "0.6.2"
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, ".cache", "mpfb2")
PREFIX = "anny/data/mpfb2/"
SKIP = (".py", ".pth", ".pt")


def _download(tmp):
    """Get the wheel straight from PyPI (no pip needed); fall back to pip."""
    import hashlib
    import json
    import urllib.request
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/anny/{VERSION}/json", timeout=60) as r:
            files = json.load(r)["urls"]
        info = next(f for f in files if f["filename"].endswith(".whl"))
        path = os.path.join(tmp, info["filename"])
        with urllib.request.urlopen(info["url"], timeout=600) as r, open(path, "wb") as out:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                out.write(chunk)
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        if digest != info["digests"]["sha256"]:
            raise RuntimeError("checksum mismatch for " + info["filename"])
        return path
    except Exception as exc:  # e.g. a proxy that only allows pip
        print("direct download failed (%s); trying pip" % exc)
        subprocess.check_call([sys.executable, "-m", "pip", "download", f"anny=={VERSION}",
                               "--no-deps", "-d", tmp, "-q"])
        return next(os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith(".whl"))


def main():
    if os.path.exists(os.path.join(DEST, "3dobjs", "base.obj")):
        print("already present:", DEST)
        return
    with tempfile.TemporaryDirectory() as tmp:
        wheel = _download(tmp)
        n = 0
        with zipfile.ZipFile(wheel) as z:
            for info in z.infolist():
                name = info.filename
                if not name.startswith(PREFIX) or name.endswith("/") or name.endswith(SKIP):
                    continue
                rel = os.path.normpath(name[len(PREFIX):])
                if rel.startswith("..") or os.path.isabs(rel):
                    continue
                out = os.path.join(DEST, rel)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with z.open(info) as src, open(out, "wb") as dst:
                    dst.write(src.read())
                n += 1
    print(f"extracted {n} data files to {DEST}")


if __name__ == "__main__":
    main()
