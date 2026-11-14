# -*- coding: utf-8 -*-
"""
niche_content.py
----------------
Pre-written content dictionary for the site-generation engine.
ZERO runtime API calls — every niche's services, FAQ, hero copy, and
trust badges are written once, here, and reused for every business
in that niche (only name/phone/city/areas get swapped per-site).

Already-built as full reference sites (content already proven, not
duplicated here — engine pulls their pattern directly):
  roofing, junk_removal, dumpster_rental, plumbing, landscaping, cleaning

This file covers the next 10:
  hvac, electrician, water_heater, garage_door, storm_damage,
  pest_control, lawn_care, tree_service, fencing, gutter_cleaning

Each niche entry:
  theme       -> palette name from theme.PALETTES ("green", "blue", "amber", ...)
                 — sets the accent colours AND the tinted page background
  logo        -> Lucide icon used as the brand mark (optional)
  audience    -> who the reviews speak for, default "Homeowners" (optional)
  tagline     -> topbar one-liner
  hero_h1     -> (line1, line2, highlight_word)
  hero_sub    -> paragraph under H1
  badges      -> 4 short trust badges (hero + about section)
  services    -> 6 x (slug, name, icon, short_desc)
  faq         -> 4 x (question, answer)
  stats       -> 4 x (number, suffix, label)   for hero side-card / stats bar
  about_h2    -> about section headline
  about_body  -> 2 short paragraphs
  cta_h2      -> final CTA headline
"""

import re

