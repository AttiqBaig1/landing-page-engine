# -*- coding: utf-8 -*-
"""
app.py — Streamlit UI for the landing page engine.

Run locally:
    pip install streamlit requests pillow openpyxl --break-system-packages
    streamlit run app.py

Two things it does:
  1. Generate — upload a CSV (name, address, phone, niche) or add rows
     manually, click Generate, get a table of sites + download buttons.
  2. Publish — for any generated site, push it to your WordPress site
     as a Page via the REST API using an Application Password. You
     control this button; nothing publishes automatically.
"""
import io
import csv
import json
import re
import base64
import requests
import streamlit as st
import pandas as pd
from pathlib import Path

from generate_site import build_site, slugify
from niche_content import NICHE_CONTENT
from wp_format import scope_css, _build_gutenberg  # noqa: F401


def publish_one(site, wp_url, wp_user, wp_pw):
    """Publish a single generated site to WordPress as a brand-new page with a
    unique slug. Returns (ok: bool, message_or_link: str)."""
    import secrets
    from pathlib import Path as _Path
    path = _Path(site["path"])
    if not path.exists():
        return False, "file missing on disk"
    html = path.read_text(encoding="utf-8")
    gutenberg = _build_gutenberg(html)

    base_slug = site["slug"]
    unique_slug = base_slug

    def _taken(slug):
        try:
            chk = requests.get(
                f"{wp_url}/wp-json/wp/v2/pages",
                auth=(wp_user, wp_pw),
                params={"slug": slug, "status": "publish,draft,pending,private,future"},
                timeout=20,
            )
            return chk.status_code == 200 and bool(chk.json())
        except Exception:
            return False

    if _taken(unique_slug):
        for _ in range(8):
            cand = f"{base_slug}-{secrets.token_hex(2)}"
            if not _taken(cand):
                unique_slug = cand
                break

    payload = {"title": site["name"], "slug": unique_slug,
               "status": "publish", "content": gutenberg}
    try:
        resp = requests.post(f"{wp_url}/wp-json/wp/v2/pages",
                             auth=(wp_user, wp_pw), json=payload, timeout=30)
        if resp.status_code in (200, 201):
            return True, resp.json().get("link", "")
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, str(e)


st.set_page_config(page_title="Landing Page Engine", page_icon="🏗️", layout="wide")

OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

if "sites" not in st.session_state:
    st.session_state.sites = []  # list of dicts: name, phone, niche, slug, path, wp_url, wp_status

st.title("🏗️ Landing Page Engine")
st.caption("Everything on one page: connect WordPress, add businesses, "
           "then generate — publishing happens in the same click.")

# =====================================================================
# 0. WORDPRESS CONNECTION (used by both the one-click flow below and
#    the manual publish section further down)
# =====================================================================
with st.expander("🔌 WordPress connection", expanded=not st.session_state.get("wp_url")):
    st.caption("Uses the WordPress REST API with an Application Password. "
               "Nothing is sent anywhere until you click a Generate or Publish button.")
    with st.form("wp_creds"):
        wp_url_in = st.text_input("WordPress site URL", placeholder="https://yourdomain.com",
                                   value=st.session_state.get("wp_url", ""))
        wp_user_in = st.text_input("WordPress username", value=st.session_state.get("wp_user", ""))
        wp_app_pw_in = st.text_input("Application Password", type="password",
                                      help="WP Admin → Users → Profile → Application Passwords")
        saved = st.form_submit_button("Save credentials for this session")
    if saved:
        st.session_state["wp_url"] = wp_url_in.rstrip("/")
        st.session_state["wp_user"] = wp_user_in
        st.session_state["wp_app_pw"] = wp_app_pw_in
        st.success("Saved for this session (not stored on disk).")
    if st.session_state.get("wp_url"):
        st.caption(f"Connected to: {st.session_state['wp_url']}")

