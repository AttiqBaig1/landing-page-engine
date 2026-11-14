# -*- coding: utf-8 -*-
"""
build_web.py
------------
Builds the browser version of the engine (no server needed) into a folder
that GitHub Pages serves. The real Python engine runs in the browser through
Pyodide; photos are pre-resized here because Pillow isn't shipped.

Usage:
    python build_web.py --pyodide path/to/pyodide/package --out ../site
Binary bundles use the .wasm extension so every static host serves them
as plain binary files.
"""
import argparse
import io
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"
LIB = ROOT / "photo_library"
WEB = Path(__file__).resolve().parent
EXTS = (".jpg", ".jpeg", ".png", ".webp")
ENGINE_FILES = ["generate_site.py", "niche_content.py", "niche_content_extra.py", "theme.py",
                "images.py", "cities.py", "icons.py", "wp_format.py", "niche_content_more.py",
                "niche_more_data.py", "remote_photos.py", "base_css.txt",
                "cities.csv", "sample_leads.csv"]
PYODIDE_FILES = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "pyodide-lock.json", "pyodide.js"]


def _jpeg(im, w, q):
    im = im.copy()
    if im.width > w:
        im = im.resize((w, int(im.height * w / im.width)), Image.Resampling.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=q, optimize=True, progressive=True)
    return b.getvalue()


def build(pyodide_dir: Path, out: Path):
    if out.exists():
        shutil.rmtree(out)
    (out / "bin").mkdir(parents=True)
    (out / "photos").mkdir()
    (out / "pyodide").mkdir()

    shutil.copy(WEB / "index.html", out / "index.html")
    shutil.copy(WEB / "web_api.py", out / "web_api.txt")
    (out / ".nojekyll").write_text("")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ENGINE_FILES:
            z.write(ENGINE / f, f)
    (out / "bin" / "engine.wasm").write_bytes(buf.getvalue())

    folders = []
    for folder in sorted(p for p in LIB.iterdir() if p.is_dir()):
        files = [f for f in sorted((folder / "original").glob("*")) if f.suffix.lower() in EXTS]
        if not files:
            continue
        zb = io.BytesIO()
        with zipfile.ZipFile(zb, "w", zipfile.ZIP_STORED) as z:
            for f in files:
                im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
                z.writestr(f"{folder.name}/original/{f.name}", _jpeg(im, 1400, 70))
                for w, q in ((800, 72), (700, 70)):
                    z.writestr(f"{folder.name}/sized/{f.stem}__{w}.jpg", _jpeg(im, w, q))
        (out / "photos" / f"{folder.name}.wasm").write_bytes(zb.getvalue())
        folders.append(folder.name)
    (out / "photos" / "manifest.json").write_text(json.dumps(folders))

    for f in PYODIDE_FILES:
        shutil.copy(pyodide_dir / f, out / "pyodide" / f)
    shutil.copy(pyodide_dir / "python_stdlib.zip", out / "pyodide" / "python_stdlib.wasm")
    print(f"Web app built in {out} ({len(folders)} photo folders)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pyodide", required=True, help="folder with pyodide.mjs, pyodide.asm.wasm, ...")
    ap.add_argument("--out", default=str(ROOT / "site"))
    a = ap.parse_args()
    build(Path(a.pyodide), Path(a.out))
