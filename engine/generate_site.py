# -*- coding: utf-8 -*-
"""
generate_site.py
----------------
Core engine. Takes one business (name, address, phone, niche) and
produces a complete, self-contained index.html.

STRUCTURE is the "Summit Roofing" reference layout for EVERY niche:
  top bar -> nav -> mobile drawer -> hero (bg image + stats aside)
  -> mobile stats -> services -> about -> service areas -> projects
  -> reviews -> FAQ -> CTA -> contact -> footer -> floating call

Only the ACCENT COLOURS change per niche family (see theme.py):
  orange = trades/dark, green = outdoor, blue = cleaning.

Supports both US ("Fresno, CA") and Canadian ("Kitchener, ON") addresses.

Usage:
    from generate_site import build_site
    build_site("R&R Roofing", "Kitchener, ON", "(519) 555-0123", "roofing",
               out_dir="output")
"""
import re
import io
import base64
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

from niche_content import get_niche
from cities import nearby_areas, find_city
from images import pick_images, has_photos
from theme import get_theme, apply_theme_canvas
from icons import icon as _icon

ROOT = Path(__file__).parent
OUT_DEFAULT = ROOT.parent / "output"

# Pre-compiled utility CSS — replaces the Tailwind CDN <script>, which
# WordPress strips when publishing as a Custom HTML block.
BASE_CSS = (ROOT / "base_css.txt").read_text(encoding="utf-8")

# Canadian province codes -> used to switch county/province wording.
CA_PROVINCES = {"ON", "QC", "BC", "AB", "MB", "SK", "NS", "NB", "NL", "PE", "NT", "YT", "NU"}

# Wording that changes with the kind of business. Home-service niches use
# "home" (the original wording); clinics, professional offices, salons, pet
# and care services and auto shops get CTA buttons, reviews and trust lines
# that fit them. A niche picks one with the `profile` key (default "home").
PROFILES = {
    "home":   {"cta": "Get a Free Quote", "cta_short": "Free Quote", "trust": "Licensed &amp; Insured",
               "form_note": "Fill out the form for a <strong>free, no-obligation estimate</strong>. We respond within 24 hours.",
               "title_tail": "Free Quotes", "team_alt": "crew working", "area_note": "Same crew, same pricing, no travel fees.",
               "work": "Projects", "kinds": ["Residential", "Emergency", "Commercial"]},
    "auto":   {"cta": "Get a Free Quote", "cta_short": "Free Quote", "trust": "Certified &amp; Insured",
               "form_note": "Tell us about your vehicle for a <strong>free, no-obligation quote</strong>. We respond within 24 hours.",
               "title_tail": "Free Quotes", "team_alt": "technicians working", "area_note": "Same team, same pricing, wherever you are.",
               "work": "Work", "kinds": ["Cars", "Trucks", "Fleet"]},
    "clinic": {"cta": "Book an Appointment", "cta_short": "Book Now", "trust": "Licensed Professionals",
               "form_note": "Send your details and we'll call to <strong>confirm a time that suits you</strong>. New patients welcome.",
               "title_tail": "Book Today", "team_alt": "team caring for patients", "area_note": "Convenient for patients across the area.",
               "work": "Clinic", "kinds": ["Care", "Treatment", "Follow-Up"]},
    "pro":    {"cta": "Get a Free Consultation", "cta_short": "Free Consult", "trust": "Licensed Professionals",
               "form_note": "Tell us what you need for a <strong>free, confidential consultation</strong>. We respond within one business day.",
               "title_tail": "Free Consultation", "team_alt": "team meeting a client", "area_note": "In-person and virtual appointments available.",
               "work": "Work", "kinds": ["Clients", "Cases", "Results"]},
    "beauty": {"cta": "Book Your Appointment", "cta_short": "Book Now", "trust": "Licensed Professionals",
               "form_note": "Send your details and we'll <strong>confirm your appointment</strong>. Walk-ins welcome when we have space.",
               "title_tail": "Book Online", "team_alt": "team at work", "area_note": "Easy to reach from across the area.",
               "work": "Work", "kinds": ["Before", "After", "Studio"]},
    "care":   {"cta": "Book Now", "cta_short": "Book Now", "trust": "Insured &amp; Background-Checked",
               "form_note": "Send your details and we'll <strong>get you booked in</strong>. We respond within 24 hours.",
               "title_tail": "Book Today", "team_alt": "team at work", "area_note": "Same friendly team, wherever you are.",
               "work": "Work", "kinds": ["Happy Clients", "Daily Care", "Specials"]},
}

REVIEW_POOLS = {
    "clinic": [("Friendly staff, no long wait, and everything was explained clearly before anything was done.", "MK", "Michael K."),
               ("Got in the same week. They actually listened, and the follow-up call was a nice touch.", "SR", "Sarah R."),
               ("Upfront about costs and insurance from the start. Felt looked after the whole time.", "DT", "David T.")],
    "pro":    [("Explained my options in plain English and never pushed. Answered every call and email.", "MK", "Michael K."),
               ("Responsive, organised and upfront about fees. I knew exactly where things stood at each step.", "SR", "Sarah R."),
               ("Took a stressful situation off my plate. Professional from the first call to the end.", "DT", "David T.")],
    "beauty": [("Booked in quickly, on time, and the result was exactly what I asked for. Already rebooked.", "MK", "Michelle K."),
               ("Clean, relaxing and really skilled. They took the time to understand what I wanted.", "SR", "Sarah R."),
               ("Fair prices and great attention to detail. Best experience I've had in town.", "DT", "Dana T.")],
    "care":   [("Reliable, kind and always on time. We trust them completely.", "MK", "Michael K."),
               ("They answered right away and fit us in fast. Great communication the whole way.", "SR", "Sarah R."),
               ("Upfront pricing and they genuinely care. Highly recommend.", "DT", "David T.")],
}

# Generic review templates — city names get filled in; work for any niche.
REVIEW_POOL = [
    ("Same crew showed up every time, always upfront about pricing. No surprises on the final invoice.",
     "MK", "Michael K."),
    ("Called two other places first — these guys actually answered, showed up when they said, and did it right.",
     "SR", "Sarah R."),
    ("Quoted a flat price and that's exactly what we paid. Walked me through everything before starting.",
     "DT", "David T."),
]

# Service-name keyword -> Iconify icon (reference uses lucide).
ICON_MAP = [
    ("inspect", "lucide:search"), ("estimate", "lucide:clipboard-list"),
    ("replace", "lucide:home"), ("repair", "lucide:wrench"),
    ("storm", "lucide:cloud-lightning"), ("hail", "lucide:cloud-hail"),
    ("emergency", "lucide:siren"), ("gutter", "lucide:droplets"),
    ("slate", "lucide:layers"), ("tile", "lucide:layers"),
    ("commercial", "lucide:building-2"), ("install", "lucide:hammer"),
    ("design", "lucide:pen-tool"), ("hardscap", "lucide:brick-wall"),
    ("patio", "lucide:brick-wall"), ("irrigation", "lucide:sprout"),
    ("sprinkler", "lucide:sprout"), ("plant", "lucide:flower-2"),
    ("garden", "lucide:flower-2"), ("light", "lucide:lightbulb"),
    ("drain", "lucide:waves"), ("mow", "lucide:scissors"),
    ("lawn", "lucide:scissors"), ("fertil", "lucide:leaf"),
    ("weed", "lucide:leaf"), ("aerat", "lucide:wind"),
    ("tree", "lucide:trees"), ("stump", "lucide:axe"),
    ("trim", "lucide:scissors"), ("prun", "lucide:scissors"),
    ("fence", "lucide:fence"), ("gate", "lucide:door-open"),
    ("pest", "lucide:bug"), ("rodent", "lucide:mouse"),
    ("termite", "lucide:bug"), ("mosquito", "lucide:bug"),
    ("clean", "lucide:sparkles"), ("deep", "lucide:sparkles"),
    ("move", "lucide:package"), ("office", "lucide:briefcase"),
    ("carpet", "lucide:layers"), ("window", "lucide:app-window"),
    ("junk", "lucide:trash-2"), ("haul", "lucide:truck"),
    ("dumpster", "lucide:container"), ("cleanout", "lucide:box"),
    ("appliance", "lucide:washing-machine"), ("furniture", "lucide:armchair"),
    ("drain", "lucide:waves"), ("leak", "lucide:droplet"),
    ("water heater", "lucide:flame"), ("heater", "lucide:flame"),
    ("sewer", "lucide:waves"), ("pipe", "lucide:pipette"),
    ("furnace", "lucide:flame"), ("heating", "lucide:flame"),
    ("air condition", "lucide:snowflake"), ("cooling", "lucide:snowflake"),
    ("duct", "lucide:wind"), ("thermostat", "lucide:thermometer"),
    ("panel", "lucide:cpu"), ("wiring", "lucide:cable"),
    ("outlet", "lucide:plug"), ("electric", "lucide:zap"),
    ("generator", "lucide:battery-charging"), ("ev charger", "lucide:plug-zap"),
    ("garage", "lucide:door-open"), ("opener", "lucide:remote"),
    ("spring", "lucide:settings"), ("tarp", "lucide:umbrella"),
    ("board", "lucide:panel-top"), ("restoration", "lucide:hammer"),
    ("insurance", "lucide:file-check"), ("roof", "lucide:home"),
    ("maintenance", "lucide:settings"), ("guard", "lucide:shield"),
]


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[\s_]+", "-", s)


def clean_phone(phone: str) -> str:
    d = re.sub(r"\D", "", phone)
    return d if d.startswith("1") else "1" + d


# Valid US state + Canadian province codes, used to locate the region token
# no matter where it sits in a messy address.
_REGION_CODES = {
    # US
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","DC",
    # Canada
    "ON","QC","BC","AB","MB","SK","NS","NB","NL","PE","NT","YT","NU",
}


