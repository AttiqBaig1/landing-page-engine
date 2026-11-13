# Landing Page Engine

Give it a business **name, address (City, ST) and phone number** plus a **niche**, and it builds a complete, SEO-ready, single-file landing page — services, about, nearby service areas (from a 27,000-city database), projects, reviews, FAQ with schema markup, contact form and footer.

**76 niches** are included, and every niche has its own colour palette: accent colours *and* a tinted page background (lawn care on deep green, plumbing on deep navy, towing on deep red, and so on).

## Run the app (single + bulk)

```bash
pip install -r requirements.txt
cd engine
streamlit run app.py
```

* **Manual entry** — type one or more businesses and pick a niche.
* **Upload CSV** — bulk mode. Columns: `name, address, phone, niche` (see `engine/sample_leads.csv`).
* Optional one-click publishing to WordPress (REST API + Application Password).

## Bulk from the command line

```bash
cd engine
python run_batch.py sample_leads.csv --out-dir output --results results.csv
```

## Demo gallery (GitHub Pages)

`.github/workflows/pages.yml` (Actions tab → *Run workflow*) builds one sample page per niche with `engine/build_demo.py` and publishes the gallery to GitHub Pages. Pages on a private repo needs a paid GitHub plan; otherwise build it locally with `python build_demo.py --out ../site` and open `site/index.html`.

## Adding a niche

Add an `N(...)` entry to `engine/niche_content_extra.py` (name, palette, logo icon, copy, 6 services, 4 FAQs, 4 stats). Optional:

* `photos="plumbing"` — borrow another niche's photo folder until you add `photo_library/<niche>/original/`
* `radius=(miles, min_population)` — service-area search radius
* `audience="Drivers"` — who the reviews speak for (default "Homeowners")

Palettes live in `engine/theme.py` (`PALETTES`) — one line each; backgrounds, cards and borders are derived automatically.

## Niches by palette

| Palette | Niches |
|---|---|
| amber | `electrician`, `solar_installation` |
| blue | `commercial_cleaning`, `drain_cleaning`, `plumbing`, `water_treatment` |
| brown | `deck_building`, `fencing`, `flooring` |
| crimson | `auto_detailing`, `christmas_lights` |
| cyan | `cleaning`, `pool_service`, `pressure_washing`, `water_damage_restoration` |
| emerald | `junk_removal`, `mold_remediation`, `mosquito_control`, `pest_control` |
| gold | `kitchen_remodeling`, `locksmith` |
| green | `irrigation`, `landscaping`, `lawn_care` |
| ice | `snow_removal`, `window_cleaning` |
| indigo | `carpet_cleaning`, `home_inspection`, `moving`, `security_systems`, `storm_damage` |
| lime | `artificial_turf`, `ev_charger_installation`, `pet_waste_removal` |
| olive | `land_clearing`, `septic_service`, `stump_grinding`, `tree_service`, `wildlife_removal` |
| orange | `dryer_vent_cleaning`, `handyman`, `remodeling`, `roofing` |
| pink | `insulation` |
| purple | `cabinet_refinishing` |
| red | `auto_repair`, `chimney_sweep`, `demolition`, `fire_damage_restoration`, `towing`, `water_heater` |
| sand | `excavation`, `stucco` |
| sky | `air_duct_cleaning`, `appliance_repair`, `hvac`, `window_installation`, `windshield_repair` |
| slate | `concrete`, `countertops`, `drywall`, `epoxy_flooring`, `garage_door`, `paving_asphalt` |
| steel | `custom_home_builder`, `gutter_cleaning`, `gutter_installation`, `siding` |
| teal | `basement_waterproofing`, `bathroom_remodeling`, `tile_installation` |
| terracotta | `foundation_repair`, `masonry` |
| violet | `painting` |
| yellow | `dumpster_rental`, `generator_installation` |
