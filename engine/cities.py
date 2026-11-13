# -*- coding: utf-8 -*-
"""
cities.py
---------
Loads the 27,619-city US database (with lat/lon/population/county)
and finds real nearby service areas for a given business address.

Tested logic (haversine + population-sort) — same as validated
earlier in the roofing/dumpster examples.
"""
import csv
import math
from pathlib import Path
from functools import lru_cache

CITIES_CSV = Path(__file__).parent / "cities.csv"

# Default search radius (miles) and min population, per niche family.
# Falls back to GENERIC if the niche isn't listed.
NICHE_RADIUS = {
    # dark / trades — people drive further for these
    "roofing": (35, 3000), "junk_removal": (30, 3000), "dumpster_rental": (30, 3000),
    "plumbing": (25, 3000), "hvac": (25, 3000), "electrician": (25, 3000),
    "water_heater": (25, 3000), "garage_door": (25, 3000), "storm_damage": (35, 3000),
    # green / outdoor — usually more local
    "landscaping": (20, 3000), "lawn_care": (12, 3000), "tree_service": (25, 3000),
    "fencing": (20, 3000), "pest_control": (20, 3000),
    # blue / recurring services — tightest radius
    "cleaning": (15, 5000), "gutter_cleaning": (18, 3000),
    "GENERIC": (25, 3000),
}


def _content_radius(niche: str):
    """Newer niches declare their own (miles, min_pop) as `radius` in
    niche_content_extra.py instead of being listed above."""
    try:
        from niche_content import get_niche
        return (get_niche(niche) or {}).get("radius")
    except Exception:
        return None


@lru_cache(maxsize=1)
def _load_cities():
    """Load once, cache in memory for the whole batch run."""
    rows = []
    with open(CITIES_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({
                    "city": r["city"], "state": r["state"], "county": r["county"],
                    "pop": int(r["population"] or 0),
                    "lat": float(r["lat"]), "lon": float(r["lon"]),
                })
            except (ValueError, KeyError):
                continue
    return rows


def _haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_city(name: str, state: str):
    """Look up a city's lat/lon/pop by name + 2-letter state code."""
    name = name.strip().lower()
    state = state.strip().upper()
    for c in _load_cities():
        if c["city"].lower() == name and c["state"] == state:
            return c
    return None


def nearby_areas(city_name: str, state: str, niche: str, n: int = 5,
                  fallback_latlon: tuple = None):
    """
    Returns up to n nearby cities, sorted by population (largest first),
    within the niche's typical service radius.

    fallback_latlon: (lat, lon) to use if city_name isn't in our database
                      (small towns sometimes aren't listed).
    """
    radius, min_pop = NICHE_RADIUS.get(niche) or _content_radius(niche) or NICHE_RADIUS["GENERIC"]
    src = find_city(city_name, state)

    if src:
        src_lat, src_lon = src["lat"], src["lon"]
    elif fallback_latlon:
        src_lat, src_lon = fallback_latlon
    else:
        return []  # can't compute without a starting point

    out = []
    for c in _load_cities():
        if c["city"].lower() == city_name.strip().lower() and c["state"] == state.strip().upper():
            continue  # skip itself
        if c["pop"] < min_pop:
            continue
        # quick bounding-box filter before the expensive haversine call
        if abs(c["lat"] - src_lat) > 0.9 or abs(c["lon"] - src_lon) > 1.0:
            continue
        d = _haversine(src_lat, src_lon, c["lat"], c["lon"])
        if d <= radius:
            out.append({"city": c["city"], "state": c["state"], "county": c["county"],
                        "pop": c["pop"], "miles": round(d)})

    out.sort(key=lambda x: -x["pop"])
    return out[:n]


if __name__ == "__main__":
    # quick self-test
    for name, st, niche in [("Fresno", "CA", "roofing"), ("Round Rock", "TX", "lawn_care"),
                             ("Highland Park", "IL", "cleaning")]:
        areas = nearby_areas(name, st, niche)
        print(f"{name}, {st} ({niche}) ->")
        for a in areas:
            print(f"   {a['city']}, {a['state']}  {a['miles']} mi  pop {a['pop']:,}  {a['county']}")