def parse_address(address: str):
    """Pull (city, state/province) out of whatever address the user typed.

    Works with all of these:
        'Fresno, CA'                         'Fresno CA 93721'
        'Fresno'            (state looked up from the city database)
        'Street 1, Fresno'  /  'Street 1 Fresno CA'  (street is ignored)
        '143 Shawcliffe Cir SW, Calgary, AB T2Y 1J5'
        'Fresno, California'                 (full state names too)

    The street part never ends up in the H1: the city is matched against the
    27,000-city database, taking the words right before the state.
    """
    from cities import lookup_city, state_names, city_index, norm_city

    text = (address or "").strip()
    if not text:
        raise ValueError("Address is empty — give at least a city, e.g. 'Fresno, CA'")

    # Words with the comma-group each belongs to.
    groups = [g.strip() for g in text.split(",") if g.strip()]
    words = []                      # (word, group_no, last_alpha_in_group)
    for gi, grp in enumerate(groups):
        ws = grp.replace("-", " ").split()
        alpha_pos = [k for k, w in enumerate(ws) if re.sub(r"[^A-Za-z]", "", w) and not any(ch.isdigit() for ch in w)]
        last_alpha = alpha_pos[-1] if alpha_pos else -1
        for k, w in enumerate(ws):
            words.append((w, gi, k == last_alpha))

    # 1) Find the state: full name ('New York') or 2-letter code, scanning
    #    right-to-left. Quadrants (NE/NW/SE/SW) only count if nothing else does.
    snames = state_names()
    state, state_at = None, None
    quadrant_hit = None
    for i in range(len(words) - 1, -1, -1):
        for L in (3, 2):            # 'british columbia', 'new york', 'district of columbia'
            if i - L + 1 >= 0:
                phrase = " ".join(re.sub(r"[^A-Za-z]", "", w).lower() for w, _, _ in words[i - L + 1:i + 1])
                if phrase in snames:
                    state, state_at = snames[phrase], i - L + 1
                    break
        if state:
            break
        w, gi, last_alpha = words[i]
        if any(ch.isdigit() for ch in w):
            continue
        code = re.sub(r"[^A-Za-z]", "", w)
        if len(code) == 2 and code.upper() in _REGION_CODES and (code.isupper() or last_alpha):
            if code.upper() in {"NE", "NW", "SE", "SW"} and i > 0 and words[i - 1][1] == gi:
                quadrant_hit = quadrant_hit or (code.upper(), i)
                continue
            state, state_at = code.upper(), i
            break
        if len(code) > 2 and code.lower() in snames:
            state, state_at = snames[code.lower()], i
            break
    if state is None and quadrant_hit:
        state, state_at = quadrant_hit

    # 2) Candidate words for the city: everything before the state, minus
    #    numbers / postal codes.
    before = words[:state_at] if state_at is not None else words
    cand = [w for w, _, _ in before if not any(ch.isdigit() for ch in w)]
    cand = [re.sub(r"[^A-Za-z.'’ ]", "", w) for w in cand]
    cand = [w for w in cand if w]

    # 3) Longest run of words ending right before the state that is a real city.
    idx = city_index()
    for end in range(len(cand), 0, -1):
        for L in range(min(5, end), 0, -1):
            name = " ".join(cand[end - L:end])
            rows = idx.get(norm_city(name), [])
            if state:
                rows = [c for c in rows if c["state"] == state]
            if rows:
                return rows[0]["city"], rows[0]["state"]
        if state:      # only look at the words directly before the state
            break

    # 4) Not in the database. Use the comma-group right before the state
    #    (street groups contain digits / street words, so skip those).
    if state:
        prev_groups = sorted({gi for _, gi, _ in before}, reverse=True)
        for gi in prev_groups:
            grp_words = [w for w, g, _ in before if g == gi]
            if any(any(ch.isdigit() for ch in w) for w in grp_words):
                continue
            city = " ".join(grp_words).strip()
            if city:
                return city.title() if city.islower() or city.isupper() else city, state
        if cand:
            return cand[-1].title(), state
        raise ValueError(f"Couldn't find a city in '{address}' — write it like 'Fresno, CA'")

    raise ValueError(f"City not recognised in '{address}' — add the state, e.g. 'Fresno, CA'")


def unescape(s: str) -> str:
    """niche_content stores &amp; — undo for JSON-LD / meta / <option>."""
    return (s.replace("&amp;", "&").replace("&quot;", '"')
             .replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">"))


def json_escape(s: str) -> str:
    return unescape(s).replace("\\", "\\\\").replace('"', '\\"')


def pick_icon(slug_s: str, sname: str) -> str:
    hay = f"{slug_s} {sname}".lower()
    for key, icon in ICON_MAP:
        if key in hay:
            return icon
    return "lucide:wrench"


def img_to_datauri(path: Path, max_w: int = 1200, quality: int = 72) -> str:
    """Resize + compress before embedding — never embed a raw original."""
    if not path or not Path(path).exists():
        return ""
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)
        if im.mode != "RGB":
            im = im.convert("RGB")
        if im.width > max_w:
            new_h = int(im.height * (max_w / im.width))
            im = im.resize((max_w, new_h), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"  ! image encode failed for {Path(path).name}: {e}")
        return ""


# ---------------------------------------------------------------------------
# WordPress hardening
# ---------------------------------------------------------------------------
# Two things go wrong when this HTML is pasted into a WordPress page:
#
#   1. The editor HTML-escapes characters inside <style> (notably `>`), which
#      kills every rule after that point — taking the reset with it. That is
#      why blue links and grey FAQ buttons kept coming back. We now emit no
#      `>` in CSS at all, but belt-and-braces:
#   2. Theme rules carrying an id (`#main .entry-content a`) outrank any class
#      selector we write, even with !important.
#
# The one thing a theme can never beat and an editor never rewrites is an
# inline style attribute. So after the page is built we stamp the handful of
# properties that themes actually clobber directly onto the elements.

_INLINE_FIXES = [
    (re.compile(r'<a (?![^>]*\bstyle=)'), '<a style="color:inherit;text-decoration:none" '),
    (re.compile(r'<button (?![^>]*\bstyle=)'),
     '<button style="background:none;border:0;color:inherit;font:inherit;padding:0;cursor:pointer;text-align:inherit" '),
    (re.compile(r'<ol (?![^>]*\bstyle=)'), '<ol style="list-style:none;margin:0;padding:0" '),
    (re.compile(r'<ul (?![^>]*\bstyle=)'), '<ul style="list-style:none;margin:0;padding:0" '),
    (re.compile(r'<li (?![^>]*\bstyle=)'), '<li style="list-style:none" '),
    (re.compile(r'<li>'), '<li style="list-style:none">'),
]


def harden_for_wordpress(html: str) -> str:
    """Stamp theme-proof inline styles onto links, buttons and lists."""
    body_start = html.index('<body')
    head, body = html[:body_start], html[body_start:]
    for pattern, replacement in _INLINE_FIXES:
        body = pattern.sub(replacement, body)
    # Merge our defaults into elements that already carry a style attribute,
    # so an existing style= never means "no reset".
    body = re.sub(r'<a style="(?!color:inherit)', '<a style="color:inherit;text-decoration:none;', body)
    return head + body



