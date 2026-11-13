# -*- coding: utf-8 -*-
"""
images.py
---------
Picks images for a business from the shared /photo_library/{niche}/ folder.

ROLE-AWARE: filenames carry meaning, and we respect it.
    hero.jpg / *hero*        -> the wide banner shot (buildings, exteriors)
    about.jpg / ab-*         -> team / on-the-job shot for the About block
    gal-* / proj-* / ba*     -> finished-work photos for the Projects grid
    svc-*                    -> tight service close-ups; NEVER used as hero,
                                because a cropped close-up looks wrong behind
                                the H1 (this was the "random worker face"
                                bug — svc-repair.jpg was landing in the hero).

Where a niche's files have no role prefix (plumbing, tree_service, ...),
we fall back to deterministic hashing over the whole pool.

Same business name always gets the same images (deterministic hash), so
re-running never reshuffles a site — but two businesses in the same niche
get different photos, avoiding the "identical site" problem.
"""
import hashlib
from pathlib import Path

LIBRARY = Path(__file__).parent.parent / "photo_library"

# Filenames were being filtered on these markers, which left pest_control
# with 1 usable photo and gutter_cleaning with none - so the same image
# repeated in every section, or no image loaded at all. Every photo in the
# library is now used.
BAD_MARKERS = ()
EXTS = (".jpg", ".jpeg", ".png", ".webp")


def _photo_folder(niche: str) -> Path:
    """A niche's own folder if it has photos, otherwise the folder named by
    its `photos` key in niche_content (e.g. drain_cleaning -> plumbing).
    Drop real photos into photo_library/<niche>/original/ to override."""
    own = LIBRARY / niche / "original"
    if own.exists() and any(f.suffix.lower() in EXTS for f in own.iterdir()):
        return own
    try:
        from niche_content import get_niche
        alias = (get_niche(niche) or {}).get("photos")
    except Exception:
        alias = None
    return LIBRARY / alias / "original" if alias else own


def _usable_files(niche: str):
    folder = _photo_folder(niche)
    if not folder.exists():
        return []
    files = [f for f in sorted(folder.glob("*")) if f.suffix.lower() in EXTS]
    if BAD_MARKERS:
        files = [f for f in files
                 if not any(m in f.name.lower() for m in BAD_MARKERS)]
    return files


def _hash_pick(business_name: str, salt: str, pool: list):
    if not pool:
        return None
    h = int(hashlib.md5(f"{business_name}|{salt}".encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def _role(path: Path) -> str:
    """Classify a file by its filename convention."""
    n = path.stem.lower()
    if n.startswith("svc-") or n.startswith("svc_"):
        return "service"
    if "hero" in n:
        return "hero"
    if n.startswith("ab-") or n.startswith("ab_") or "about" in n:
        return "about"
    if (n.startswith(("gal-", "gal_", "proj-", "proj_", "ba", "before", "after"))
            or "gallery" in n or "project" in n):
        return "gallery"
    return "generic"


def pick_images(business_name: str, niche: str) -> dict:
    """
    Returns {"hero": Path|None, "about": Path|None, "gallery": [Path x3]}

    Hero prefers a real hero/wide shot and never uses an svc-* close-up
    unless there is genuinely nothing else in the folder.
    """
    pool = _usable_files(niche)
    result = {"hero": None, "about": None, "gallery": []}
    if not pool:
        return result

    buckets = {"hero": [], "about": [], "gallery": [], "service": [], "generic": []}
    for f in pool:
        buckets[_role(f)].append(f)

    used = set()

    def take(salt, *preferred):
        """Pick from the first non-empty preference tier, skipping used files."""
        for tier in preferred:
            avail = [f for f in tier if f not in used]
            if avail:
                pick = _hash_pick(business_name, salt, avail)
                used.add(pick)
                return pick
        return None

    # Hero: a dedicated hero shot, else a wide finished-work/generic photo.
    # svc-* is the last resort only (tight crops read badly behind the H1).
    result["hero"] = take("hero",
                          buckets["hero"], buckets["gallery"],
                          buckets["generic"], buckets["about"], buckets["service"])

    # About: team/on-the-job shot.
    result["about"] = take("about",
                           buckets["about"], buckets["generic"],
                           buckets["gallery"], buckets["service"], pool)

    # Gallery: three finished-work photos, rotated so businesses differ.
    gal_pool = ([f for f in buckets["gallery"] if f not in used]
                + [f for f in buckets["generic"] if f not in used]
                + [f for f in buckets["service"] if f not in used])
    if not gal_pool:
        gal_pool = [f for f in pool if f not in used] or pool
    h = int(hashlib.md5(f"{business_name}|gallery".encode()).hexdigest(), 16)
    start = h % len(gal_pool)
    rotated = gal_pool[start:] + gal_pool[:start]

    # Fill the three project slots with DISTINCT photos. Repeating one image
    # three times is what made the tree_service and pest_control pages look
    # like the same picture over and over. Widen to the rest of the library
    # before we ever consider repeating.
    gallery = rotated[:3]
    if len(gallery) < 3:
        spare = [f for f in pool if f not in gallery]
        s_start = h % len(spare) if spare else 0
        spare = spare[s_start:] + spare[:s_start]
        for f in spare:
            if len(gallery) >= 3:
                break
            gallery.append(f)
    # Only as a last resort (a folder with fewer than 3 photos in total) do
    # we cycle, so the section still renders rather than breaking.
    if gallery and len(gallery) < 3:
        gallery = (gallery * 3)[:3]
    result["gallery"] = gallery

    return result


def has_photos(niche: str) -> bool:
    return len(_usable_files(niche)) > 0


if __name__ == "__main__":
    for niche in ["roofing", "cleaning", "plumbing", "tree_service", "landscaping"]:
        print(f"--- {niche} ---")
        for biz in ["Brother's Roofing", "Summit Roofing", "R&R Co"]:
            i = pick_images(biz, niche)
            if not i["hero"]:
                print(f"  {biz:<20} (no photos)"); continue
            print(f"  {biz:<20} hero={i['hero'].name:<28} "
                  f"about={i['about'].name if i['about'] else '-':<28} "
                  f"gal={[g.name for g in i['gallery']]}")
