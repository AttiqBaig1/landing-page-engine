# -*- coding: utf-8 -*-
"""
niche_content_more.py
---------------------
200 more niches, written compactly with M(...). Each niche supplies what is
genuinely niche-specific (keyword, tagline, hook, palette, logo and six
services with their own copy and icons); badges, FAQs, stats, about copy and
CTA headline are composed from the niche's keyword and services, worded for
its business type (`profile`: home, auto, clinic, pro, beauty, care).

Merged into NICHE_CONTENT by niche_content.py, same schema as the rest.
"""
import hashlib
import re

MORE_NICHES = {}


def _esc(s):
    return re.sub(r"&(?!amp;|quot;|#39;|lt;|gt;)", "&amp;", s)


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def _pick(key, options, salt=""):
    h = int(hashlib.md5((key + salt).encode()).hexdigest(), 16)
    return options[h % len(options)]


def _a(word):
    return "an" if word[:1].lower() in "aeiou" else "a"


BADGES = {
    "home":   ["Licensed & Insured", "Free Estimates", "Upfront Pricing", "Satisfaction Guaranteed"],
    "auto":   ["Certified Technicians", "Free Quotes", "Upfront Pricing", "Warranty on Work"],
    "clinic": ["Licensed Professionals", "New Patients Welcome", "Most Insurance Accepted", "Same-Week Appointments"],
    "pro":    ["Licensed Professionals", "Free Consultation", "Clear, Upfront Fees", "Local & Responsive"],
    "beauty": ["Licensed Professionals", "Easy Online Booking", "Premium Products", "Satisfaction Guaranteed"],
    "care":   ["Insured & Background-Checked", "Flexible Scheduling", "Upfront Pricing", "Satisfaction Guaranteed"],
}

AUDIENCE = {"home": "Homeowners", "auto": "Drivers", "clinic": "Patients", "pro": "Clients",
            "beauty": "Clients", "care": "Families"}


def _faq(key, kw, services, profile):
    s1, s2, s3 = services[0][0], services[1][0], services[2][0]
    kwl = kw.lower()
    if profile == "home":
        return [
            (f"How much does {s1.lower()} cost?",
             "Every job is different, so we look first and then give you a written, upfront price — free and with no "
             "obligation. The price we quote is the price you pay."),
            ("Are you licensed and insured?",
             "Yes. We're fully licensed and insured, and we're happy to send proof before any work starts."),
            ("How soon can you get started?",
             "Most estimates happen within 24-48 hours, and many jobs can start the same week. Call us for urgent work."),
            (f"Do you also offer {s2.lower()} and {s3.lower()}?",
             f"Yes — along with {s1.lower()}, we handle {s2.lower()}, {s3.lower()} and more, so one call covers it."),
        ]
    if profile == "auto":
        return [
            (f"How much does {s1.lower()} cost?",
             "It depends on your vehicle and what it needs. We give you a clear quote before any work begins — no surprises."),
            ("Do you work on all makes and models?",
             "Yes. Domestic, Asian and European cars, trucks and SUVs."),
            ("Is your work guaranteed?",
             "Yes. Parts and labor come with a written warranty, and we stand behind every job."),
            ("How quickly can you help?",
             "Most jobs are booked within a day or two, and many are done the same day. Call us to check today's availability."),
        ]
    if profile == "clinic":
        return [
            ("Are you accepting new patients?",
             "Yes. New patients are always welcome, and we can usually see you within the same week."),
            ("Do you accept insurance?",
             "We accept most major insurance plans and will check your coverage before your visit. Self-pay options are available."),
            (f"What happens at a first {kwl.split()[-1]} visit?",
             "We listen to your concerns, do a thorough assessment and explain your options and costs clearly before anything is done."),
            (f"Do you offer {s2.lower()}?",
             f"Yes — we offer {s1.lower()}, {s2.lower()}, {s3.lower()} and more under one roof."),
        ]
    if profile == "pro":
        return [
            ("Is the first consultation free?",
             "Yes. Your first consultation is free and confidential, with no obligation to go further."),
            ("How are your fees structured?",
             "We explain our fees in writing before any work begins, so you always know what to expect."),
            (f"Do you handle {s2.lower()}?",
             f"Yes — {s1.lower()}, {s2.lower()}, {s3.lower()} and more are all part of what we do every day."),
            ("Can we meet virtually?",
             "Yes. We offer in-person, phone and video appointments — whatever is easiest for you."),
        ]
    if profile == "beauty":
        return [
            ("How do I book an appointment?",
             "Call us or send the form on this page and we'll confirm a time. Walk-ins are welcome when we have space."),
            (f"How much does {s1.lower()} cost?",
             "Prices depend on the service and your goals. We'll give you a clear price before we start — no surprises."),
            ("Are your professionals licensed?",
             "Yes. Every member of our team is fully licensed and trained, and we use professional-grade products."),
            (f"Do you offer {s2.lower()}?",
             f"Yes — {s1.lower()}, {s2.lower()}, {s3.lower()} and more."),
        ]
    # care
    return [
        ("How do I book?",
         "Call us or send the form on this page and we'll get you booked in — usually within the same week."),
        (f"How much does {s1.lower()} cost?",
         "Pricing depends on what you need. We'll give you a clear, upfront price before we start."),
        ("Are you insured and background-checked?",
         "Yes. We're fully insured, and every team member is background-checked and trained."),
        (f"Do you offer {s2.lower()}?",
         f"Yes — {s1.lower()}, {s2.lower()}, {s3.lower()} and more."),
    ]