def html_attr(s: str) -> str:
    """Escape a value for use inside an HTML attribute or text node.
    Business names legitimately contain & and ' (e.g. "Bob & Son's"), which
    must not go into <title>/<meta content=""> raw."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------------------
# SERVICE AREAS section: headline + coverage stats on the left, a radar map
# that plots every nearby city at its real bearing and distance on the right,
# then city cards with distance and drive time, then a "don't see your town"
# call-to-action strip. Colours come from the niche palette via CSS variables
# set on the section, so it works the same standalone and inside WordPress.
# ---------------------------------------------------------------------------
SERVICE_AREA_CSS = """
        .sa { position: relative; overflow: hidden; padding: 6.5rem 0; border-top: 1px solid rgba(38,38,38,0.5); }
        .sa::before { content: ""; position: absolute; inset: 0; pointer-events: none;
            background: radial-gradient(700px 420px at 78% 38%, color-mix(in srgb, var(--sa-acc) 16%, transparent), transparent 70%),
                        radial-gradient(520px 360px at 8% 90%, color-mix(in srgb, var(--sa-acc2) 9%, transparent), transparent 70%); }
        .sa > div { position: relative; }
        .sa-top { display: grid; gap: 3rem; align-items: center; }
        @media (min-width: 1024px) { .sa-top { grid-template-columns: 1fr 1.05fr; gap: 4rem; } }
        .sa-title { font-size: clamp(2rem, 4.2vw, 3.25rem); line-height: 1.05; font-weight: 800; letter-spacing: -0.03em; color: #fff; margin: 1rem 0 1.25rem; text-wrap: balance; }
        .sa-title .sa-hl { background: linear-gradient(90deg, var(--sa-acc2), var(--sa-acc)); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .sa-lead { color: #a8a29e; font-size: 1.05rem; line-height: 1.7; max-width: 34rem; margin: 0; }
        .sa-lead strong { color: #fff; font-weight: 600; }
        .sa-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .75rem; margin: 2rem 0; max-width: 34rem; }
        .sa-stat { border: 1px solid rgba(38,38,38,0.5); background: rgba(23,23,23,0.2); border-radius: 1rem; padding: 1rem .9rem; }
        .sa-stat b { display: block; font-size: 1.9rem; line-height: 1; font-weight: 800; color: var(--sa-acc2); font-variant-numeric: tabular-nums; }
        .sa-stat span { display: block; margin-top: .45rem; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: #78716c; font-weight: 600; }
        @media (max-width: 480px) { .sa-stat { padding: .85rem .7rem; } .sa-stat b { font-size: 1.5rem; } .sa-stat span { font-size: .58rem; letter-spacing: .06em; } }
        .sa-actions { display: flex; flex-wrap: wrap; gap: .75rem; }
        .sa-btn { display: inline-flex; align-items: center; gap: .6rem; padding: .95rem 1.4rem; border-radius: .75rem; font-weight: 700; font-size: .9rem; color: #fff; text-decoration: none; transition: transform .2s, box-shadow .2s, background .2s; }
        .sa-btn-main { background: var(--sa-acc); box-shadow: 0 14px 34px -14px var(--sa-acc); }
        .sa-btn-main:hover { transform: translateY(-2px); box-shadow: 0 18px 40px -12px var(--sa-acc); }
        .sa-btn-ghost { border: 1px solid #404040; background: rgba(255,255,255,.04); }
        .sa-btn-ghost:hover { border-color: var(--sa-acc2); }

        .sa-radar { position: relative; aspect-ratio: 1 / 1; width: 100%; max-width: 560px; margin: 0 auto; border-radius: 50%;
            background: radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--sa-acc) 12%, transparent) 0%, rgba(10,10,10,0.0) 70%);
            box-shadow: inset 0 0 0 1px rgba(38,38,38,0.5), 0 30px 80px -40px var(--sa-acc); }
        .sa-radar svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
        .sa-sweep { position: absolute; inset: 0; border-radius: 50%; pointer-events: none;
            background: conic-gradient(from 0deg, transparent 0deg, color-mix(in srgb, var(--sa-acc2) 26%, transparent) 40deg, transparent 75deg);
            animation: saSpin 7s linear infinite; mask: radial-gradient(circle, #000 0 69.5%, transparent 70%); -webkit-mask: radial-gradient(circle, #000 0 69.5%, transparent 70%); }
        @keyframes saSpin { to { transform: rotate(360deg); } }
        .sa-dot { animation: saPop .6s ease-out both; transform-box: fill-box; transform-origin: center; }
        @keyframes saPop { from { opacity: 0; transform: scale(.3); } to { opacity: 1; transform: scale(1); } }
        .sa-pulse { animation: saPulse 2.4s ease-out infinite; transform-box: fill-box; transform-origin: center; }
        @keyframes saPulse { 0% { opacity: .65; transform: scale(.6); } 100% { opacity: 0; transform: scale(2.6); } }
        .sa-label { font: 600 11px Inter, system-ui, sans-serif; fill: #e7e5e4; paint-order: stroke; stroke: rgba(10,10,10,0.85); stroke-width: 3px; }
        .sa-ring-label { font: 500 9px Inter, system-ui, sans-serif; fill: #78716c; letter-spacing: .08em; }

        .sa-cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .9rem; margin-top: 3.5rem; }
        @media (min-width: 640px) { .sa-cards { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
        @media (min-width: 1024px) { .sa-cards { grid-template-columns: repeat(5, minmax(0, 1fr)); } }
        .sa-card { position: relative; display: flex; flex-direction: column; gap: .35rem; padding: 1.1rem 1.1rem 1rem; border-radius: 1rem; text-decoration: none;
            border: 1px solid rgba(38,38,38,0.5); background: rgba(23,23,23,0.2); transition: transform .25s, border-color .25s, background .25s; overflow: hidden; }
        .sa-card::after { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: linear-gradient(var(--sa-acc2), var(--sa-acc)); opacity: .35; transition: opacity .25s; }
        .sa-card:hover { transform: translateY(-3px); border-color: color-mix(in srgb, var(--sa-acc2) 55%, transparent); background: color-mix(in srgb, var(--sa-acc) 9%, transparent); }
        .sa-card:hover::after { opacity: 1; }
        .sa-card-top { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
        .sa-chip { font-size: .66rem; font-weight: 700; letter-spacing: .06em; padding: .2rem .5rem; border-radius: 999px; color: var(--sa-acc2); background: color-mix(in srgb, var(--sa-acc) 16%, transparent); white-space: nowrap; }
        .sa-card-name { font-size: 1rem; font-weight: 700; color: #fff; line-height: 1.25; }
        .sa-card-meta { font-size: .74rem; color: #78716c; display: flex; align-items: center; gap: .35rem; }
        .sa-card-go { position: absolute; right: .9rem; bottom: .9rem; opacity: 0; transform: translateX(-4px); transition: opacity .25s, transform .25s; }
        .sa-card:hover .sa-card-go { opacity: 1; transform: none; }
        .sa-card.sa-hq { border-color: color-mix(in srgb, var(--sa-acc2) 60%, transparent); background: linear-gradient(150deg, color-mix(in srgb, var(--sa-acc) 22%, transparent), rgba(23,23,23,0.2)); }
        .sa-card.sa-hq::after { opacity: 1; }

        .sa-foot { margin-top: 1.5rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.15rem 1.35rem;
            border-radius: 1rem; border: 1px dashed color-mix(in srgb, var(--sa-acc2) 45%, transparent); background: color-mix(in srgb, var(--sa-acc) 7%, transparent); }
        .sa-foot p { margin: 0; color: #d6d3d1; font-size: .95rem; }
        .sa-foot p b { color: #fff; }
        @media (prefers-reduced-motion: reduce) { .sa-sweep, .sa-pulse, .sa-dot { animation: none !important; } }
"""


def _sa_drive_minutes(miles):
    return max(5, round(miles * 1.35 + 4))


def build_service_areas(name, city, state, region, kw, phone, tel, areas, P, ACC, ACC2, ACCD, _icon):
    from cities import find_city
    import math as _m

    src = find_city(city, state)
    pts = [a for a in areas if "lat" in a]
    max_mi = max([a["miles"] for a in pts] + [5])
    ring_mi = max(5, int(_m.ceil(max_mi * 1.12 / 5.0) * 5))     # outer ring, rounded up to 5 mi
    counties = {a.get("county") for a in areas if a.get("county")}
    n_comm = len(areas) + 1

    # --- radar map (SVG, 400x400, centre 200,200, outer ring r=170) -----------
    C, R = 200, 170
    rings = ""
    for k, frac in enumerate((0.25, 0.5, 0.75, 1.0)):
        rr = R * frac
        dash = ' stroke-dasharray="3 5"' if frac < 1 else ""
        rings += (f'<circle cx="{C}" cy="{C}" r="{rr:.1f}" fill="none" stroke="#262626" '
                  f'stroke-width="1"{dash}/>')
        if frac > 0.25:   # the innermost ring is too close to the HQ label
            rings += (f'<text x="{C + rr * 0.7071 + 4:.1f}" y="{C + rr * 0.7071 + 10:.1f}" '
                      f'class="sa-ring-label">{round(ring_mi * frac)} MI</text>')
    axes = (f'<line x1="{C - R}" y1="{C}" x2="{C + R}" y2="{C}" stroke="#262626" stroke-width="1"/>'
            f'<line x1="{C}" y1="{C - R}" x2="{C}" y2="{C + R}" stroke="#262626" stroke-width="1"/>'
            f'<text x="{C}" y="{C - R - 8}" text-anchor="middle" class="sa-ring-label" style="fill:{ACC2}">N</text>')

    placed = []
    if src:
        cos0 = _m.cos(_m.radians(src["lat"]))
        for a in pts:
            dx = (a["lon"] - src["lon"]) * 69.0 * cos0
            dy = (a["lat"] - src["lat"]) * 69.0
            d = _m.hypot(dx, dy) or 1
            x = C + dx / d * (min(a["miles"], ring_mi) / ring_mi * R)
            y = C - dy / d * (min(a["miles"], ring_mi) / ring_mi * R)
            placed.append({"x": x, "y": y, "a": a})
    # simple label de-collision: labels sit to the outside of the dot,
    # then nudge vertically when two on the same side overlap
    def _box(p):
        w = 6.4 * len(p["a"]["city"]) + 4
        x0 = p["x"] + 9 if p["right"] else p["x"] - 9 - w
        return (x0, p["ly"] - 10, x0 + w, p["ly"] + 3)

    def _hits(b1, b2):
        return not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1])

    for p in placed:
        p["right"] = p["x"] >= C
        p["ly"] = p["y"] + 4
    # place labels one by one (closest to HQ first): try outside side, then the
    # other side, then small vertical nudges — so a label never drifts away
    # from its own dot.
    hq_w = 3.6 * max(len(city), 12) + 6
    done = [(C - hq_w, C + 16, C + hq_w, C + 48), (C - 15, C - 15, C + 15, C + 15)]
    done += [(p["x"] - 5, p["y"] - 5, p["x"] + 5, p["y"] + 5) for p in placed]
    for frac in (0.5, 0.75, 1.0):   # ring distance labels
        rx = C + R * frac * 0.7071 + 4
        done.append((rx, C + R * frac * 0.7071 + 1, rx + 34, C + R * frac * 0.7071 + 12))
    for p in sorted(placed, key=lambda q: q["a"]["miles"]):
        best = None
        for right in (p["right"], not p["right"]):
            for dy in (0, -8, 8, -15, 15, -22, 22):
                p["right"], p["ly"] = right, p["y"] + 4 + dy
                b = _box(p)
                if not any(_hits(b, q) for q in done) and 2 < b[0] and b[2] < 398:
                    best = (right, p["ly"]); break
            if best:
                break
        if best:
            p["right"], p["ly"] = best
            done.append(_box(p))
        else:
            p["hide"] = True        # no room: keep the dot, the city is still in the cards below
    dots = ""
    for i, p in enumerate(placed):
        lx = p["x"] + (9 if p["right"] else -9)
        anchor = "start" if p["right"] else "end"
        dots += (f'<g class="sa-dot" style="animation-delay:{0.15 + i * 0.08:.2f}s">'
                 f'<line x1="{C}" y1="{C}" x2="{p["x"]:.1f}" y2="{p["y"]:.1f}" stroke="{ACC2}" stroke-opacity=".18" stroke-width="1"/>'
                 f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="7" fill="{ACC}" fill-opacity=".18"/>'
                 f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="3.6" fill="{ACC2}"/>'
                 + ("" if p.get("hide") else
                    f'<text x="{lx:.1f}" y="{p["ly"]:.1f}" text-anchor="{anchor}" class="sa-label">{p["a"]["city"]}</text>')
                 + '<title>' + f'{p["a"]["city"]} &#8211; {p["a"]["miles"]} mi' + '</title></g>')
    hq = (f'<circle cx="{C}" cy="{C}" r="14" fill="{ACC2}" class="sa-pulse"/>'
          f'<circle cx="{C}" cy="{C}" r="11" fill="{ACC}"/>'
          f'<circle cx="{C}" cy="{C}" r="4.5" fill="#fff"/>'
          f'<text x="{C}" y="{C + 30}" text-anchor="middle" class="sa-label" style="font-size:13px;font-weight:800">{city}</text>'
          f'<text x="{C}" y="{C + 44}" text-anchor="middle" class="sa-ring-label" style="fill:{ACC2}">HEADQUARTERS</text>')
    radar = (f'<div class="sa-radar" role="img" aria-label="Map of {name} service area around {city}, {state}">'
             f'<div class="sa-sweep"></div>'
             f'<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{rings}{axes}{dots}{hq}</svg></div>')

    # --- city cards ------------------------------------------------------------------
    pin = _icon("lucide:map-pin", 13, ACC2)
    clock = _icon("lucide:clock", 12, "#78716c")
    go = _icon("lucide:arrow-up-right", 16, ACC2)
    cards = (f'<a href="#contact" class="sa-card sa-hq">'
             f'<div class="sa-card-top">{_icon("lucide:home", 15, ACC2)}<span class="sa-chip">HQ</span></div>'
             f'<span class="sa-card-name">{city}</span>'
             f'<span class="sa-card-meta">{_icon("lucide:zap", 12, ACC2)}Fastest response</span>'
             f'<span class="sa-card-go">{go}</span></a>')
    for a in areas:
        cards += (f'<a href="#contact" class="sa-card">'
                  f'<div class="sa-card-top">{pin}<span class="sa-chip">{a["miles"]} MI</span></div>'
                  f'<span class="sa-card-name">{a["city"]}</span>'
                  f'<span class="sa-card-meta">{clock}~{_sa_drive_minutes(a["miles"])} min drive</span>'
                  f'<span class="sa-card-go">{go}</span></a>')

    team = "same crew" if P.get("team_alt", "").startswith("crew") else "same team"
    lead = (f'<strong>{name}</strong> covers <strong>{city}</strong> and <strong>{n_comm - 1} neighbouring '
            f'communities</strong> across {region} &mdash; {team}, same pricing, no travel fees.'
            if areas else
            f'<strong>{name}</strong> serves <strong>{city}</strong> and all of {region} &mdash; {team}, same pricing, no travel fees.')
    if areas:
        stats = [(str(n_comm), "Communities"), (str(ring_mi), "Mile Radius"),
                 (str(len(counties)), "Counties" if len(counties) != 1 else "County")]
    else:   # city not in the database: no fake numbers
        stats = [("100%", "Local Team"), (str(ring_mi), "Mile Radius"), ("24/7", "Response")]
    stats_html = "".join(f'<div class="sa-stat"><b>{v}</b><span>{lbl}</span></div>' for v, lbl in stats)

    return f'''
    <!-- ==================== SERVICE AREAS ==================== -->
    <section id="service-areas" class="sa" aria-label="Service areas" style="--sa-acc:{ACC};--sa-acc2:{ACC2};--sa-accd:{ACCD}">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="sa-top">
                <div class="scroll-reveal">
                    <div class="eyebrow">{_icon("lucide:map", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">Service Areas</span></div>
                    <h2 class="sa-title">{kw} serving <span class="sa-hl">{city}</span> &amp; every town around it</h2>
                    <p class="sa-lead">{lead}</p>
                    <div class="sa-stats">
                        {stats_html}
                    </div>
                    <div class="sa-actions">
                        <a style="color:#fff;text-decoration:none" href="tel:+{tel}" class="sa-btn sa-btn-main">{_icon("lucide:phone", 16, "currentColor")}Call {phone}</a>
                        <a style="color:#fff;text-decoration:none" href="#contact" class="sa-btn sa-btn-ghost">{_icon("lucide:map-pin", 16, ACC2)}Check My Area</a>
                    </div>
                </div>
                <div class="scroll-reveal">{radar}</div>
            </div>
            <div class="sa-cards scroll-reveal">{cards}</div>
            <div class="sa-foot scroll-reveal">
                <p>{_icon("lucide:navigation", 15, ACC2)} <b>Don't see your town?</b> We cover all of {region} and nearby &mdash; just ask.</p>
                <a style="color:#fff;text-decoration:none;padding:.75rem 1.15rem" href="#contact" class="sa-btn sa-btn-main">{P["cta"]} {_icon("lucide:arrow-right", 15, "currentColor")}</a>
            </div>
        </div>
    </section>
'''


def build_site(name: str, address: str, phone: str, niche: str,
               out_dir=None, email: str = None, hours: str = "Mon–Sat: 7AM–7PM",
               warn=print) -> Path:
    """Builds one complete site. Returns path to the generated index.html."""
    niche_key = niche.lower().strip().replace(" ", "_").replace("-", "_")
    content = get_niche(niche_key)
    if content is None:
        from niche_content import NICHE_CONTENT
        raise ValueError(f"No content for niche '{niche}'. Available: {sorted(NICHE_CONTENT)}")

    T = get_theme(content["theme"])
    ACC, ACC2, ACCD = T["accent"], T["accent2"], T["accent_d"]
    RGB = T["accent_rgb"]
    g = T["hero_grad"]

    city, state = parse_address(address)
    is_ca = state in CA_PROVINCES
    rec = find_city(city, state)

    # In Canada the CSV stores the province in `county`; word it correctly.
    if rec:
        region = rec["county"] if is_ca else rec["county"] + " County"
        lat, lon = rec["lat"], rec["lon"]
    else:
        region = "the surrounding area"
        lat = lon = None
        warn(f"  ! '{city}, {state}' not found in the city database.")

    areas = nearby_areas(city, state, niche_key, n=9)
    if not areas:
        warn(f"  ! No nearby areas for {city}, {state} — area section will be sparse.")

    imgs = pick_images(name, niche_key)
    have_photos = has_photos(niche_key)
    if not have_photos:
        warn(f"  ! No photo library for '{niche_key}' — using CSS gradients instead.")

    slug = slugify(name)
    tel = clean_phone(phone)
    email = email or f"info@{slug.replace('-', '')}.com"
    brand = name.upper()
    logo = content.get("logo", "lucide:hard-hat")     # niche-specific brand mark
    audience = content.get("audience", "Homeowners")  # who the reviews speak for
    P = dict(PROFILES["home"], **PROFILES.get(content.get("profile", "home"), {}))
    CTA, CTA_SHORT = P["cta"], P["cta_short"]

    tagline   = content["tagline"]
    kw        = content["h1_keyword"]
    hook      = content["hero_hook"]
    hero_sub  = content["hero_sub"].format(city=city, county=region)
    about_b   = [p.format(city=city, county=region) for p in content["about_body"]]
    meta_desc = unescape(f"{name} — {kw} in {city}, {state}. {hook}. {hero_sub}")[:157]

    hero_img  = img_to_datauri(imgs["hero"],  1400, 70) if have_photos else ""
    about_img = img_to_datauri(imgs["about"],  800, 72) if have_photos else ""
    gal       = [img_to_datauri(p, 700, 70) for p in imgs["gallery"]] if have_photos else []
    gal       = [x for x in gal if x]

    # ---------------------------------------------------------- JSON-LD
    svc_ld = ",".join(
        f'{{"@type":"Offer","itemOffered":{{"@type":"Service","name":"{json_escape(s[1])}"}}}}'
        for s in content["services"])
    area_ld = ",".join(
        [f'{{"@type":"City","name":"{json_escape(city)}"}}'] +
        [f'{{"@type":"City","name":"{json_escape(a["city"])}"}}' for a in areas[:6]])
    faq_ld = ",".join(
        f'{{"@type":"Question","name":"{json_escape(q)}","acceptedAnswer":'
        f'{{"@type":"Answer","text":"{json_escape(a)}"}}}}'
        for q, a in content["faq"])
    geo_ld   = f',"geo":{{"@type":"GeoCoordinates","latitude":{lat},"longitude":{lon}}}' if lat else ""
    geo_meta = (f'\n    <meta name="geo.position" content="{lat};{lon}">'
                f'\n    <meta name="ICBM" content="{lat}, {lon}">') if lat else ""
    country = "CA" if is_ca else "US"

    # --------------------------------------------------------- SERVICES
    services_html = ""
    for s_slug, s_name, _old_svg, s_desc in content["services"]:
        # New-style entries name their Lucide icon directly ("lucide:..."),
        # older ones carry a raw SVG path and get a keyword-matched icon.
        icon = _old_svg if str(_old_svg).startswith("lucide:") else pick_icon(s_slug, s_name)
        services_html += f'''
                <article class="scroll-reveal service-card group rounded-xl border border-neutral-800 bg-neutral-900/20 p-7 transition-all duration-300">
                    <div class="service-icon-wrap rounded-xl border border-neutral-700 bg-neutral-800/80 mb-5 transition-all duration-300">{_icon(icon, 26, ACC2, cls="transition-colors duration-300")}</div>
                    <h3 class="text-lg font-semibold tracking-tight mb-2 text-white">{s_name} in {city}</h3>
                    <p class="text-sm text-stone-400 leading-relaxed mb-5">{s_desc}</p>
                    <a href="#contact" class="accent-link inline-flex items-center gap-1.5 text-sm font-medium transition-colors" style="color:{ACC2}">{CTA} {_icon("lucide:arrow-right", 14, "currentColor")}</a>
                </article>'''

    # -------------------------------------------------------------- FAQ
    faq_html = ""
    for i, (q, a) in enumerate(content["faq"]):
        faq_html += f'''
                <div class="faq-item rounded-xl border border-neutral-800 bg-neutral-900/20 overflow-hidden{" open" if i == 0 else ""}" style="margin-bottom:1rem">
                    <button class="faq-toggle w-full flex items-center justify-between p-5 text-left"><h3 class="text-sm font-semibold pr-4 text-white">{q}</h3>{_icon("lucide:chevron-down", 18, ACC2, cls="faq-chevron shrink-0")}</button>
                    <div class="faq-answer px-5"><p class="text-sm text-stone-400 leading-relaxed pb-5">{a}</p></div>
                </div>'''

    # ----------------------------------------------------- HERO BADGES
    badge_icons = ["lucide:shield-check", "lucide:award", "lucide:badge-check", "lucide:star"]
    badges_html = "".join(
        f'<div class="glass-badge flex items-center gap-2 px-3.5 py-2 rounded-lg">'
        f'{_icon(badge_icons[i % 4], 14, ACC2)}'
        f'<span class="text-[11px] font-semibold text-stone-300">{b}</span></div>'
        for i, b in enumerate(content["badges"]))

    about_checks = "".join(
        f'<div class="flex items-start gap-3">{_icon("lucide:check-circle-2", 20, ACC2, cls="mt-0.5 shrink-0")}'
        f'<p class="font-semibold text-sm text-white">{b}</p></div>'
        for b in content["badges"])

    # ------------------------------------------------------------ STATS
    stats_lg, stats_sm = "", ""
    for num, suf, label in content["stats"]:
        digits = re.sub(r"\D", "", num)
        if digits and "/" not in num:   # numbers count up: "1600" -> 0..1,600+ ; "24hr" -> 0..24hr
            prefix = re.sub(r"[\d,]", "", num)
            attrs = f'data-target="{digits}" data-suffix="{prefix + suf}"'
            shown = "0"
        else:        # words ("Free", "Same", "24/7"-less text) are shown as-is, no counter
            attrs, shown = "", f"{num}{suf}"
        stats_lg += (f'<div class="glass-badge rounded-xl p-5 text-center">'
                     f'<p class="stat-counter text-3xl font-extrabold" style="color:{ACC2}" {attrs}>{shown}</p>'
                     f'<p class="text-[10px] text-stone-500 mt-1.5 font-medium tracking-wide uppercase">{label}</p></div>')
        stats_sm += (f'<div class="text-center">'
                     f'<p class="stat-counter text-2xl font-extrabold" style="color:{ACC2}" {attrs}>{shown}</p>'
                     f'<p class="text-[10px] text-stone-500 mt-1">{label}</p></div>')

    # ----------------------------------------------------- SERVICE AREAS
    areas_section = build_service_areas(name, city, state, region, kw, phone, tel, areas,
                                        P, ACC, ACC2, ACCD, _icon)

    # ---------------------------------------------------------- REVIEWS
    rcities = ([city] + [a["city"] for a in areas])[:3]
    stars = "".join(f'{_icon("lucide:star", 16, ACC2)}' for _ in range(5))
    reviews_html = ""
    for i, (text, initials, person) in enumerate(REVIEW_POOLS.get(content.get("profile", "home"), REVIEW_POOL)):
        reviews_html += f'''
                <div class="scroll-reveal review-card rounded-xl border border-neutral-800 bg-neutral-900/20 p-7 transition-all">
                    <div class="flex items-center gap-1 mb-4">{stars}</div>
                    <p class="text-sm text-stone-300 leading-relaxed mb-5">"{text}"</p>
                    <div class="flex items-center gap-3 pt-5 border-t border-neutral-800"><div class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0" style="background:linear-gradient(135deg,{ACC2},{ACCD})">{initials}</div><div><p class="text-sm font-semibold text-white">{person}</p><p class="text-xs text-stone-500">{rcities[i % len(rcities)]}, {state}</p></div></div>
                </div>'''

    # --------------------------------------------------------- PROJECTS
    projects_section, projects_nav, projects_nav_m = "", "", ""
    if gal:
        kinds = P["kinds"]
        svcs = content["services"]
        cards = ""
        for i, gi in enumerate(gal[:3]):
            place = rcities[i % len(rcities)]
            title = svcs[i % len(svcs)][1]
            cards += f'''
                <article class="scroll-reveal project-card group relative rounded-xl overflow-hidden border border-neutral-800 transition-all duration-500">
                    <div class="img-fixed h-64"><img src="{gi}" alt="{unescape(title)} project by {name} in {place}, {state}" class="group-hover:scale-105 transition-transform duration-700" loading="lazy"></div>
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none"></div>
                    <div class="absolute bottom-0 left-0 right-0 p-5"><span class="text-[10px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">{kinds[i]} — {place}</span><h3 class="text-lg font-semibold mt-1 text-white">{title}</h3><p class="text-sm text-stone-400 mt-1">{hook}</p></div>
                </article>'''
        projects_nav = '<a href="#projects" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">' + P["work"] + '</a>'
        projects_nav_m = '<a href="#projects" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">' + P["work"] + '</a>'
        projects_section = f'''
    <!-- ==================== PROJECTS ==================== -->
    <section id="projects" class="py-24 border-t border-neutral-800/50" aria-label="Recent projects">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="scroll-reveal text-center mb-16">
                <div class="eyebrow">{_icon("lucide:images", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">Recent {P["work"]}</span></div>
                <h2 class="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-white">{unescape(kw)} {P["work"]} in {city} &amp; {region}</h2>
                <p class="text-stone-400 max-w-2xl mx-auto">See the workmanship behind the reviews.</p>
            </div>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">{cards}
            </div>
        </div>
    </section>
'''

    hero_media = (f'<div class="hero-bg-wrapper"><img id="heroBgImg" src="{hero_img}" '
                  f'alt="{name} — {unescape(kw)} at work in {city}, {state}" loading="eager" '
                  f'onload="this.classList.add(\'loaded\')" onerror="this.style.display=\'none\'"></div>'
                  ) if hero_img else ""
    about_media = (f'<img src="{about_img}" alt="{name} {P["team_alt"]} in {city}, {state}" loading="lazy">'
                   if about_img else
                   f'<div class="w-full h-full flex items-center justify-center">'
                   f'{_icon(logo, 110, ACC2, style="opacity:.18")}</div>')

    footer_services = "".join(
        f'<li style="margin-bottom:.75rem"><a href="#services" class="footer-link text-sm text-stone-500 transition-colors">{s[1]}</a></li>'
        for s in content["services"][:6])
    footer_areas = "".join(
        f'<li style="margin-bottom:.75rem"><a href="#service-areas" class="footer-link text-sm text-stone-500 transition-colors">{c}</a></li>'
        for c in ([city] + [a["city"] for a in areas])[:6])
    service_opts = "".join(f"<option>{unescape(s[1])}</option>" for s in content["services"])

    # ================================================================
    #                          HTML TEMPLATE
    # ================================================================
    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{html_attr(meta_desc)}">
    <meta name="keywords" content="{unescape(kw).lower()} {city} {state}, {unescape(kw).lower()} near me, {unescape(content['services'][0][1]).lower()} {city}, {unescape(tagline).lower()}, {unescape(kw).lower()} {region}">
    <meta name="robots" content="index, follow">
    <meta name="geo.region" content="{country}-{state}">
    <meta name="geo.placename" content="{city}">{geo_meta}
    <title>{html_attr(name)} | {kw} in {city}, {state} | {P["title_tail"]}</title>

    <meta property="og:title" content="{html_attr(name)} — {kw} in {city}, {state}">
    <meta property="og:description" content="{html_attr(meta_desc)}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="en_{country}">
    <meta property="og:site_name" content="{html_attr(name)}">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">


    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "{json_escape(name)}",
        "telephone": "+{tel}",
        "email": "{email}",
        "address": {{
            "@type": "PostalAddress",
            "addressLocality": "{json_escape(city)}",
            "addressRegion": "{state}",
            "addressCountry": "{country}"
        }}{geo_ld},
        "areaServed": [{area_ld}],
        "priceRange": "$$",
        "aggregateRating": {{
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "127",
            "bestRating": "5"
        }},
        "hasOfferCatalog": {{
            "@type": "OfferCatalog",
            "name": "{json_escape(kw)} Services",
            "itemListElement": [{svc_ld}]
        }}
    }}
    </script>

    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{faq_ld}]
    }}
    </script>

    <style>
/* ===== HOST-THEME RESET =====================================
           When this page is embedded in WordPress,
        the active theme's
           stylesheet still applies to our markup — turning links blue and
           underlined,
        giving buttons a grey background,
        and numbering the
           breadcrumb lists. These rules take our styling back. Never use angle
           brackets or child combinators here: the WP editor escapes them
           and every rule after that point dies.            */
        #lp-engine-root.lp-engine-site,
        .lp-engine-site,
        #lp-engine-root.lp-engine-site {{ color: #fff !important; background: #0a0a0a !important;
            font-family: 'Inter', system-ui, sans-serif !important; line-height: 1.6 !important; }}.lp-engine-site,
        #lp-engine-root.lp-engine-site,
        .lp-engine-site *,
        #lp-engine-root.lp-engine-site *,
        .lp-engine-site *::before,
        #lp-engine-root.lp-engine-site *::before,
        .lp-engine-site *::after,
        #lp-engine-root.lp-engine-site *::after {{ box-sizing: border-box !important; }}.lp-engine-site *,
        #lp-engine-root.lp-engine-site * {{ font-family: inherit; }}.lp-engine-site a,
        #lp-engine-root.lp-engine-site a,
        .lp-engine-site a:link,
        #lp-engine-root.lp-engine-site a:link,
        .lp-engine-site a:visited,
        #lp-engine-root.lp-engine-site a:visited,
        .lp-engine-site a:hover,
        #lp-engine-root.lp-engine-site a:hover,
        .lp-engine-site a:active,
        #lp-engine-root.lp-engine-site a:active,
        .lp-engine-site a:focus,
        #lp-engine-root.lp-engine-site a:focus {{
            color: inherit !important; text-decoration: none !important; box-shadow: none !important;
            border-bottom: 0 !important; background-image: none !important; }}.lp-engine-site ol,
        #lp-engine-root.lp-engine-site ol,
        .lp-engine-site ul,
        #lp-engine-root.lp-engine-site ul {{ list-style: none !important; margin: 0 !important; padding: 0 !important; }}.lp-engine-site li,
        #lp-engine-root.lp-engine-site li {{ list-style: none !important; margin: 0 !important; padding: 0 !important; }}.lp-engine-site li::before,
        #lp-engine-root.lp-engine-site li::before,
        .lp-engine-site li::marker,
        #lp-engine-root.lp-engine-site li::marker {{ content: none !important; display: none !important; }}.lp-engine-site button,
        #lp-engine-root.lp-engine-site button {{ background: none !important; border: 0 !important; color: inherit !important; font: inherit !important; cursor: pointer; text-align: inherit; padding: 0; box-shadow: none !important; }}.lp-engine-site input,
        #lp-engine-root.lp-engine-site input,
        .lp-engine-site select,
        #lp-engine-root.lp-engine-site select,
        .lp-engine-site textarea,
        #lp-engine-root.lp-engine-site textarea {{ font: inherit !important; color: #fff !important; }}.lp-engine-site img,
        #lp-engine-root.lp-engine-site img,
        .lp-engine-site svg,
        #lp-engine-root.lp-engine-site svg {{ max-width: 100% !important; border: 0 !important; }}.lp-engine-site svg,
        #lp-engine-root.lp-engine-site svg {{ display: inline-block !important; height: auto; }}.lp-engine-site p,
        #lp-engine-root.lp-engine-site p,
        .lp-engine-site h1,
        #lp-engine-root.lp-engine-site h1,
        .lp-engine-site h2,
        #lp-engine-root.lp-engine-site h2,
        .lp-engine-site h3,
        #lp-engine-root.lp-engine-site h3,
        .lp-engine-site h4,
        #lp-engine-root.lp-engine-site h4,
        .lp-engine-site h5,
        #lp-engine-root.lp-engine-site h5,
        .lp-engine-site h6,
        #lp-engine-root.lp-engine-site h6 {{ margin: 0 !important; padding: 0 !important; }}.lp-engine-site section,
        #lp-engine-root.lp-engine-site section,
        .lp-engine-site header,
        #lp-engine-root.lp-engine-site header,
        .lp-engine-site footer,
        #lp-engine-root.lp-engine-site footer,
        .lp-engine-site nav,
        #lp-engine-root.lp-engine-site nav,
        .lp-engine-site article,
        #lp-engine-root.lp-engine-site article,
        .lp-engine-site aside,
        #lp-engine-root.lp-engine-site aside {{ margin: 0 !important; float: none !important; width: auto !important; max-width: none !important; }}.lp-engine-site::before,
        #lp-engine-root.lp-engine-site::before,
        .lp-engine-site::after,
        #lp-engine-root.lp-engine-site::after {{ content: none; }}

{BASE_CSS}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a0a; }}
        ::-webkit-scrollbar-thumb {{ background: #262626; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #404040; }}

        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes slideInRight {{ from {{ opacity: 0; transform: translateX(40px); }} to {{ opacity: 1; transform: translateX(0); }} }}
        @keyframes pulse-glow {{ 0%, 100% {{ box-shadow: 0 0 20px -3px rgba({RGB}, 0.35); }} 50% {{ box-shadow: 0 0 35px -3px rgba({RGB}, 0.65); }} }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px); }} }}
        @keyframes shimmer {{ 0% {{ background-position: -200% 0; }} 100% {{ background-position: 200% 0; }} }}

        .animate-fade-in-up {{ animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
        .animate-slide-right {{ animation: slideInRight 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
        .delay-100 {{ animation-delay: 0.1s; }} .delay-200 {{ animation-delay: 0.2s; }} .delay-300 {{ animation-delay: 0.3s; }}
        .delay-400 {{ animation-delay: 0.4s; }} .delay-500 {{ animation-delay: 0.5s; }} .delay-600 {{ animation-delay: 0.6s; }}
        .delay-700 {{ animation-delay: 0.7s; }} .delay-800 {{ animation-delay: 0.8s; }}

        .hero-section {{
            position: relative; min-height: 100vh; overflow: hidden;
            background: linear-gradient(170deg, {g[0]} 0%, {g[1]} 10%, {g[2]} 20%, {g[3]} 30%, {g[4]} 38%, {g[3]} 48%, {g[2]} 58%, {g[1]} 70%, {g[0]} 85%, {g[0]} 100%);
        }}
        .hero-bg-wrapper {{ position: absolute; inset: 0; z-index: 1; }}
        .hero-bg-wrapper img {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; object-position: center center; display: block; opacity: 0; transition: opacity 1.5s ease; }}
        .hero-bg-wrapper img.loaded {{ opacity: 1; }}
        .hero-image-overlay {{ position: absolute; inset: 0; z-index: 2; background: linear-gradient(160deg, rgba(10,10,10,0.78) 0%, rgba(10,10,10,0.62) 35%, rgba(10,10,10,0.45) 60%, rgba(10,10,10,0.35) 80%, rgba(10,10,10,0.50) 100%); }}

        .stat-counter {{ font-variant-numeric: tabular-nums; }}
        .glass-badge {{ backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); background: rgba(23, 23, 23, 0.55); border: 1px solid rgba(255,255,255,0.07); }}
        .cta-glow {{ animation: pulse-glow 2.5s ease-in-out infinite; }}
        .float-anim {{ animation: float 4s ease-in-out infinite; }}
        /* This card needs BOTH the entrance fade and the idle float.
           Declaring them separately makes the second win, leaving the
           card invisible, so list them together in one shorthand. */
        .animate-slide-right.float-anim {{
            animation: slideInRight 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards,
                       float 4s ease-in-out 1.4s infinite; }}

        .eyebrow {{ display: inline-flex; align-items: center; gap: 10px; padding: 8px 16px; border-radius: 9999px; border: 1px solid rgba({RGB},0.25); background: rgba({RGB},0.10); margin-bottom: 24px; }}

        .nav-link {{ position: relative; white-space: nowrap; }}
        .lp-engine-site .max-w-7xl {{ max-width: 80rem; }}
        nav .hidden.lg\\:flex {{ flex-wrap: nowrap; }}
        /* Long business names used to run into the menu on 1024-1400px screens. */
        @media (max-width: 1400px) {{ nav .hidden.lg\\:flex {{ gap: 1.25rem; }} }}
        .brand-name {{ display: block; max-width: 15rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
{SERVICE_AREA_CSS}
        .nav-link::after {{ content: ''; position: absolute; bottom: -2px; left: 0; width: 0; height: 2px; background: {ACC}; transition: width 0.3s ease; }}
        .nav-link:hover::after {{ width: 100%; }}

        .service-icon-wrap {{ display: flex; align-items: center; justify-content: center; width: 56px; height: 56px; min-width: 56px; min-height: 56px; }}
        .service-card:hover .service-icon-wrap {{ background: {ACC} !important; border-color: {ACC} !important; }}
        .service-card:hover .service-icon-wrap svg {{ stroke: #fff !important; }}
        .service-card:hover {{ border-color: rgba({RGB},0.30) !important; box-shadow: 0 0 30px -5px rgba({RGB},0.10); }}
        .area-card:hover {{ border-color: rgba({RGB},0.30) !important; }}
        .area-card:hover .area-name {{ color: {ACC2}; }}
        .project-card:hover {{ border-color: rgba({RGB},0.30) !important; }}
        .review-card:hover {{ border-color: rgba({RGB},0.20) !important; }}
        .footer-link:hover {{ color: {ACC2}; }}
        .accent-link:hover {{ opacity: .8; }}
        .top-link:hover {{ color: {ACC2}; }}
        .btn-accent {{ background: {ACC}; }}
        .btn-accent:hover {{ background: {ACCD}; }}
        .btn-ghost:hover {{ border-color: {ACC} !important; background: rgba({RGB},0.10) !important; }}

        .mobile-menu {{ transform: translateX(100%); transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1); }}
        .mobile-menu.open {{ transform: translateX(0); }}

        .divider-shimmer {{ background: linear-gradient(90deg, transparent, rgba({RGB},0.4), transparent); background-size: 200% 100%; animation: shimmer 3s ease-in-out infinite; }}

        .scroll-reveal {{ opacity: 0; transform: translateY(30px); transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1); }}
        .scroll-reveal.visible {{ opacity: 1; transform: translateY(0); }}

        .img-fixed {{ overflow: hidden; position: relative; background: {T['img_tint']}; }}
        .img-fixed img {{ width: 100%; height: 100%; object-fit: cover; object-position: center; display: block; }}

        .faq-answer {{ max-height: 0; overflow: hidden; transition: max-height 0.4s ease; }}
        .faq-item.open .faq-answer {{ max-height: 320px; }}
        .faq-item.open .faq-chevron {{ transform: rotate(180deg); }}
        .faq-chevron {{ transition: transform 0.3s ease; }}

        .grid-pattern {{ background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 32px 32px; }}

        input:focus, select:focus, textarea:focus {{ outline: none; border-color: {ACC} !important; box-shadow: 0 0 0 1px {ACC}; }}
        h1, h2, h3, h4, h5, h6 {{ color: #ffffff; }}
        a, a:link, a:visited, a:hover {{ text-decoration: none; }}
        body {{ background: #0a0a0a; }}
    </style>
</head>
<body class="bg-[#0a0a0a] text-white font-sans antialiased overflow-x-hidden">

    <!-- ==================== TOP BAR ==================== -->
    <div class="bg-[#050505] border-b border-neutral-800/50 hidden md:block">
        <div class="max-w-7xl mx-auto px-6 lg:px-8 flex items-center justify-between h-10">
            <div class="flex items-center gap-6">
                <a href="tel:+{tel}" class="top-link flex items-center gap-1.5 text-xs text-stone-500 transition-colors">{_icon("lucide:phone", 11, ACC)}{phone}</a>
                <a href="mailto:{email}" class="top-link flex items-center gap-1.5 text-xs text-stone-500 transition-colors">{_icon("lucide:mail", 11, ACC)}{email}</a>
                <span class="flex items-center gap-1.5 text-xs text-stone-500">{_icon("lucide:map-pin", 11, ACC)}{city}, {state}</span>
            </div>
            <div class="flex items-center gap-4">
                <span class="flex items-center gap-1.5 text-xs font-medium" style="color:{ACC2}">{_icon("lucide:clock", 11, "currentColor")}{tagline}</span>
                <div class="flex items-center gap-2 ml-3">
                    <a href="#" class="text-stone-600 top-link transition-colors" aria-label="Facebook">{_icon("lucide:facebook", 14, "currentColor")}</a>
                    <a href="#" class="text-stone-600 top-link transition-colors" aria-label="Instagram">{_icon("lucide:instagram", 14, "currentColor")}</a>
                    <a href="#" class="text-stone-600 top-link transition-colors" aria-label="YouTube">{_icon("lucide:youtube", 14, "currentColor")}</a>
                </div>
            </div>
        </div>
    </div>

    <!-- ==================== NAVIGATION ==================== -->
    <nav id="navbar" class="fixed top-0 md:top-10 left-0 right-0 z-50 transition-all duration-300" style="background: rgba(10,10,10,0.88); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <a href="#hero" class="flex items-center gap-3 group shrink-0" aria-label="{html_attr(name)} home">
                    <div class="w-10 h-10 rounded-lg flex items-center justify-center transition-colors" style="background:{ACC}">{_icon(logo, 20, "currentColor")}</div>
                    <div class="min-w-0"><span class="brand-name text-lg font-bold tracking-tight text-white" title="{html_attr(name)}">{brand}</span><span class="text-[10px] block text-stone-500 tracking-[0.2em] uppercase -mt-0.5">{kw}</span></div>
                </a>
                <div class="hidden lg:flex items-center gap-8">
                    <a href="#services" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">Services</a>
                    <a href="#about" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">About</a>
                    <a href="#service-areas" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">Service Areas</a>
                    {projects_nav}
                    <a href="#reviews" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">Reviews</a>
                    <a href="#faq" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">FAQ</a>
                    <a href="#contact" class="nav-link text-sm text-stone-300 hover:text-white transition-colors">Contact</a>
                </div>
                <div class="flex items-center gap-4">
                    <a href="tel:+{tel}" class="btn-ghost hidden lg:flex items-center gap-2.5 px-4 py-2 rounded-lg transition-colors shrink-0" style="border:1px solid rgba({RGB},0.20);background:rgba({RGB},0.05)">
                        {_icon("lucide:phone-call", 16, ACC2)}
                        <div><p class="text-[9px] font-semibold tracking-widest uppercase leading-none" style="color:{ACC2}">{tagline}</p><p class="text-sm font-bold text-white leading-tight">{phone}</p></div>
                    </a>
                    <a href="#contact" class="btn-accent hidden sm:inline-flex items-center gap-2 text-white text-sm font-semibold px-6 py-2.5 rounded-lg transition-all duration-200 shrink-0">{CTA_SHORT}</a>
                    <button id="mobileMenuBtn" class="lg:hidden p-2 text-stone-400 hover:text-white transition-colors" aria-label="Open menu">{_icon("lucide:menu", 24, "currentColor")}</button>
                </div>
            </div>
        </div>
        <div class="absolute bottom-0 left-0 right-0 h-px divider-shimmer"></div>
    </nav>

    <!-- ==================== MOBILE MENU ==================== -->
    <div id="mobileMenu" class="mobile-menu fixed top-0 right-0 bottom-0 w-80 z-[60] bg-[#0a0a0a] border-l border-neutral-800 p-6 overflow-y-auto">
        <div class="flex justify-between items-center mb-8">
            <div class="flex items-center gap-2"><div class="w-8 h-8 rounded-md flex items-center justify-center" style="background:{ACC}">{_icon(logo, 16, "currentColor")}</div><span class="font-bold text-sm text-white">{brand}</span></div>
            <button id="mobileMenuClose" class="p-2 text-stone-400 hover:text-white transition-colors" aria-label="Close menu">{_icon("lucide:x", 24, "currentColor")}</button>
        </div>
        <div class="flex flex-col gap-1">
            <a href="#services" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">Services</a>
            <a href="#about" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">About</a>
            <a href="#service-areas" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">Service Areas</a>
            {projects_nav_m}
            <a href="#reviews" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">Reviews</a>
            <a href="#faq" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">FAQ</a>
            <a href="#contact" class="mobile-nav-link text-base text-stone-300 hover:text-white hover:bg-neutral-800 transition-all py-3 px-4 rounded-lg">Contact</a>
        </div>
        <div class="mt-8 pt-6 border-t border-neutral-800">
            <a href="tel:+{tel}" class="flex items-center gap-3 text-sm text-stone-400 mb-4 px-4">{_icon("lucide:phone-call", 16, ACC2)}{phone}</a>
            <a href="#contact" class="btn-accent mobile-nav-link flex items-center justify-center gap-2 text-white text-sm font-semibold px-6 py-3.5 rounded-lg transition-colors w-full">{CTA}</a>
        </div>
    </div>
    <div id="mobileOverlay" class="fixed inset-0 z-[55] bg-black/70 hidden"></div>

    <!-- ==================== HERO ==================== -->
    <header id="hero" class="hero-section flex items-center">
        {hero_media}
        <div class="hero-image-overlay"></div>
        <div class="absolute bottom-0 left-0 right-0 h-48 z-[3]" style="background: linear-gradient(to top, #0a0a0a, transparent);"></div>
        <div class="absolute top-0 left-0 right-0 h-1 z-[4]" style="background:linear-gradient(90deg,{ACC},{ACC2},{ACC});opacity:.6"></div>

        <div class="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 pt-32 pb-24 w-full">
            <div class="grid lg:grid-cols-12 gap-8 items-center">
                <div class="lg:col-span-7">
                    <div class="opacity-0 animate-fade-in-up mb-6">
                        <nav aria-label="Breadcrumb" class="text-xs text-stone-500">
                            <ol class="flex items-center gap-1.5" style="list-style:none;margin:0;padding:0"><li><a href="#hero" class="top-link transition-colors">Home</a></li><li><span class="text-stone-700">/</span></li><li class="text-stone-400">{city}, {state} {kw}</li></ol>
                        </nav>
                    </div>

                    <div class="opacity-0 animate-fade-in-up eyebrow"><span class="w-1.5 h-1.5 rounded-full inline-block" style="background:{ACC2}"></span><span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">{tagline}</span></div>

                    <h1 class="opacity-0 animate-fade-in-up delay-200">
                        <span class="block text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold leading-[1.05] tracking-tight text-white">{kw}</span>
                        <span class="block text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold leading-[1.05] tracking-tight mt-1 text-white">in <span style="color:{ACC2}">{city}, {state}</span></span>
                    </h1>

                    <p class="opacity-0 animate-fade-in-up delay-400 text-base sm:text-lg font-semibold mt-6" style="color:{ACC2}">{hook}</p>
                    <p class="opacity-0 animate-fade-in-up delay-400 text-base sm:text-lg text-stone-300 leading-relaxed mt-4 max-w-xl">{hero_sub}</p>

                    <div class="opacity-0 animate-fade-in-up delay-500 flex flex-wrap gap-4 mt-10">
                        <a href="#contact" class="btn-accent cta-glow inline-flex items-center gap-2.5 text-white font-semibold px-8 py-4 rounded-lg transition-all duration-200 text-sm tracking-wide">{CTA.upper()} {_icon("lucide:arrow-right", 18, "currentColor")}</a>
                        <a href="tel:+{tel}" class="btn-ghost inline-flex items-center gap-2.5 border border-neutral-600 text-white font-semibold px-8 py-4 rounded-lg transition-all duration-200 text-sm tracking-wide bg-white/5">{_icon("lucide:phone", 16, ACC2)}{phone}</a>
                    </div>

                    <div class="opacity-0 animate-fade-in-up delay-700 flex flex-wrap items-center gap-3 mt-10">{badges_html}</div>
                </div>

                <aside class="lg:col-span-5 hidden lg:flex flex-col items-end gap-5">
                    <div class="opacity-0 animate-slide-right delay-600 glass-badge rounded-2xl p-6 max-w-xs w-full float-anim">
                        <div class="flex items-center gap-4 mb-4"><div class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0" style="background:{ACC}">{_icon("lucide:phone-call", 22, "currentColor")}</div><div><p class="text-[10px] font-bold tracking-[0.15em] uppercase" style="color:{ACC2}">{tagline}</p><p class="text-xl font-bold text-white mt-0.5"><a href="tel:+{tel}">{phone}</a></p></div></div>
                        <p class="text-xs text-stone-500 leading-relaxed">Serving {city} and all of {region}. Call or text — we answer, and we show up when we say we will.</p>
                    </div>
                    <div class="opacity-0 animate-slide-right delay-800 grid grid-cols-2 gap-4 w-full max-w-xs">{stats_lg}</div>
                </aside>
            </div>
        </div>
    </header>

    <!-- Mobile Stats -->
    <section class="lg:hidden bg-[#0a0a0a] py-8 border-y border-neutral-800/50" aria-label="Statistics">
        <div class="max-w-7xl mx-auto px-6">
            <div class="glass-badge rounded-xl p-4 mb-5 flex items-center gap-4">
                <div class="w-10 h-10 shrink-0 rounded-xl flex items-center justify-center" style="background:{ACC}">{_icon("lucide:phone-call", 18, "currentColor")}</div>
                <div><p class="text-[9px] font-bold tracking-[0.15em] uppercase" style="color:{ACC2}">{tagline}</p><p class="text-lg font-bold text-white"><a href="tel:+{tel}">{phone}</a></p></div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">{stats_sm}</div>
        </div>
    </section>

    <!-- ==================== SERVICES ==================== -->
    <section id="services" class="py-24 bg-[#0a0a0a] grid-pattern" aria-label="Services">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="scroll-reveal text-center mb-16">
                <div class="eyebrow">{_icon("lucide:wrench", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">Our Services Near {city}, {state}</span></div>
                <h2 class="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-white">{content['services'][0][1]} &amp; More in {region}</h2>
                <p class="text-stone-400 max-w-3xl mx-auto leading-relaxed">Everything we do, explained plainly — for homes and businesses across <strong>{city}</strong> and {region}.</p>
            </div>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">{services_html}
            </div>
        </div>
    </section>

    <!-- ==================== ABOUT ==================== -->
    <section id="about" class="py-24 border-t border-neutral-800/50" aria-label="About {html_attr(name)}">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="grid lg:grid-cols-2 gap-16 items-center">
                <div class="scroll-reveal relative">
                    <div class="img-fixed rounded-2xl border border-neutral-800 h-[420px]">{about_media}</div>
                    <div class="absolute -bottom-5 right-6 sm:right-10 glass-badge rounded-xl p-4 shadow-2xl">
                        <div class="flex items-center gap-3"><div class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0" style="background:{ACC}">{_icon("lucide:award", 24, "currentColor")}</div><div><p class="text-2xl font-extrabold text-white leading-none">4.9★</p><p class="text-[10px] text-stone-400 font-medium tracking-wide">Customer Rated</p></div></div>
                    </div>
                    <div class="absolute -top-3 -left-3 w-16 h-16 rounded-tl-xl" style="border-left:2px solid rgba({RGB},0.30);border-top:2px solid rgba({RGB},0.30)"></div>
                </div>
                <div class="scroll-reveal">
                    <div class="eyebrow">{_icon("lucide:users", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">About Us</span></div>
                    <h2 class="text-3xl sm:text-4xl font-bold tracking-tight mb-6 text-white">{content['about_h2']}</h2>
                    <p class="text-stone-400 leading-relaxed mb-5">{about_b[0]}</p>
                    <p class="text-stone-400 leading-relaxed mb-8">{about_b[1] if len(about_b) > 1 else ''}</p>
                    <div class="space-y-4 mb-8">{about_checks}</div>
                    <a href="#contact" class="btn-accent inline-flex items-center gap-2.5 text-white font-semibold px-8 py-3.5 rounded-lg transition-colors text-sm">{CTA} {_icon("lucide:arrow-right", 16, "currentColor")}</a>
                </div>
            </div>
        </div>
    </section>

{areas_section}
{projects_section}
    <!-- ==================== REVIEWS ==================== -->
    <section id="reviews" class="py-24 border-t border-neutral-800/50 grid-pattern" aria-label="Reviews">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="scroll-reveal text-center mb-16">
                <div class="eyebrow">{_icon("lucide:message-square-quote", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">Customer Reviews</span></div>
                <h2 class="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-white">Why {city} {audience} Call Us Back</h2>
                <p class="text-stone-400 max-w-2xl mx-auto">4.9★ from verified customers across {region}.</p>
            </div>
            <div class="grid md:grid-cols-3 gap-6">{reviews_html}
            </div>
        </div>
    </section>

    <!-- ==================== FAQ ==================== -->
    <section id="faq" class="py-24 border-t border-neutral-800/50" aria-label="FAQ">
        <div class="max-w-3xl mx-auto px-6 lg:px-8">
            <div class="scroll-reveal text-center mb-16">
                <div class="eyebrow">{_icon("lucide:help-circle", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">FAQ</span></div>
                <h2 class="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-white">{unescape(kw)} Questions — {city}, {state}</h2>
            </div>
            <div class="scroll-reveal space-y-4">{faq_html}
            </div>
        </div>
    </section>

    <!-- ==================== CTA ==================== -->
    <section class="py-20 border-t border-neutral-800/50 relative overflow-hidden">
        <div class="absolute inset-0" style="background:linear-gradient(135deg,{ACCD} 0%,#0a0a0a 70%)"></div>
        <div class="relative max-w-4xl mx-auto px-6 lg:px-8 text-center">
            <div class="scroll-reveal">
                <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight mb-5 text-white">{content['cta_h2']}</h2>
                <p class="text-stone-300 text-lg max-w-2xl mx-auto mb-10 leading-relaxed">{hook} — serving {city} and all of {region}.</p>
                <div class="flex flex-wrap justify-center gap-4">
                    <a href="#contact" class="btn-accent cta-glow inline-flex items-center gap-2.5 text-white font-semibold px-10 py-4 rounded-lg transition-all text-sm tracking-wide">{CTA.upper()} {_icon("lucide:arrow-right", 18, "currentColor")}</a>
                    <a href="tel:+{tel}" class="btn-ghost inline-flex items-center gap-2.5 border border-neutral-500 text-white font-semibold px-10 py-4 rounded-lg transition-all text-sm tracking-wide bg-white/5">{_icon("lucide:phone", 16, "currentColor")}{phone}</a>
                </div>
            </div>
        </div>
    </section>

    <!-- ==================== CONTACT ==================== -->
    <section id="contact" class="py-24 border-t border-neutral-800/50 relative overflow-hidden">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full opacity-[0.04]" style="background: radial-gradient(circle, {ACC}, transparent 70%);"></div>
        <div class="relative max-w-7xl mx-auto px-6 lg:px-8">
            <div class="grid lg:grid-cols-2 gap-16">
                <div class="scroll-reveal">
                    <div class="eyebrow">{_icon("lucide:phone", 14, ACC2)}<span class="text-[11px] font-semibold tracking-[0.15em] uppercase" style="color:{ACC2}">Contact Us</span></div>
                    <h2 class="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-white">{CTA} in <span style="color:{ACC2}">{city}, {state}</span></h2>
                    <p class="text-stone-400 leading-relaxed mb-10">{P["form_note"]}</p>
                    <div class="space-y-6">
                        <div class="flex items-start gap-4" style="margin-bottom:1.5rem"><div class="w-11 h-11 shrink-0 rounded-lg flex items-center justify-center" style="background:rgba({RGB},0.10);border:1px solid rgba({RGB},0.15)">{_icon("lucide:phone", 18, ACC2)}</div><div><p class="font-semibold text-sm text-white">Call or Text</p><p class="text-stone-400 text-sm"><a href="tel:+{tel}">{phone}</a></p></div></div>
                        <div class="flex items-start gap-4" style="margin-bottom:1.5rem"><div class="w-11 h-11 shrink-0 rounded-lg flex items-center justify-center" style="background:rgba({RGB},0.10);border:1px solid rgba({RGB},0.15)">{_icon("lucide:mail", 18, ACC2)}</div><div><p class="font-semibold text-sm text-white">Email Us</p><p class="text-stone-400 text-sm"><a href="mailto:{email}">{email}</a></p></div></div>
                        <div class="flex items-start gap-4" style="margin-bottom:1.5rem"><div class="w-11 h-11 shrink-0 rounded-lg flex items-center justify-center" style="background:rgba({RGB},0.10);border:1px solid rgba({RGB},0.15)">{_icon("lucide:map-pin", 18, ACC2)}</div><div><p class="font-semibold text-sm text-white">Service Area</p><p class="text-stone-400 text-sm">{city}, {state} &amp; {region}</p></div></div>
                        <div class="flex items-start gap-4" style="margin-bottom:1.5rem"><div class="w-11 h-11 shrink-0 rounded-lg flex items-center justify-center" style="background:rgba({RGB},0.10);border:1px solid rgba({RGB},0.15)">{_icon("lucide:clock", 18, ACC2)}</div><div><p class="font-semibold text-sm text-white">Business Hours</p><p class="text-stone-400 text-sm">{hours}</p></div></div>
                    </div>
                </div>
                <div class="scroll-reveal rounded-2xl border border-neutral-800 bg-neutral-900/20 p-8">
                    <form id="contactForm" class="space-y-5">
                        <div style="margin-bottom:1.25rem" class="grid sm:grid-cols-2 gap-5">
                            <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">First Name *</label><input type="text" name="firstName" required class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors placeholder:text-stone-600" placeholder="John"></div>
                            <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">Last Name *</label><input type="text" name="lastName" required class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors placeholder:text-stone-600" placeholder="Doe"></div>
                        </div>
                        <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">Email *</label><input type="email" name="email" required class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors placeholder:text-stone-600" placeholder="john@example.com"></div>
                        <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">Phone *</label><input type="tel" name="phone" required class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors placeholder:text-stone-600" placeholder="{phone}"></div>
                        <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">City / Town</label><input type="text" name="city" class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors placeholder:text-stone-600" placeholder="{city}"></div>
                        <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">Service Needed</label><select name="service" class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors"><option value="">Select...</option>{service_opts}</select></div>
                        <div style="margin-bottom:1.25rem"><label class="block text-sm font-semibold text-stone-300 mb-2">Tell Us About Your Project</label><textarea name="message" rows="4" class="w-full px-4 py-3 rounded-lg bg-neutral-800/80 border border-neutral-700 text-white text-sm transition-colors placeholder:text-stone-600 resize-none" placeholder="Describe what you need..."></textarea></div>
                        <button type="submit" class="btn-accent w-full inline-flex items-center justify-center gap-2.5 text-white font-semibold px-8 py-4 rounded-lg transition-colors text-sm tracking-wide">GET MY FREE QUOTE {_icon("lucide:arrow-right", 16, "currentColor")}</button>
                        <p class="text-[11px] text-stone-600 text-center">100% free. No spam. No obligation.</p>
                    </form>
                    <div id="formSuccess" class="hidden mt-4 p-4 rounded-lg bg-green-900/30 border border-green-700/30"><div class="flex items-center gap-2">{_icon("lucide:check-circle-2", 20, "currentColor")}<p class="text-sm text-green-400 font-semibold">Thank you! We'll contact you within 24 hours.</p></div></div>
                </div>
            </div>
        </div>
    </section>

    <!-- ==================== FOOTER ==================== -->
    <footer class="border-t border-neutral-800/50 bg-[#050505]">
        <div class="max-w-7xl mx-auto px-6 lg:px-8 py-16">
            <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-12">
                <div class="sm:col-span-2 lg:col-span-1">
                    <div class="flex items-center gap-3 mb-5"><div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" style="background:{ACC}">{_icon(logo, 20, "currentColor")}</div><div><span class="text-lg font-bold tracking-tight text-white">{brand}</span><span class="text-[10px] block text-stone-500 tracking-[0.2em] uppercase -mt-0.5">{kw}</span></div></div>
                    <p class="text-sm text-stone-500 leading-relaxed mb-5">{tagline} in {city}, {state}. Locally owned. {P["trust"]}.</p>
                    <div class="flex items-center gap-2.5">
                        <a href="#" class="footer-link w-9 h-9 rounded-lg border border-neutral-800 flex items-center justify-center text-stone-500 transition-all" aria-label="Facebook">{_icon("lucide:facebook", 16, "currentColor")}</a>
                        <a href="#" class="footer-link w-9 h-9 rounded-lg border border-neutral-800 flex items-center justify-center text-stone-500 transition-all" aria-label="Instagram">{_icon("lucide:instagram", 16, "currentColor")}</a>
                        <a href="#" class="footer-link w-9 h-9 rounded-lg border border-neutral-800 flex items-center justify-center text-stone-500 transition-all" aria-label="YouTube">{_icon("lucide:youtube", 16, "currentColor")}</a>
                    </div>
                </div>
                <div><h4 class="text-sm font-bold tracking-tight mb-5 text-white">Services</h4><ul class="space-y-3">{footer_services}</ul></div>
                <div><h4 class="text-sm font-bold tracking-tight mb-5 text-white">Service Areas</h4><ul class="space-y-3">{footer_areas}</ul></div>
                <div><h4 class="text-sm font-bold tracking-tight mb-5 text-white">Contact</h4><ul class="space-y-3">
                    <li class="flex items-center gap-2 text-sm text-stone-500" style="margin-bottom:.75rem">{_icon("lucide:phone", 12, ACC, cls="shrink-0")}<a href="tel:+{tel}">{phone}</a></li>
                    <li class="flex items-center gap-2 text-sm text-stone-500" style="margin-bottom:.75rem">{_icon("lucide:mail", 12, ACC, cls="shrink-0")}<a href="mailto:{email}">{email}</a></li>
                    <li class="flex items-start gap-2 text-sm text-stone-500" style="margin-bottom:.75rem">{_icon("lucide:map-pin", 12, ACC, cls="mt-1 shrink-0")}<span>{city}, {state}<br>{region}</span></li>
                    <li class="flex items-center gap-2 text-sm text-stone-500" style="margin-bottom:.75rem">{_icon("lucide:clock", 12, ACC, cls="shrink-0")}{hours}</li>
                    <li class="flex items-center gap-2 text-sm text-stone-500" style="margin-bottom:.75rem">{_icon("lucide:badge-check", 12, ACC, cls="shrink-0")}{P["trust"]}</li>
                </ul></div>
            </div>
            <div class="mt-14 pt-8 border-t border-neutral-800/50 flex flex-col sm:flex-row justify-between items-center gap-4">
                <p class="text-[11px] text-stone-600">© 2026 {name}. All rights reserved. {P["trust"]}.</p>
                <div class="flex items-center gap-6"><a href="#" class="text-[11px] text-stone-600 hover:text-stone-400 transition-colors">Privacy Policy</a><a href="#" class="text-[11px] text-stone-600 hover:text-stone-400 transition-colors">Terms of Service</a></div>
            </div>
        </div>
    </footer>

    <!-- Floating Call -->
    <div class="lg:hidden fixed bottom-6 right-6 z-50"><a href="tel:+{tel}" class="w-14 h-14 rounded-full flex items-center justify-center transition-colors" style="background:{ACC};box-shadow: 0 0 25px -3px rgba({RGB},0.5);" aria-label="Call {html_attr(name)}">{_icon("lucide:phone", 22, "currentColor")}</a></div>

    <script>
        const mobileMenuBtn=document.getElementById('mobileMenuBtn'),mobileMenu=document.getElementById('mobileMenu'),mobileMenuClose=document.getElementById('mobileMenuClose'),mobileOverlay=document.getElementById('mobileOverlay'),mobileNavLinks=document.querySelectorAll('.mobile-nav-link');
        function openMobileMenu(){{mobileMenu.classList.add('open');mobileOverlay.classList.remove('hidden');document.body.style.overflow='hidden'}}
        function closeMobileMenu(){{mobileMenu.classList.remove('open');mobileOverlay.classList.add('hidden');document.body.style.overflow=''}}
        mobileMenuBtn.addEventListener('click',openMobileMenu);mobileMenuClose.addEventListener('click',closeMobileMenu);mobileOverlay.addEventListener('click',closeMobileMenu);mobileNavLinks.forEach(l=>l.addEventListener('click',closeMobileMenu));

        const navbar=document.getElementById('navbar');
        function handleNavPosition(){{navbar.style.top=(window.scrollY>40)?'0':(window.innerWidth>=768?'40px':'0')}}
        window.addEventListener('scroll',handleNavPosition);window.addEventListener('resize',handleNavPosition);handleNavPosition();

        let countersAnimated=false;
        function animateCounters(){{if(countersAnimated)return;countersAnimated=true;document.querySelectorAll('[data-target]').forEach(c=>{{const t=parseInt(c.getAttribute('data-target')),s=c.getAttribute('data-suffix')||'',d=2000,st=performance.now();function u(n){{const p=Math.min((n-st)/d,1),e=1-Math.pow(1-p,3);c.textContent=Math.floor(e*t).toLocaleString()+s;if(p<1)requestAnimationFrame(u);else c.textContent=t.toLocaleString()+s}}requestAnimationFrame(u)}})}}
        const statsObserver=new IntersectionObserver(e=>{{e.forEach(en=>{{if(en.isIntersecting){{animateCounters();statsObserver.disconnect()}}}})}},{{threshold:0.2}});
        document.querySelectorAll('[data-target]').forEach(el=>statsObserver.observe(el.closest('div')));

        const revealObserver=new IntersectionObserver(e=>{{e.forEach(en=>{{if(en.isIntersecting){{en.target.classList.add('visible');revealObserver.unobserve(en.target)}}}})}},{{threshold:0.1,rootMargin:'0px 0px -40px 0px'}});
        document.querySelectorAll('.scroll-reveal').forEach(el=>revealObserver.observe(el));

        document.querySelectorAll('.faq-toggle').forEach(btn=>{{btn.addEventListener('click',()=>{{const item=btn.closest('.faq-item'),isOpen=item.classList.contains('open');document.querySelectorAll('.faq-item').forEach(i=>i.classList.remove('open'));if(!isOpen)item.classList.add('open')}})}});

        const contactForm=document.getElementById('contactForm'),formSuccess=document.getElementById('formSuccess');
        contactForm.addEventListener('submit',e=>{{e.preventDefault();const btn=contactForm.querySelector('button[type="submit"]'),orig=btn.innerHTML;btn.innerHTML='Sending...';btn.disabled=true;btn.classList.add('opacity-70');setTimeout(()=>{{btn.innerHTML=orig;btn.disabled=false;btn.classList.remove('opacity-70');formSuccess.classList.remove('hidden');contactForm.reset();setTimeout(()=>formSuccess.classList.add('hidden'),6000)}},1200)}});

        document.querySelectorAll('a[href^="#"]').forEach(a=>{{a.addEventListener('click',function(e){{const id=this.getAttribute('href');if(id==='#')return;const t=document.querySelector(id);if(t){{e.preventDefault();window.scrollTo({{top:t.getBoundingClientRect().top+window.pageYOffset-80,behavior:'smooth'}})}}}})}});
    </script>
</body>
</html>"""

    # Swap the template's fixed near-black canvas for this niche's tinted one.
    html = apply_theme_canvas(html, T)
    html = harden_for_wordpress(html)

    out_root = Path(out_dir) if out_dir else OUT_DEFAULT
    # Two businesses in a bulk run can share a name ("Brother's Roofing" x8 in
    # a scraped list). Without a unique folder the second overwrites the first,
    # so disambiguate with a numeric suffix while keeping the first one clean.
    site_dir = out_root / slug
    if site_dir.exists():
        i = 2
        while (out_root / f"{slug}-{i}").exists():
            i += 1
        site_dir = out_root / f"{slug}-{i}"
    site_dir.mkdir(parents=True, exist_ok=True)
    out_path = site_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    for biz, addr, ph, nk in [
        ("Summit Roofing", "Kitchener, ON", "(519) 555-0123", "roofing"),
        ("Evergreen Tree Service", "Kitchener, ON", "(519) 555-0188", "tree_service"),
        ("Crystal Clean Co", "Fresno, CA", "(559) 555-0177", "cleaning"),
    ]:
        p = build_site(biz, addr, ph, nk)
        print(f"Built: {p}  ({round(p.stat().st_size/1024,1)} KB)")