# =====================================================================
# 1. GENERATE  (+ publish in the same click, optionally)
# =====================================================================
st.header("1️⃣ Generate Sites")
if True:
    st.subheader("Add businesses")
    available = sorted(NICHE_CONTENT.keys())
    st.info(f"**{len(available)} niches ready:** " + ", ".join(available))

    method = st.radio("Input method", ["Upload CSV", "Manual entry"], horizontal=True)

    rows_to_build = []

    if method == "Upload CSV":
        st.caption("CSV columns required: `name, address, phone, niche` — address format: `City, ST`")
        up = st.file_uploader("Upload leads CSV", type=["csv"])
        if up:
            df = pd.read_csv(up)
            df.columns = [c.strip().lower() for c in df.columns]
            missing = {"name", "address", "phone", "niche"} - set(df.columns)
            if missing:
                st.error(f"CSV is missing columns: {missing}")
            else:
                st.dataframe(df, width="stretch")
                rows_to_build = df.to_dict("records")

    else:
        st.caption("Add one or more rows, then click Generate below.")
        n_rows = st.number_input("How many businesses?", min_value=1, max_value=50, value=1)
        manual_rows = []
        for i in range(int(n_rows)):
            c1, c2, c3, c4 = st.columns([2, 2, 1.4, 1.6])
            with c1:
                nm = st.text_input(f"Name #{i+1}", key=f"nm{i}")
            with c2:
                ad = st.text_input(f"Address (City, ST) #{i+1}", key=f"ad{i}")
            with c3:
                ph = st.text_input(f"Phone #{i+1}", key=f"ph{i}")
            with c4:
                nc = st.selectbox(f"Niche #{i+1}", available, key=f"nc{i}")
            if nm and ad and ph:
                manual_rows.append({"name": nm, "address": ad, "phone": ph, "niche": nc})
        rows_to_build = manual_rows

    st.divider()

    creds_ok = all(st.session_state.get(k) for k in ("wp_url", "wp_user", "wp_app_pw"))
    also_publish = st.checkbox(
        "Also publish to WordPress right after generating (one click, no separate step)",
        value=creds_ok, disabled=not creds_ok,
        help="Uses the WordPress connection saved above. Untick this to only "
             "generate the sites locally and publish later from step 3.",
    )
    if not creds_ok:
        st.caption("Connect WordPress above to enable one-click publishing.")

    btn_label = "🚀 Generate & Publish to WordPress" if also_publish else "🚀 Generate Sites"
    if st.button(btn_label, type="primary", disabled=not rows_to_build):
        progress = st.progress(0, text="Starting...")
        results = []
        total = len(rows_to_build)
        wp_url = st.session_state.get("wp_url")
        wp_user = st.session_state.get("wp_user")
        wp_pw = st.session_state.get("wp_app_pw")

        for i, row in enumerate(rows_to_build):
            name, address, phone, niche = row["name"], row["address"], row["phone"], row["niche"]
            step_label = f"Building {name}..."
            progress.progress(i / total, text=step_label)
            niche_key = str(niche).lower().strip().replace(" ", "_").replace("-", "_")
            if niche_key not in NICHE_CONTENT:
                results.append({"name": name, "phone": phone, "niche": niche,
                                 "slug": "", "path": "", "status": "SKIPPED — no content for this niche",
                                 "wp_status": ""})
                continue
            try:
                path = build_site(name, address, phone, niche_key, out_dir=str(OUT_DIR), warn=lambda m: None)
                row_result = {"name": name, "phone": phone, "niche": niche,
                               "slug": path.parent.name, "path": str(path), "status": "✅ Built",
                               "wp_status": ""}
                # One-click publish: right after this site builds, push it live
                # too, so there is no separate "now go click Publish" step.
                if also_publish and creds_ok:
                    progress.progress(i / total, text=f"Publishing {name}...")
                    site_for_publish = {"name": name, "slug": path.parent.name, "path": str(path)}
                    ok_flag, msg = publish_one(site_for_publish, wp_url, wp_user, wp_pw)
                    row_result["wp_status"] = f"✅ Live: {msg}" if ok_flag else f"❌ {msg}"
                results.append(row_result)
            except Exception as e:
                results.append({"name": name, "phone": phone, "niche": niche,
                                 "slug": "", "path": "", "status": f"❌ {e}", "wp_status": ""})
        progress.progress(1.0, text="Done")
        st.session_state.sites = results

        built_n = sum(1 for r in results if r["status"].startswith("✅"))
        if also_publish and creds_ok:
            pub_n = sum(1 for r in results if r["wp_status"].startswith("✅"))
            st.success(f"Built {built_n} of {total} sites — published {pub_n} of {built_n} to WordPress.")
            failed_pub = [r for r in results if r["status"].startswith("✅") and r["wp_status"].startswith("❌")]
            if failed_pub:
                st.warning(f"{len(failed_pub)} site(s) built but failed to publish — "
                           "see the Status column, or retry them in step 3 below.")
        else:
            st.success(f"Built {built_n} of {total} sites.")

    if st.session_state.sites:
        st.subheader("Results")
        df_res = pd.DataFrame(st.session_state.sites)
        st.dataframe(df_res, width="stretch")
        csv_buf = io.StringIO()
        df_res.to_csv(csv_buf, index=False)
        st.download_button("⬇️ Download results.csv", csv_buf.getvalue(), "results.csv", "text/csv")

st.divider()

