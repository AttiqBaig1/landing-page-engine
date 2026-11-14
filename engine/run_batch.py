# -*- coding: utf-8 -*-
"""
run_batch.py
------------
Reads a CSV of businesses (name, address, phone, niche) and generates
a site for every row. Writes an output CSV with status + local path
for each (live URL column added later once WordPress publishing is
wired in via the Streamlit app).

Input CSV columns (header required): name, address, phone, niche
    R&R Roofing, "Fresno, CA", (559) 555-0123, roofing

Output CSV columns: name, phone, niche, slug, status, path, error

Usage:
    python run_batch.py leads.csv
    python run_batch.py leads.csv --out-dir my_sites --results results.csv
"""
import argparse
import csv
import sys
from pathlib import Path

from generate_site import build_site
from niche_content import NICHE_CONTENT, resolve_key


def run_batch(input_csv: str, out_dir: str = None, results_csv: str = None):
    input_path = Path(input_csv)
    if not input_path.exists():
        sys.exit(f"Input file not found: {input_csv}")

    out_dir = out_dir or "output"
    results_csv = results_csv or "results.csv"

    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"name", "address", "phone", "niche"}
        missing = required - set(h.strip().lower() for h in (reader.fieldnames or []))
        if missing:
            sys.exit(f"CSV missing required columns: {missing}. "
                      f"Found columns: {reader.fieldnames}")
        for r in reader:
            rows.append({k.strip().lower(): v.strip() for k, v in r.items()})

    if not rows:
        sys.exit("No data rows found in CSV.")

    print(f"\nProcessing {len(rows)} business(es)...\n")

    results = []
    ok, failed = 0, 0

    for i, row in enumerate(rows, 1):
        name, address, phone, niche = row["name"], row["address"], row["phone"], row["niche"]
        print(f"[{i}/{len(rows)}] {name} ({niche})...", end=" ")

        niche_key = resolve_key(niche)
        if niche_key not in NICHE_CONTENT:
            print(f"SKIPPED — no content for niche '{niche}'")
            results.append({"name": name, "phone": phone, "niche": niche,
                             "slug": "", "status": "SKIPPED",
                             "path": "", "error": f"niche '{niche}' not in content library"})
            failed += 1
            continue

        try:
            path = build_site(name, address, phone, niche_key, out_dir=out_dir,
                               warn=lambda m: print(f"\n    {m}", end=""))
            print(f"OK -> {path}")
            results.append({"name": name, "phone": phone, "niche": niche,
                             "slug": path.parent.name, "status": "BUILT",
                             "path": str(path), "error": ""})
            ok += 1
        except Exception as e:
            print(f"FAILED — {e}")
            results.append({"name": name, "phone": phone, "niche": niche,
                             "slug": "", "status": "FAILED",
                             "path": "", "error": str(e)})
            failed += 1

    with open(results_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "phone", "niche", "slug", "status", "path", "error"])
        w.writeheader()
        w.writerows(results)

    print(f"\nDone. {ok} built, {failed} failed/skipped.")
    print(f"Results written to: {results_csv}")
    print(f"Sites written under: {out_dir}/")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Batch-generate landing pages from a CSV of leads.")
    ap.add_argument("input_csv", help="CSV with columns: name, address, phone, niche")
    ap.add_argument("--out-dir", default="output", help="Folder to write generated sites into")
    ap.add_argument("--results", default="results.csv", help="Output CSV summarizing what was built")
    args = ap.parse_args()
    run_batch(args.input_csv, args.out_dir, args.results)