NICHE_CONTENT = {

# ============================================================= ROOFING
"roofing": {
    "theme": "orange",
    "logo": "lucide:home",
    "tagline": "24/7 Emergency Roof Repair",
    "h1_keyword": "Roofing Contractor",
    "hero_hook": "Free Inspection &amp; Insurance Claims Handled",
    "hero_sub": "Roof repair, replacement, and storm damage restoration for homes across {city} &amp; {county}. Free inspection, insurance claims handled.",
    "badges": ["Licensed &amp; Insured", "Free Roof Inspection", "24/7 Storm Response", "Insurance Claims Handled"],
    "services": [
        ("roof-repair", "Roof Repair", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Leaks, missing shingles, and wind damage fixed at the source — not just patched over."),
        ("roof-replacement", "Roof Replacement", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Full tear-off and rebuild in architectural shingle, metal, or tile — most homes done in 1-2 days."),
        ("storm-damage", "Storm &amp; Hail Damage", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Emergency tarping within 24 hours and full documentation for your insurance claim."),
        ("free-inspection", "Free Roof Inspection", "M11 11m-7 0a7 7 0 1 0 14 0a7 7 0 1 0-14 0|m20 20-3.5-3.5",
         "A full walk of the roof, photos of anything found, and a written estimate — no cost, no pressure."),
        ("gutter-installation", "Gutter Installation", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Seamless gutters, guards, and repair so a good roof doesn't fail from water with nowhere to go."),
        ("slate-restoration", "Slate &amp; Tile Restoration", "M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1L12 21l7.7-7.6 1.1-1a5.5 5.5 0 0 0 0-7.8z",
         "Cracked slate and slipped tiles brought back without a full tear-off."),
    ],
    "faq": [
        ("How much does a roof replacement cost?", "Most homes fall between $8,000 and $18,000 depending on size, pitch, and material. Storm damage claims often cover most of it."),
        ("Do you handle insurance claims for storm damage?", "Yes. We document damage with photos, meet your adjuster, and handle the paperwork."),
        ("How fast can you respond after a storm?", "Emergency tarping within 24 hours. Full repairs typically scheduled the same week."),
        ("Is the roof inspection really free?", "Yes. We walk the roof, photograph what we find, and give a written estimate — even if the answer is your roof is fine."),
    ],
    "stats": [("2500","+","Roofs Completed"),("15","+","Years Experience"),("24hr","","Storm Response"),("98","%","Satisfaction")],
    "about_h2": "Not a Storm-Chaser. A Neighbor.",
    "about_body": ["Locally owned, serving {city} and {county}. We're not an outfit that shows up after hail season and disappears — our reputation is the only marketing we've got.",
                   "Every job gets an honest inspection, a written estimate before anything starts, and a crew that cleans up after itself."],
    "cta_h2": "Repair or Replace? Find Out for Free.",
},

# ========================================================= JUNK REMOVAL
"junk_removal": {
    "theme": "emerald",
    "logo": "lucide:truck",
    "tagline": "Same-Day Junk Removal",
    "h1_keyword": "Junk Removal",
    "hero_hook": "Same-Day Service, Flat-Rate Pricing",
    "hero_sub": "Furniture, appliances, estate cleanouts, and construction debris hauled away across {city} &amp; {county}. Flat-rate pricing, quoted before we touch anything.",
    "badges": ["Licensed &amp; Insured", "Flat-Rate Pricing", "Donate &amp; Recycle First", "Same-Day Service"],
    "services": [
        ("furniture-removal", "Furniture Removal", "M20 9V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v3|M4 9a2 2 0 0 0-2 2v5h20v-5a2 2 0 0 0-2-2Z|M4 19v-3M20 19v-3",
         "Couches, mattresses, tables, dressers — heavy lifting handled, no stairs too tight."),
        ("estate-cleanouts", "Estate &amp; Home Cleanouts", "M3 21h18|M5 21V7l7-4 7 4v14",
         "Full property cleanouts for moves, downsizing, or after a loss, handled with care."),
        ("appliance-removal", "Appliance Removal", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Fridges, washers, dryers, water heaters — disconnected, hauled, disposed of properly."),
        ("construction-debris", "Construction Debris", "M2 20h20|M12 4a8 8 0 0 0-8 8v4h16v-4a8 8 0 0 0-8-8z",
         "Drywall, wood scraps, renovation waste — cleared fast so your job site keeps moving."),
        ("dumpster-rental-addon", "Dumpster Rental", "M3 21h18|M5 21V7l7-4 7 4v14|M9 9h2M9 13h2M15 9h2M15 13h2",
         "Roll-off dumpsters delivered for larger projects — no permit hassle on your end."),
        ("same-day-pickup", "Same-Day Pickup", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Call before noon, we're usually there the same afternoon."),
    ],
    "faq": [
        ("How much does junk removal cost?", "Single-item pickups run $75-$150. Full truckloads run $350-$600. We quote a flat price before touching anything."),
        ("Do you offer same-day junk removal?", "Yes, in most cases. Call before noon and we usually have a truck out same-day."),
        ("What items can't you take?", "We can't legally haul hazardous materials like paint, chemicals, or asbestos. Everything else, we take."),
        ("Do you donate or recycle items?", "Yes. Usable items go to donation centers first, recyclables get recycled, landfill is the last option."),
    ],
    "stats": [("4100","+","Jobs Completed"),("9","+","Years Local"),("70","%","Donated / Recycled"),("60","min","Avg Response")],
    "about_h2": "Locally Owned. We Do the Lifting.",
    "about_body": ["Family-owned, working out of {city} across {county}. Same crew usually shows up, not a rotating group of strangers.",
                   "We sort every load before it leaves your driveway — donation first, recycling second, landfill last."],
    "cta_h2": "That Pile Isn't Going to Haul Itself",
},

# ========================================================= DUMPSTER RENTAL
"dumpster_rental": {
    "theme": "yellow",
    "logo": "lucide:container",
    "tagline": "Dumpster Rental — Next-Day Delivery",
    "h1_keyword": "Dumpster Rental",
    "hero_hook": "Next-Day Delivery, Flat-Rate Pricing",
    "hero_sub": "10 to 30-yard roll-off containers for cleanouts, renovations, and job sites across {city} &amp; {county}. Flat-rate pricing, no permit hassle.",
    "badges": ["Next-Day Delivery", "Flat-Rate, No Hidden Fees", "Driveway Protected", "Licensed &amp; Insured"],
    "services": [
        ("10-yard", "10 Yard Dumpster", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Small cleanouts, single-room reno, garage declutter."),
        ("20-yard", "20 Yard Dumpster", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Kitchen/bath remodel, roofing job, medium cleanout — our most popular size."),
        ("30-yard", "30 Yard Dumpster", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Whole-home renovation, new construction debris."),
        ("40-yard", "40 Yard Dumpster", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Commercial jobs, demolition, large-scale cleanout."),
        ("residential-dumpster", "Residential Delivery", "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
         "Driveway protection boards under every container, standard on every delivery."),
        ("commercial-dumpster", "Commercial &amp; Job Site", "M3 21h18|M5 21V7l7-4 7 4v14",
         "Scheduled swaps for active job sites so debris never piles up."),
    ],
    "faq": [
        ("How much does a dumpster rental cost?", "Flat rates run $349-$599 depending on size, including delivery, pickup, and standard weight allowance."),
        ("Do I need a permit for a dumpster in my driveway?", "No permit needed on your own driveway. If it needs to go on the street, we pull the permit for you."),
        ("How fast can you deliver?", "Next-day delivery in most cases, same-day if you call before 11am."),
        ("What can't go in the dumpster?", "No paint, chemicals, tires, batteries, or hazardous waste. Everything else is fine."),
    ],
    "stats": [("1800","+","Dumpsters Delivered"),("6","+","Years Local"),("24hr","","Avg Delivery Time"),("0","","Hidden Fees Ever")],
    "about_h2": "Flat-Rate Pricing, No Permit Headaches",
    "about_body": ["Locally owned, serving {city} and {county}. We quote one flat price up front — delivery, pickup, and standard weight included.",
                   "1,800+ dumpsters delivered, and every one comes with driveway protection as standard, not an upsell."],
    "cta_h2": "Project Ready to Start? Get the Dumpster First.",
},

# ========================================================= PLUMBING
"plumbing": {
    "theme": "blue",
    "logo": "lucide:droplet",
    "tagline": "24/7 Emergency Plumbing",
    "h1_keyword": "Plumber",
    "hero_hook": "24/7 Emergency Service, Free Estimates",
    "hero_sub": "Leaks, clogs, water heaters, and full repipes handled by licensed plumbers across {city} &amp; {county}. Upfront pricing, quoted before we start.",
    "badges": ["Licensed &amp; Insured", "Free Written Estimates", "24/7 Emergency", "No After-Hours Upcharge"],
    "services": [
        ("leak-detection", "Leak Detection &amp; Repair", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Slab leaks, wall leaks, and slow drips found without tearing your house apart."),
        ("drain-cleaning", "Drain Cleaning", "M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.683 3 4 3.683 4 4.5V17a5 5 0 0 0 5 5h6a5 5 0 0 0 5-5v-2|M6 12h16",
         "Camera-inspected, snake or hydro-jetted, cleared at the source."),
        ("water-heater-svc", "Water Heater Repair &amp; Install", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Tank and tankless, gas and electric — repaired or replaced, usually same day."),
        ("emergency-plumbing", "24/7 Emergency Plumbing", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Burst pipes, sewage backup, no water — dispatched day or night."),
        ("fixture-install", "Fixture Installation", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Faucets, toilets, garbage disposals, and sinks installed right and tested before we leave."),
        ("repiping", "Repiping", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Old galvanized or copper pipe replaced whole-home, planned around your schedule."),
    ],
    "faq": [
        ("How much does a plumber cost?", "Most standard calls run $150-$350. We quote a flat price before starting, not an hourly rate that keeps climbing."),
        ("Do you offer 24/7 emergency plumbing?", "Yes. Burst pipes, no hot water, sewage backup — we answer around the clock."),
        ("Are you licensed to work in this state?", "Yes, fully licensed and insured. Every plumber on our team is state-licensed."),
        ("Do you charge for estimates?", "No. Diagnosis and a written quote are free."),
    ],
    "stats": [("5200","+","Jobs Completed"),("14","+","Years Local"),("45","min","Avg Dispatch"),("98","%","First-Visit Fix")],
    "about_h2": "Straight-Talk Plumbing",
    "about_body": ["Locally owned, serving {city} and {county}. Every plumber is state-licensed, not just the person who answers the phone.",
                   "5,200+ jobs completed with a 98% first-visit fix rate. If it takes a second trip, that one's on us."],
    "cta_h2": "A Small Drip Today Is a Big Bill Tomorrow",
},

# ========================================================= LANDSCAPING
"landscaping": {
    "theme": "green",
    "logo": "lucide:flower-2",
    "tagline": "Landscaping &amp; Design — Free Estimate",
    "h1_keyword": "Landscaping Company",
    "hero_hook": "Free Design Consultation",
    "hero_sub": "Landscape design, hardscaping, and outdoor renovations across {city} &amp; {county}. Free on-site consultation, quality materials.",
    "badges": ["Licensed &amp; Insured", "Free Design Consultation", "Quality Materials", "Satisfaction Guaranteed"],
    "services": [
        ("landscape-design", "Landscape Design", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Full yard redesigns — beds, mulch, plantings — built around what survives your climate."),
        ("hardscaping", "Hardscaping &amp; Patios", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Paver patios, retaining walls, and walkways built to drain properly and last."),
        ("irrigation", "Irrigation &amp; Sprinklers", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Installation, repair, and seasonal adjustments so your lawn gets exactly what it needs."),
        ("planting", "Planting &amp; Garden Beds", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "New beds, mulch, and layered plantings that survive more than one season."),
        ("outdoor-lighting", "Outdoor Lighting", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Landscape lighting that highlights your yard and adds security after dark."),
        ("drainage-solutions", "Drainage Solutions", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Standing water and erosion fixed at the source, not just moved somewhere else."),
    ],
    "faq": [
        ("How much does a landscape redesign cost?", "Depends heavily on scope — small bed refreshes start around $800, full redesigns can run several thousand. We quote after an on-site walk."),
        ("Do you offer free design consultations?", "Yes, we walk the property and discuss options before any commitment."),
        ("What's the best time of year to landscape?", "Spring and fall are ideal for most planting, though hardscaping can be done nearly year-round."),
        ("Are you licensed and insured?", "Yes, fully licensed and insured for landscaping and hardscape construction."),
    ],
    "stats": [("1900","+","Yards Serviced"),("12","+","Years Local"),("97","%","Satisfaction"),("48","hr","Quote Turnaround")],
    "about_h2": "Local Landscaping Since 2012",
    "about_body": ["Family-owned, serving {city} and {county}. We design around what actually survives your climate, not just what looks good on day one.",
                   "Every project gets a written quote after we've actually seen the property — no phone-quote surprises."],
    "cta_h2": "Stop Fighting Your Own Yard",
},

# ========================================================= CLEANING
"cleaning": {
    "theme": "cyan",
    "logo": "lucide:sparkles",
    "tagline": "House Cleaning — Free Quote",
    "h1_keyword": "House Cleaning Company",
    "hero_hook": "Bonded &amp; Background-Checked Staff",
    "hero_sub": "Recurring and one-time house cleaning across {city} &amp; {county}. Bonded and background-checked cleaners, upfront flat-rate pricing.",
    "badges": ["Bonded &amp; Insured", "Background-Checked Staff", "Eco-Friendly Products", "Satisfaction Guaranteed"],
    "services": [
        ("recurring-cleaning", "Recurring House Cleaning", "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
         "Weekly, bi-weekly, or monthly visits. Same trusted cleaner assigned to your home each time."),
        ("deep-cleaning", "Deep Cleaning", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Baseboards, inside appliances, grout — the once-a-year reset regular cleaning skips."),
        ("move-in-out", "Move-In / Move-Out Cleaning", "M20 9V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v3|M4 9a2 2 0 0 0-2 2v5h20v-5a2 2 0 0 0-2-2Z",
         "Empty-home deep clean for closings and move day — cabinets, closets, appliances."),
        ("carpet-upholstery", "Carpet &amp; Upholstery Cleaning", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Steam extraction for carpets, sofas, and area rugs — lifts what vacuuming leaves behind."),
        ("office-cleaning", "Office &amp; Commercial Cleaning", "M3 21h18|M5 21V7l7-4 7 4v14",
         "After-hours cleaning for offices and small retail, scheduled around your business hours."),
        ("special-occasion", "Special Occasion Cleaning", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Before guests arrive or after they leave — party prep and post-event resets."),
    ],
    "faq": [
        ("How much does house cleaning cost?", "Recurring cleans typically run $120-$220 per visit depending on home size and frequency. Quoted flat by phone before booking."),
        ("Do I need to be home during the cleaning?", "No. Most clients provide a key or entry code. All staff are background-checked and bonded."),
        ("Do you bring your own supplies?", "Yes, all supplies and equipment included, eco-friendly products by default."),
        ("What if I'm not happy with a clean?", "Tell us within 24 hours and we'll send someone back to fix it at no charge."),
    ],
    "stats": [("3200","+","Cleans Completed"),("8","+","Years Local"),("98","%","Client Retention"),("24hr","","Quote Turnaround")],
    "about_h2": "Trusted Cleaning Since 2017",
    "about_body": ["Locally owned, serving {city} and {county}. Every cleaner is background-checked and trained on our exact checklist — same standard, every visit.",
                   "3,200+ cleans completed and 98% client retention — most clients stay with us for years, not months."],
    "cta_h2": "Give Yourself Back Your Saturday",
},


"hvac": {
    "theme": "sky",
    "logo": "lucide:thermometer",
    "tagline": "24/7 Emergency HVAC Service",
    "h1_keyword": "HVAC Repair Company",
    "hero_hook": "24/7 Emergency Service, Same-Day Repairs",
    "hero_sub": "AC repair, furnace service, and full system installs — licensed HVAC techs serving {city} &amp; {county}. Upfront pricing, same-day service most calls.",
    "badges": ["Licensed &amp; Insured", "Same-Day Service", "24/7 Emergency", "Free Estimates"],
    "services": [
        ("ac-repair", "AC Repair", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "No cooling? Diagnosed and usually fixed same-day, refrigerant and parts included in the quote."),
        ("furnace-repair", "Furnace Repair", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Ignition issues, no heat, strange noises — found and fixed before the next cold night."),
        ("ac-installation", "AC &amp; Furnace Installation", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Full system replacement sized correctly for your home, not oversized to upsell you."),
        ("maintenance-plans", "Maintenance Plans", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Twice-yearly tune-ups that catch small problems before they become a broken system in July."),
        ("ductwork", "Ductwork &amp; Airflow", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Uneven temperatures room to room usually means duct leaks or bad sizing — we find it."),
        ("emergency-hvac", "24/7 Emergency Service", "M13 2 3 14h9l-1 8 10-12h-9z",
         "No heat in winter or no AC in a heat wave — we answer and dispatch, day or night."),
    ],
    "faq": [
        ("How much does AC repair cost?", "Most repairs run $150-$450 depending on the part. We diagnose first and give a flat quote before any work starts — no hourly surprises."),
        ("Do you offer emergency HVAC service?", "Yes, 24/7. No-heat and no-AC calls get priority dispatch, including nights and weekends."),
        ("How often should I service my HVAC system?", "Twice a year — once before summer, once before winter. Regular maintenance is the biggest factor in avoiding a mid-season breakdown."),
        ("Are you licensed to work on gas furnaces?", "Yes, fully licensed and insured for both gas and electric systems."),
    ],
    "stats": [("3800","+","Systems Serviced"),("13","+","Years Local"),("45","min","Avg Response"),("97","%","Same-Visit Fix")],
    "about_h2": "Straight-Talk HVAC Since 2012",
    "about_body": ["Locally owned, serving {city} and {county} for over a decade. The tech who diagnoses your system is the same one licensed to fix it — no subcontractors, no guesswork.",
                   "We size equipment for your actual home, not the biggest unit we can sell. That's why most of our new customers come from referrals, not ads."],
    "cta_h2": "Don't Wait For a Breakdown in July",
},

# ========================================================= ELECTRICIAN
"electrician": {
    "theme": "amber",
    "logo": "lucide:zap",
    "tagline": "Licensed Electrician — Same-Day Service",
    "h1_keyword": "Electrician",
    "hero_hook": "Licensed &amp; Same-Day Service",
    "hero_sub": "Panel upgrades, outlet installs, troubleshooting, and full rewiring — licensed electricians serving {city} &amp; {county}. Free estimates, upfront pricing.",
    "badges": ["Licensed Master Electrician", "Free Estimates", "24/7 Emergency", "Code-Compliant Work"],
    "services": [
        ("panel-upgrades", "Panel Upgrades", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Old fuse box or undersized panel replaced with a properly rated, code-compliant panel."),
        ("outlet-switch", "Outlet &amp; Switch Installation", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "New outlets, GFCI upgrades, dimmer switches — installed to code, tested before we leave."),
        ("troubleshooting", "Electrical Troubleshooting", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Flickering lights, tripped breakers, dead outlets — we trace it to the actual cause."),
        ("whole-home-rewiring", "Whole-Home Rewiring", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Old knob-and-tube or aluminum wiring replaced safely, room by room or all at once."),
        ("ceiling-fans", "Ceiling Fans &amp; Fixtures", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Light fixtures, ceiling fans, and chandeliers mounted and wired safely, no wobble."),
        ("ev-chargers", "EV Charger Installation", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Home EV charger installed on a dedicated circuit sized for your vehicle and panel."),
    ],
    "faq": [
        ("How much does it cost to hire an electrician?", "Most standard jobs (outlet install, switch replacement) run $120-$300. Panel upgrades and rewiring are quoted after an in-person look — always in writing before we start."),
        ("Is it normal for breakers to trip occasionally?", "Occasional trips during a storm are normal. Frequent trips without an obvious cause usually mean an overloaded circuit or a wiring issue — worth a look before it becomes a fire risk."),
        ("Are you licensed for panel upgrades?", "Yes, fully licensed and insured, and all panel work is permitted and inspected per local code."),
        ("Do you offer emergency electrical service?", "Yes, 24/7 for active hazards like sparking outlets, burning smells, or total power loss."),
    ],
    "stats": [("4600","+","Jobs Completed"),("16","+","Years Local"),("40","min","Avg Response"),("99","%","Code Pass Rate")],
    "about_h2": "Licensed Electricians Since 2008",
    "about_body": ["Family-owned, serving {city} and {county}. Every electrician on the team is state-licensed and every job is permitted and inspected where required — not cut corners to save time.",
                    "We explain what we find in plain language before any work starts, so you're deciding with real information, not a scare tactic."],
    "cta_h2": "That Flicker Isn't Nothing",
},

# ========================================================= WATER HEATER
"water_heater": {
    "theme": "red",
    "logo": "lucide:flame",
    "tagline": "Water Heater Repair &amp; Install — Same Day",
    "h1_keyword": "Water Heater Repair &amp; Installation",
    "hero_hook": "Same-Day Service Available",
    "hero_sub": "Tank and tankless water heater repair, replacement, and installation serving {city} &amp; {county}. Most jobs finished same-day, upfront flat pricing.",
    "badges": ["Licensed &amp; Insured", "Same-Day Install", "All Brands Serviced", "Free Estimates"],
    "services": [
        ("water-heater-repair", "Water Heater Repair", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "No hot water, rusty water, or strange noises — diagnosed and usually fixed same visit."),
        ("tank-replacement", "Tank Water Heater Replacement", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Old tank swapped for a properly sized new one, usually done in half a day."),
        ("tankless-install", "Tankless Water Heater Install", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Endless hot water and smaller footprint — sized and installed for your home's demand."),
        ("leak-repair", "Leak &amp; Corrosion Repair", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "A leaking tank rarely gets better — we assess whether it's a quick fix or time to replace."),
        ("emergency-water-heater", "Emergency No-Hot-Water Service", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Cold showers aren't an emergency you should wait days for — same-day dispatch."),
        ("water-heater-maintenance", "Annual Maintenance &amp; Flush", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Sediment flush extends tank life significantly — a 30-minute job that saves years."),
    ],
    "faq": [
        ("How much does a new water heater cost installed?", "Tank replacements typically run $1,200-$2,200 installed. Tankless units run higher upfront but lower operating cost long-term. We quote both options in writing."),
        ("Can you install same-day if my tank fails?", "In most cases yes, if the unit is in stock for your size and fuel type. We prioritize no-hot-water calls."),
        ("Tank or tankless — which is better?", "Depends on household size and usage pattern. We walk through the tradeoffs honestly rather than pushing the higher-margin option."),
        ("Do you service gas and electric water heaters?", "Yes, both, plus tankless gas and electric units from all major brands."),
    ],
    "stats": [("2900","+","Water Heaters Installed"),("11","+","Years Local"),("Same","Day","Most Installs"),("97","%","First-Visit Fix")],
    "about_h2": "Water Heater Specialists Since 2014",
    "about_body": ["Locally owned, serving {city} and {county}. We carry common tank sizes on the truck, which is why most replacements happen the same day you call.",
                    "We'll tell you honestly if a repair makes more sense than a replacement — a 3-year-old tank with one bad part shouldn't be thrown out."],
    "cta_h2": "Cold Showers Aren't a Life Sentence",
},

# ========================================================= GARAGE DOOR
"garage_door": {
    "theme": "slate",
    "logo": "lucide:door-open",
    "tagline": "Garage Door Repair &amp; Install — Same Day",
    "h1_keyword": "Garage Door Repair Company",
    "hero_hook": "Same-Day Service, Free Estimates",
    "hero_sub": "Spring replacement, opener repair, and full door installation serving {city} &amp; {county}. Same-day service, upfront flat pricing.",
    "badges": ["Licensed &amp; Insured", "Same-Day Service", "All Brands Serviced", "Free Estimates"],
    "services": [
        ("spring-replacement", "Spring Replacement", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "A snapped spring means a dead door — replaced safely same-day, both springs matched."),
        ("opener-repair", "Opener Repair &amp; Installation", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Remote not working, door reversing, or dead opener — repaired or replaced same visit."),
        ("door-installation", "New Garage Door Installation", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Full door replacement — wood, steel, or insulated, sized and hung correctly."),
        ("cable-track-repair", "Cable &amp; Track Repair", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Off-track or frayed cable doors are dangerous to force — fixed properly, not jammed back on."),
        ("panel-replacement", "Panel &amp; Dent Repair", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Damaged panel from a backed-into door or storm — replaced to match, not a full new door."),
        ("emergency-garage-door", "Same-Day Emergency Repair", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Stuck door blocking your car isn't a next-week problem — same-day dispatch."),
    ],
    "faq": [
        ("How much does garage door spring replacement cost?", "Typically $200-$450 for both springs, done together since they wear at the same rate. Quoted flat before we start."),
        ("Why is my garage door making a loud bang or not opening?", "Usually a broken spring or worn cable. Don't try to force it open — it's under heavy tension and can cause injury."),
        ("Do you install openers from all brands?", "Yes — LiftMaster, Chamberlain, Genie, and most others, including smart/Wi-Fi models."),
        ("Can you come same-day if my door is stuck shut?", "In most cases yes, especially if your car is trapped inside — those calls get priority."),
    ],
    "stats": [("3100","+","Doors Serviced"),("10","+","Years Local"),("Same","Day","Most Repairs"),("98","%","First-Visit Fix")],
    "about_h2": "Local Garage Door Techs Since 2015",
    "about_body": ["Family-owned, serving {city} and {county}. We carry common springs, cables, and openers on the truck, so most repairs finish in one visit.",
                    "A broken spring is dangerous to DIY — we handle it safely and explain what failed and why, no unnecessary upsells."],
    "cta_h2": "A Stuck Door Won't Fix Itself",
},

# ========================================================= STORM DAMAGE
"storm_damage": {
    "theme": "indigo",
    "logo": "lucide:cloud-lightning",
    "tagline": "24/7 Storm Damage Response",
    "h1_keyword": "Storm Damage Restoration",
    "hero_hook": "24/7 Emergency Response",
    "hero_sub": "Emergency tarping, damage assessment, and full restoration serving {city} &amp; {county}. We document everything and work directly with your insurance.",
    "badges": ["24/7 Emergency Response", "Insurance Claims Handled", "Licensed &amp; Insured", "Free Inspection"],
    "services": [
        ("emergency-tarping", "Emergency Tarping", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Roof or window breach covered within hours of your call to stop further water damage."),
        ("damage-assessment", "Storm Damage Assessment", "M11 11m-7 0a7 7 0 1 0 14 0a7 7 0 1 0-14 0|m20 20-3.5-3.5",
         "Full photo-documented inspection of roof, siding, and gutters after wind or hail."),
        ("insurance-claims", "Insurance Claim Assistance", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z|M14 2v6h6",
         "We meet your adjuster on site and document damage in the terms insurers expect."),
        ("tree-debris-removal", "Fallen Tree &amp; Debris Removal", "M13 12v8M9 4l3-2 3 2M6 8l-3 3 3 3M18 8l3 3-3 3",
         "Trees on the roof or in the yard cleared safely before repairs begin."),
        ("roof-storm-repair", "Roof &amp; Siding Storm Repair", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Wind and hail damage repaired or fully replaced, matched to existing materials."),
        ("water-damage-mitigation", "Water Damage Mitigation", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Standing water and saturated materials removed fast to prevent mold before it starts."),
    ],
    "faq": [
        ("How fast can you respond after a storm?", "Emergency tarping within a few hours in most cases, day or night. Full assessment scheduled within 24-48 hours."),
        ("Do you help with insurance claims?", "Yes. We document all damage with photos, meet your adjuster on site, and provide the scope of work insurers require."),
        ("Will my insurance cover storm damage repair?", "Most homeowner policies cover wind and hail damage. We can't guarantee your specific coverage, but we document thoroughly to support your claim."),
        ("What should I do immediately after storm damage?", "Get photos if it's safe, avoid entering damaged areas, and call for emergency tarping before more water gets in. We can walk you through it on the phone."),
    ],
    "stats": [("1400","+","Storm Jobs"),("12","+","Years Local"),("2hr","","Avg Tarp Response"),("100","%","Insurance Documented")],
    "about_h2": "Storm Response You Can Trust",
    "about_body": ["Locally owned, serving {city} and {county} through every storm season. We're not a storm-chasing crew that disappears after the checks clear — we live here.",
                    "Every job is documented the way insurance companies actually need it, which speeds up your claim instead of slowing it down."],
    "cta_h2": "Every Hour Matters After a Storm",
},

# ========================================================= PEST CONTROL
"pest_control": {
    "theme": "emerald",
    "logo": "lucide:bug",
    "tagline": "Pest Control — Free Inspection",
    "h1_keyword": "Pest Control Company",
    "hero_hook": "Free Inspection, Satisfaction Guaranteed",
    "hero_sub": "Ants, termites, rodents, and seasonal pests handled for homes and businesses across {city} &amp; {county}. Family-safe treatments, free inspection.",
    "badges": ["Licensed &amp; Insured", "Family &amp; Pet Safe", "Free Inspection", "Satisfaction Guaranteed"],
    "services": [
        ("general-pest-control", "General Pest Control", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Ants, spiders, roaches — quarterly or one-time treatment around your home's perimeter."),
        ("termite-treatment", "Termite Inspection &amp; Treatment", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Free inspection for termite damage, with treatment plans that protect the structure."),
        ("rodent-control", "Rodent Control", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Mice and rats trapped and excluded, entry points sealed so they don't come back."),
        ("bed-bug-treatment", "Bed Bug Treatment", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Heat and targeted treatment that gets the whole infestation, not just visible bugs."),
        ("mosquito-control", "Mosquito &amp; Tick Control", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Yard treatments that let you actually use your backyard in summer evenings."),
        ("commercial-pest", "Commercial Pest Control", "M3 21h18|M5 21V7l7-4 7 4v14|M9 9h2M9 13h2M15 9h2M15 13h2M9 21v-4h6v4",
         "Scheduled service for restaurants, offices, and warehouses that keeps you inspection-ready."),
    ],
    "faq": [
        ("How much does pest control cost?", "One-time treatments typically run $150-$300. Quarterly plans run less per visit and catch problems before they grow — most homes do best on a plan."),
        ("Are your treatments safe for kids and pets?", "Yes. We use EPA-registered products applied per label, and can walk you through re-entry timing for extra peace of mind."),
        ("How do I know if I have termites?", "Look for mud tubes near the foundation, hollow-sounding wood, or discarded wings near windows. A free inspection settles it either way."),
        ("Do you guarantee your work?", "Yes. If pests return between scheduled visits, we come back at no charge."),
    ],
    "stats": [("2600","+","Homes Protected"),("9","+","Years Local"),("48","hr","Response Time"),("100","%","Satisfaction Guarantee")],
    "about_h2": "Local Pest Control Since 2016",
    "about_body": ["Family-owned, serving {city} and {county}. We inspect thoroughly before recommending treatment — you'll never get a quote without seeing what we actually found.",
                    "Products are chosen to be effective on pests and safe around the family, applied exactly per label."],
    "cta_h2": "Don't Wait For It to Get Worse",
},

# ========================================================= LAWN CARE
"lawn_care": {
    "theme": "green",
    "logo": "lucide:scissors",
    "tagline": "Weekly Lawn Care — Free Estimate",
    "h1_keyword": "Lawn Care Company",
    "hero_hook": "Free Estimates, Same Crew Every Visit",
    "hero_sub": "Weekly and bi-weekly lawn mowing, edging, and cleanup for homes across {city} &amp; {county}. Same crew every visit, honest flat pricing.",
    "badges": ["Licensed &amp; Insured", "Same Crew Every Visit", "Free Estimates", "Satisfaction Guaranteed"],
    "services": [
        ("lawn-mowing", "Lawn Mowing &amp; Edging", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Weekly or bi-weekly mowing, clean edges, and clippings cleared — same crew every time."),
        ("fertilization", "Fertilization &amp; Weed Control", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Seasonal feeding program that builds a thicker lawn and crowds out weeds naturally."),
        ("aeration-overseeding", "Aeration &amp; Overseeding", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Fall aeration opens compacted soil so new seed and nutrients actually take hold."),
        ("spring-fall-cleanup", "Spring &amp; Fall Cleanup", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Leaves, debris, and dead growth cleared so your yard starts the season right."),
        ("mulching", "Mulch Installation", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Fresh mulch in beds — retains moisture, blocks weeds, and finishes the look."),
        ("lawn-disease-treatment", "Lawn Disease &amp; Pest Treatment", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Brown patches and grubs diagnosed and treated before they spread across the yard."),
    ],
    "faq": [
        ("How much does weekly lawn mowing cost?", "Most residential lawns run $45-$85 per visit depending on size and terrain. We quote after seeing the property, in writing, no surprise add-ons."),
        ("Do you offer one-time cleanups or only recurring plans?", "Both. One-time cleanups for overgrown yards or move-in prep, plus weekly and bi-weekly maintenance plans."),
        ("When should I aerate my lawn?", "Fall is ideal for cool-season grass. We can recommend timing based on your specific lawn type."),
        ("Are you licensed and insured?", "Yes, fully licensed and insured for lawn care and landscaping work."),
    ],
    "stats": [("2100","+","Yards Serviced"),("13","+","Years Local"),("97","%","Satisfaction"),("48","hr","Quote Turnaround")],
    "about_h2": "Your Local Lawn Crew Since 2012",
    "about_body": ["Family-owned, serving {city} and {county}. Same two-person crew handles your property every visit — not a rotating group of strangers.",
                    "We treat every yard like it's the one we'll be back to in two weeks, because we usually are."],
    "cta_h2": "Stop Fighting Your Own Yard",
},

# ========================================================= TREE SERVICE
"tree_service": {
    "theme": "olive",
    "logo": "lucide:trees",
    "tagline": "Tree Trimming &amp; Removal — Free Estimate",
    "h1_keyword": "Tree Service",
    "hero_hook": "Free Estimates, Certified Arborists",
    "hero_sub": "Tree trimming, removal, and stump grinding for homes and properties across {city} &amp; {county}. Certified climbers, fully insured.",
    "badges": ["Licensed &amp; Insured", "Certified Arborists", "Free Estimates", "Storm Cleanup Available"],
    "services": [
        ("tree-trimming", "Tree Trimming &amp; Pruning", "M13 12v8M9 4l3-2 3 2M6 8l-3 3 3 3M18 8l3 3-3 3",
         "Deadwood removal and canopy shaping done with proper cuts, not just hacking branches off."),
        ("tree-removal", "Tree Removal", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Full removal of dead, diseased, or hazardous trees — safely, with cleanup included."),
        ("stump-grinding", "Stump Grinding", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Ground down below grade so you can plant grass or landscape right over it."),
        ("emergency-tree-removal", "Emergency Storm Tree Removal", "M13 2 3 14h9l-1 8 10-12h-9z",
         "A tree on your roof or blocking your driveway isn't a next-week problem — same-day response."),
        ("tree-health-assessment", "Tree Health Assessment", "M11 11m-7 0a7 7 0 1 0 14 0a7 7 0 1 0-14 0|m20 20-3.5-3.5",
         "Disease, pest damage, or root issues diagnosed before a tree becomes a hazard."),
        ("land-clearing", "Land &amp; Lot Clearing", "M3 21h18|M5 21V7l7-4 7 4v14",
         "Overgrown lots cleared for new construction, gardens, or usable yard space."),
    ],
    "faq": [
        ("How much does tree removal cost?", "Typically $400-$1,800 depending on tree size, location, and access. We quote after an on-site look, in writing."),
        ("Do you offer emergency tree removal after a storm?", "Yes, same-day in most cases for trees on structures, vehicles, or blocking access."),
        ("Are your climbers certified?", "Yes, our crew includes certified arborists trained in proper pruning and safe removal techniques."),
        ("What happens to the wood and debris?", "Cleanup is included in every job — we haul away branches, logs, and debris unless you'd like to keep the wood."),
    ],
    "stats": [("1900","+","Trees Serviced"),("11","+","Years Local"),("Same","Day","Storm Response"),("100","%","Insured Crews")],
    "about_h2": "Certified Tree Care Since 2014",
    "about_body": ["Family-owned, serving {city} and {county}. Every climber is trained and insured, and every job is quoted honestly before any cutting starts.",
                    "We handle everything from a single overgrown branch to full lot clearing, with cleanup always included."],
    "cta_h2": "That Leaning Tree Won't Wait",
},

# ========================================================= FENCING
"fencing": {
    "theme": "brown",
    "logo": "lucide:fence",
    "tagline": "Fence Installation &amp; Repair — Free Estimate",
    "h1_keyword": "Fence Company",
    "hero_hook": "Free On-Site Quote",
    "hero_sub": "Wood, vinyl, and chain-link fence installation and repair across {city} &amp; {county}. Free on-site quote, quality materials, clean installs.",
    "badges": ["Licensed &amp; Insured", "Free On-Site Quote", "Quality Materials", "Satisfaction Guaranteed"],
    "services": [
        ("wood-fence-install", "Wood Fence Installation", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Privacy, picket, and split-rail styles installed plumb, level, and built to last."),
        ("vinyl-fence-install", "Vinyl Fence Installation", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Low-maintenance vinyl fencing that won't warp, rot, or need repainting."),
        ("chain-link-install", "Chain Link Fence Installation", "M3 21h18|M5 21V7l7-4 7 4v14",
         "Durable, affordable fencing for yards, pools, and commercial properties."),
        ("fence-repair", "Fence Repair", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Leaning posts, broken panels, and storm damage repaired without replacing the whole fence."),
        ("gate-installation", "Gate Installation &amp; Repair", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Walk gates and driveway gates hung level and swinging smooth, with secure latches."),
        ("commercial-fencing", "Commercial &amp; Security Fencing", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Chain-link and ornamental security fencing for job sites, warehouses, and businesses."),
    ],
    "faq": [
        ("How much does a new fence cost?", "Wood privacy fencing typically runs $25-$45 per linear foot installed; vinyl and chain-link vary by style. We give an exact quote after measuring your property."),
        ("How long does fence installation take?", "Most residential jobs take 1-3 days depending on length and terrain."),
        ("Do I need a permit for a new fence?", "Depends on your local jurisdiction and fence height — we check this as part of the quote so there are no surprises."),
        ("Can you repair just a section instead of replacing the whole fence?", "Yes, in most cases. We assess whether a repair makes sense or if the fence has reached the point where replacement is more cost-effective."),
    ],
    "stats": [("1700","+","Fences Installed"),("10","+","Years Local"),("Free","","On-Site Quotes"),("98","%","Satisfaction")],
    "about_h2": "Local Fence Builders Since 2015",
    "about_body": ["Family-owned, serving {city} and {county}. We measure and quote on-site, not over the phone, so the price you're quoted is the price you pay.",
                    "Every post is set below the frost line and every gate is hung to swing smooth for years, not just look good on installation day."],
    "cta_h2": "Privacy, Property Lines, Peace of Mind",
},

# ========================================================= GUTTER CLEANING
"gutter_cleaning": {
    "theme": "steel",
    "logo": "lucide:droplets",
    "tagline": "Gutter Cleaning — Free Estimate",
    "h1_keyword": "Gutter Cleaning Company",
    "hero_hook": "Free Estimates, Photo Documented",
    "hero_sub": "Gutter cleaning, repair, and guard installation for homes across {city} &amp; {county}. Fully insured, photos before and after every job.",
    "badges": ["Licensed &amp; Insured", "Photo Documentation", "Free Estimates", "Satisfaction Guaranteed"],
    "services": [
        ("gutter-cleaning", "Gutter Cleaning", "M4 6h16v4H4z|M6 10v8a2 2 0 0 0 2 2h2|M18 10v3",
         "Leaves and debris cleared from gutters and downspouts, checked for proper flow."),
        ("gutter-repair", "Gutter Repair", "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
         "Sagging sections, leaks, and separated joints re-secured and sealed."),
        ("gutter-guard-install", "Gutter Guard Installation", "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
         "Guards installed to cut down how often you need cleaning, especially under trees."),
        ("downspout-repair", "Downspout Repair &amp; Extension", "M2 12 12 3l10 9|M5 10v10h14V10|M10 20v-6h4v6",
         "Downspouts redirected away from the foundation to stop water pooling near your home."),
        ("roof-inspection-addon", "Roof &amp; Fascia Inspection", "M11 11m-7 0a7 7 0 1 0 14 0a7 7 0 1 0-14 0|m20 20-3.5-3.5",
         "While we're up there, we check for loose shingles and rotting fascia at no extra charge."),
        ("gutter-cleaning-plans", "Seasonal Cleaning Plans", "M13 2 3 14h9l-1 8 10-12h-9z",
         "Spring and fall cleanings scheduled automatically so you never have to remember."),
    ],
    "faq": [
        ("How much does gutter cleaning cost?", "Most homes run $120-$250 per visit depending on size and number of stories. Quoted flat before we start."),
        ("How often should gutters be cleaned?", "Twice a year for most homes — spring and fall. More often if you have a lot of overhanging trees."),
        ("Do you take before and after photos?", "Yes, every job — so you can see exactly what was cleared and confirm the work from the ground."),
        ("Can clogged gutters actually damage my house?", "Yes — overflow can lead to fascia rot, foundation issues, and basement leaks. It's a cheap fix now versus an expensive one later."),
    ],
    "stats": [("2400","+","Homes Serviced"),("8","+","Years Local"),("Photo","","Documented Jobs"),("98","%","Satisfaction")],
    "about_h2": "Local Gutter Specialists Since 2017",
    "about_body": ["Family-owned, serving {city} and {county}. We check the whole system — gutters, downspouts, and fascia — not just scoop leaves and leave.",
                    "Every job comes with before-and-after photos, so you know exactly what was done even if you weren't home."],
    "cta_h2": "Don't Wait for the Overflow",
},

}


# ---------------------------------------------------------------------------
# 60 additional niches live in niche_content_extra.py (same schema).
# ---------------------------------------------------------------------------
from niche_content_extra import EXTRA_NICHES  # noqa: E402

for _k, _v in EXTRA_NICHES.items():
    if _k in NICHE_CONTENT:
        raise ValueError(f"duplicate niche key: {_k}")
    NICHE_CONTENT[_k] = _v

# 200 more (home trades, outdoor, cleaning, auto, health, legal, beauty, care)
# live in niche_content_more.py.
from niche_content_more import MORE_NICHES  # noqa: E402

for _k, _v in MORE_NICHES.items():
    if _k in NICHE_CONTENT:
        raise ValueError(f"duplicate niche key: {_k}")
    NICHE_CONTENT[_k] = _v


# Lead-list category labels -> niche key. A label that already matches a
# niche key (e.g. "Roofing", "Junk Removal") needs no entry here.
ALIASES = {
    "lawn_landscape": "landscaping", "lawn": "lawn_care", "landscape": "landscaping",
    "doors_windows": "doors_windows", "windows_doors": "doors_windows", "doors": "door_installation",
    "windows": "window_installation", "electric": "electrician", "electrical": "electrician",
    "pools": "pool_service", "pool": "pool_service", "tile": "tile_installation",
    "paving": "paving_asphalt", "asphalt": "paving_asphalt", "granite_countertops": "countertops",
    "granite": "countertops", "solar": "solar_installation", "gutters": "gutter_installation",
    "plastering": "plaster_repair", "garage_doors": "garage_door", "cabinets": "cabinet_installation",
    "contracting": "general_contractor", "contractor": "general_contractor",
    "general_contracting": "general_contractor", "tree": "tree_service", "trees": "tree_service",
    "restoration": "restoration", "hauling": "hauling", "home_improvement": "home_improvement",
    "other": "home_improvement", "pressure_wash": "pressure_washing", "power_washing": "pressure_washing",
    "auto_detail": "auto_detailing", "detailing": "auto_detailing", "movers": "moving",
    "remodel": "remodeling", "tow": "towing", "fence": "fencing", "heating_and_cooling": "hvac",
}


def resolve_key(niche) -> str:
    """Normalise any label ("Lawn/Landscape", "Garage Doors", "roof-repair")
    to a niche key. Unknown labels come back normalised but unmatched."""
    key = str(niche or "").lower().strip().replace("&", "and")
    key = re.sub(r"[^a-z0-9]+", "_", key).strip("_").replace("_and_", "_")
    if key in NICHE_CONTENT:
        return key
    return ALIASES.get(key, key)


def get_niche(niche: str) -> dict:
    """Return content dict for a niche key or category label, or None."""
    return NICHE_CONTENT.get(resolve_key(niche))


def all_niches() -> list:
    return sorted(NICHE_CONTENT.keys())


if __name__ == "__main__":
    n = all_niches()
    print(f"{len(n)} niches with full content:")
    for x in n:
        print(" ", x, "->", NICHE_CONTENT[x]["theme"])
