# Browser bridge for the landing page engine (runs inside Pyodide).
# Uses the real engine modules unchanged; only image encoding is swapped
# for pre-resized photos, because Pillow is not shipped to the browser.
import base64
import csv
import io
import json
import shutil
import sys
import types
import zipfile
from pathlib import Path

APP = Path("/app")
ENGINE = APP / "engine"
LIB = APP / "photo_library"
OUT = Path("/tmp/out")

# --- stub PIL so `from PIL import Image, ImageOps` succeeds -------------
_pil = types.ModuleType("PIL")
_pil.Image = types.ModuleType("PIL.Image")
_pil.ImageOps = types.ModuleType("PIL.ImageOps")
sys.modules.update({"PIL": _pil, "PIL.Image": _pil.Image, "PIL.ImageOps": _pil.ImageOps})

with zipfile.ZipFile("/tmp/engine.zip") as z:
    z.extractall(ENGINE)
LIB.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ENGINE))

import generate_site  # noqa: E402
import images  # noqa: E402
from niche_content import NICHE_CONTENT  # noqa: E402
from theme import get_theme  # noqa: E402


def _img_to_datauri(path, max_w=1200, quality=72):
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        return ""
    sized = p.parent.parent / "sized" / f"{p.stem}__{max_w}.jpg"
    data = (sized if sized.exists() else p).read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


generate_site.img_to_datauri = _img_to_datauri

AVAILABLE_PHOTO_FOLDERS = set()   # filled from JS (photo zips that exist)
_loaded = set()


def _key(n):
    return str(n).lower().strip().replace(" ", "_").replace("-", "_")


def niches_json():
    out = []
    for k in sorted(NICHE_CONTENT):
        c = NICHE_CONTENT[k]
        T = get_theme(c["theme"])
        out.append({"key": k, "label": k.replace("_", " ").title(),
                    "keyword": generate_site.unescape(c["h1_keyword"]),
                    "theme": c["theme"], "bg": T["bg"], "accent": T["accent"],
                    "accent2": T["accent2"]})
    return json.dumps(out)


def set_photo_folders(names_json):
    AVAILABLE_PHOTO_FOLDERS.update(json.loads(names_json))


def photo_folder_for(niche):
    k = _key(niche)
    if k in AVAILABLE_PHOTO_FOLDERS:
        return k
    alias = (NICHE_CONTENT.get(k) or {}).get("photos")
    return alias if alias in AVAILABLE_PHOTO_FOLDERS else None


def folders_needed(niches_list_json):
    need = set()
    for n in json.loads(niches_list_json):
        f = photo_folder_for(n)
        if f and f not in _loaded:
            need.add(f)
    return json.dumps(sorted(need))


def install_photos(folder):
    with zipfile.ZipFile(f"/tmp/photos_{folder}.zip") as z:
        z.extractall(LIB)
    Path(f"/tmp/photos_{folder}.zip").unlink()
    _loaded.add(folder)


def parse_csv(text):
    """Same rules as run_batch.py: header row with name, address, phone, niche."""
    text = text.lstrip("﻿")
    reader = csv.DictReader(io.StringIO(text))
    heads = [h.strip().lower() for h in (reader.fieldnames or [])]
    missing = {"name", "address", "phone", "niche"} - set(heads)
    if missing:
        return json.dumps({"error": "CSV is missing column(s): " + ", ".join(sorted(missing))
                           + ". Found: " + ", ".join(heads)})
    rows = []
    for r in reader:
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        if not any(r.get(c) for c in ("name", "address", "phone")):
            continue
        rows.append({c: r.get(c, "") for c in ("name", "address", "phone", "niche")})
    return json.dumps({"rows": rows})


def reset_output():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)


def build_one(row_json):
    r = json.loads(row_json)
    name, address, phone, niche = (r.get("name", "").strip(), r.get("address", "").strip(),
                                   r.get("phone", "").strip(), _key(r.get("niche", "")))
    res = {"name": name, "address": address, "phone": phone, "niche": niche,
           "status": "", "slug": "", "error": "", "warnings": []}
    if not (name and address and phone):
        res.update(status="SKIPPED", error="name, address and phone are all required")
        return json.dumps(res)
    if niche not in NICHE_CONTENT:
        res.update(status="SKIPPED", error=f"unknown niche '{r.get('niche', '')}'")
        return json.dumps(res)
    try:
        path = generate_site.build_site(name, address, phone, niche, out_dir=str(OUT),
                                        warn=lambda m: res["warnings"].append(m.strip(" !")))
        res.update(status="BUILT", slug=path.parent.name,
                   kb=round(path.stat().st_size / 1024))
    except Exception as e:  # noqa: BLE001
        res.update(status="FAILED", error=str(e))
    return json.dumps(res)


def page_html(slug):
    return (OUT / slug / "index.html").read_text(encoding="utf-8")


def zip_all(results_json):
    results = json.loads(results_json)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for r in results:
            if r.get("status") == "BUILT":
                z.write(OUT / r["slug"] / "index.html", f"{r['slug']}/index.html")
        sio = io.StringIO()
        w = csv.DictWriter(sio, fieldnames=["name", "address", "phone", "niche", "slug", "status", "error"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(results)
        z.writestr("results.csv", sio.getvalue())
    return buf.getvalue()


def sample_csv():
    return (ENGINE / "sample_leads.csv").read_text(encoding="utf-8")


# ---------------------------------------------------------------- WordPress
from wp_format import build_gutenberg  # noqa: E402


def wp_payload(slug, name):
    """Same scoped Gutenberg block the Streamlit app publishes."""
    html = page_html(slug)
    return json.dumps({"title": name, "slug": slug, "status": "publish",
                       "content": build_gutenberg(html)})