def _stats(key, profile):
    years = _pick(key, ["8", "10", "12", "14", "15", "17", "20"], "y")
    done = _pick(key, ["1200", "1800", "2400", "3100", "4200", "5600", "7300"], "d")
    sat = _pick(key, ["97", "98", "99"], "s")
    noun = {"home": "Jobs Completed", "auto": "Vehicles Serviced", "clinic": "Patients Seen",
            "pro": "Clients Helped", "beauty": "Happy Clients", "care": "Happy Clients"}[profile]
    third = {"home": ("Free", "", "Estimates"), "auto": ("Free", "", "Quotes"), "clinic": ("Same", "", "Week Visits"),
             "pro": ("Free", "", "Consultation"), "beauty": ("Easy", "", "Online Booking"), "care": ("Flexible", "", "Scheduling")}[profile]
    return [(done, "+", noun), (years, "+", "Years Local"), third, (sat, "%", "Satisfaction")]


def _about(key, kw, profile, tagline):
    h2 = _pick(key, {
        "home": ["Done Right the First Time", "Local Pros Who Show Up", "Honest Work, Fair Prices",
                 "Quality You Can See", "The Team Your Neighbors Call"],
        "auto": ["Honest Work on Every Vehicle", "Back on the Road, Done Right", "Straight Answers, Fair Prices"],
        "clinic": ["Care That Puts You First", "Unhurried, Personal Care", "Modern Care, Local Team"],
        "pro": ["Clear Advice, Real Results", "On Your Side From Day One", "Experience You Can Rely On"],
        "beauty": ["Look and Feel Your Best", "Skilled Hands, Relaxed Space", "Detail in Every Appointment"],
        "care": ["Care You Can Count On", "Trusted by Local Families", "Reliable, Friendly, Local"],
    }[profile])
    body = {
        "home": [f"Locally owned, serving {{city}} and {{county}}. We specialise in {kw.lower()} work and treat every home like our own.",
                 "Clear written quotes, tidy job sites and a team that shows up when we say we will — that's why neighbours keep calling us back."],
        "auto": [f"Locally owned, serving drivers across {{city}} and {{county}}. {tagline} by certified technicians with the right tools.",
                 "We explain what your vehicle needs, quote it upfront and never start extra work without your OK."],
        "clinic": [f"A local practice caring for patients across {{city}} and {{county}}. {tagline} with time to listen and explain.",
                   "Modern equipment, a friendly team and clear costs before treatment — so you can feel confident about your care."],
        "pro": [f"A local firm serving clients across {{city}} and {{county}}. {tagline} with straight answers and steady communication.",
                "You'll always know what's happening, what it costs and what comes next."],
        "beauty": [f"A local studio serving clients across {{city}} and {{county}}. {tagline} by licensed, experienced professionals.",
                   "Premium products, spotless rooms and a team that takes the time to get it exactly right."],
        "care": [f"Locally owned, serving families across {{city}} and {{county}}. {tagline} by a trained, background-checked team.",
                 "Reliable scheduling, upfront pricing and genuine care in everything we do."],
    }[profile]
    return h2, body