# =====================================================================
# 2. PREVIEW & DOWNLOAD
# =====================================================================
st.header("2️⃣ Preview & Download")
if True:
    st.subheader("Preview & download individual sites")
    if not st.session_state.sites:
        st.info("Generate some sites in step 1 above first.")
    else:
        built = [s for s in st.session_state.sites if s["status"].startswith("✅")]
        if not built:
            st.warning("No successfully built sites yet.")
        for idx, s in enumerate(built):
            with st.expander(f"📄 {s['name']} — {s['niche']}"):
                path = Path(s["path"])
                if path.exists():
                    html = path.read_text(encoding="utf-8")
                    # A bulk list often repeats a business name, so slugs are not
                    # unique. Streamlit needs a unique widget key, so pair the
                    # slug with the row index.
                    st.download_button("⬇️ Download index.html", html, f"{s['slug']}.html",
                                        "text/html", key=f"dl_{idx}_{s['slug']}")
                    with st.container(height=500):
                        # st.components.v1.html is deprecated in favour of
                        # st.iframe. st.iframe treats a string that isn't a
                        # URL/data-URI as raw HTML and embeds it directly.
                        st.iframe(src=html, height=480)

st.divider()

# =====================================================================
# 3. PUBLISH TO WORDPRESS  (manual / re-publish / bulk — the one-click
#    path in step 1 already publishes automatically if you ticked the
#    box, so this section is mainly for re-publishing or for sites you
#    generated without publishing at the time)
# =====================================================================
st.header("3️⃣ Publish to WordPress")
if True:
    st.subheader("Publish (manual / bulk)")
    st.caption("Use this if you generated sites without publishing them, or want to "
               "re-publish. WordPress credentials are set in the panel above.")

    st.divider()

    if not st.session_state.sites:
        st.info("Generate sites in step 1 above first.")
    else:
        built = [s for s in st.session_state.sites if s["status"].startswith("✅")]
        creds_ok = all(st.session_state.get(k) for k in ("wp_url", "wp_user", "wp_app_pw"))

        # -------- Publish ALL --------
        st.markdown(f"**{len(built)} site(s) ready to publish.**")
        cbtn, cinfo = st.columns([1, 3])
        with cbtn:
            publish_all = st.button("🚀 Publish ALL", type="primary", disabled=not creds_ok)
        with cinfo:
            if not creds_ok:
                st.caption("Save WordPress credentials above to enable publishing.")
            else:
                st.caption("Creates a new page with a unique URL for every site.")

        if publish_all and creds_ok:
            wp_url = st.session_state["wp_url"]
            wp_user = st.session_state["wp_user"]
            wp_pw = st.session_state["wp_app_pw"]
            prog = st.progress(0.0, text="Starting…")
            done = ok = 0
            total = len(built)
            for s in built:
                ok_flag, msg = publish_one(s, wp_url, wp_user, wp_pw)
                for r in st.session_state.sites:
                    if r["path"] == s["path"]:
                        r["wp_status"] = f"✅ Live: {msg}" if ok_flag else f"❌ {msg}"
                done += 1
                ok += 1 if ok_flag else 0
                prog.progress(done / total, text=f"Published {done}/{total} — {s['name'][:30]}")
            prog.progress(1.0, text=f"Done: {ok}/{total} published")
            st.success(f"Finished: {ok} of {total} published.")
            if ok < total:
                st.warning(f"{total - ok} failed — see the status column below.")

        st.divider()

        # -------- Per-site status + individual publish --------
        for idx, s in enumerate(built):
            c1, c2, c3 = st.columns([3, 3, 1])
            with c1:
                st.write(f"**{s['name']}** — {s['niche']}")
            with c2:
                st.write(s.get("wp_status", "Not published"))
            with c3:
                if st.button("Publish", key=f"pub_{idx}_{s['slug']}", disabled=not creds_ok):
                    if not creds_ok:
                        st.error("Save WordPress credentials above first.")
                    else:
                        ok_flag, msg = publish_one(
                            s, st.session_state["wp_url"],
                            st.session_state["wp_user"], st.session_state["wp_app_pw"])
                        for r in st.session_state.sites:
                            if r["path"] == s["path"]:
                                r["wp_status"] = f"✅ Live: {msg}" if ok_flag else f"❌ {msg}"
                        if ok_flag:
                            st.success(f"Published: {msg}")
                        else:
                            st.error(f"Failed: {msg}")
                        st.rerun()

    st.divider()
    live_sites = [s for s in st.session_state.sites if s.get("wp_status", "").startswith("✅")]
    if live_sites:
        st.subheader("Live URLs")
        st.dataframe(pd.DataFrame(live_sites)[["name", "niche", "wp_status"]], width="stretch")