def _cta(key, kw, profile):
    return _pick(key, {
        "home": [f"Ready to Get Started?", "Get Your Free Estimate Today", "One Call and It's Handled",
                 "Let's Get It Fixed", "Talk to a Local Pro Today"],
        "auto": ["Get Back on the Road", "Book Your Service Today", "Let's Take a Look"],
        "clinic": ["Book Your Visit Today", "Feel Better, Sooner", "Take the First Step Today"],
        "pro": ["Let's Talk About Your Situation", "Book Your Free Consultation", "Get Clear Answers Today"],
        "beauty": ["Book Your Appointment Today", "Treat Yourself This Week", "Your New Look Is Waiting"],
        "care": ["Book Today", "Let Us Help", "Get Started Today"],
    }[profile], "cta")


def M(key, theme, logo, kw, tagline, hook, services, profile="home", photos=None,
      audience=None, radius=None, sub=None):
    """services: 'Name|icon|description; Name|icon|description; ...' (6 items)."""
    svc = [tuple(x.strip() for x in part.split("|")) for part in services.split(";") if part.strip()]
    assert len(svc) == 6 and all(len(s) == 3 for s in svc), (key, len(svc))
    assert key not in MORE_NICHES, key
    names = ", ".join(s[0].lower() for s in svc[:3])
    if sub is None:
        where = "{city} & {county}"
        sub = {
            "home": f"{tagline} across {where} — {names} and more. Upfront pricing, careful work, and a local team that answers the phone.",
            "auto": f"{tagline} across {where} — {names} and more. Honest quotes and work you can count on.",
            "clinic": f"{tagline} for patients across {where} — {names} and more, with time to listen and clear costs upfront.",
            "pro": f"{tagline} for clients across {where} — {names} and more. Straight answers, clear fees, real results.",
            "beauty": f"{tagline} in {where} — {names} and more, by licensed professionals in a relaxed, spotless space.",
            "care": f"{tagline} across {where} — {names} and more, from a friendly, trusted local team.",
        }[profile]
    h2, body = _about(key, kw, profile, tagline)
    d = {
        "theme": theme,
        "logo": "lucide:" + logo,
        "profile": profile,
        "tagline": _esc(tagline),
        "h1_keyword": _esc(kw),
        "hero_hook": _esc(hook),
        "hero_sub": _esc(sub),
        "badges": [_esc(b) for b in BADGES[profile]],
        "services": [(_slug(n), _esc(n), "lucide:" + ic, _esc(desc)) for n, ic, desc in svc],
        "faq": [(_esc(q), _esc(a)) for q, a in _faq(key, kw, svc, profile)],
        "stats": _stats(key, profile),
        "about_h2": _esc(h2),
        "about_body": [_esc(p) for p in body],
        "cta_h2": _esc(_cta(key, kw, profile)),
        "audience": audience or AUDIENCE[profile],
    }
    if photos:
        d["photos"] = photos
    if radius:
        d["radius"] = radius
    MORE_NICHES[key] = d


from niche_more_data import *  # noqa: E402,F401,F403  (the M(...) calls)
