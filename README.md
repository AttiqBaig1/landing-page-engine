# Landing Page Engine

Give it a business **name, address (City, ST) and phone number** plus a **niche**, and it builds a complete, SEO-ready, single-file landing page — services, about, nearby service areas (from a 27,000-city database), projects, reviews, FAQ with schema markup, contact form and footer.

**278 niches** are included, and every niche has its own colour palette: accent colours *and* a tinted page background (lawn care on deep green, plumbing on deep navy, towing on deep red, and so on).

## Live web app (no install)

**https://attiqbaig1.github.io/landing-page-engine/**

Same screens as the Streamlit app: WordPress connection → 1️⃣ Generate Sites (manual entry or CSV upload, optional one-click publish) → 2️⃣ Preview & Download → 3️⃣ Publish to WordPress (Publish ALL / per site) → Live URLs. The real Python engine runs inside the browser via Pyodide. WordPress credentials stay in your own browser.

Every push to `main` rebuilds and redeploys it (`.github/workflows/pages.yml`, source in `web/`).

## Run the Streamlit app locally (optional)

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

## Adding a niche

Add an `N(...)` entry to `engine/niche_content_extra.py` (name, palette, logo icon, copy, 6 services, 4 FAQs, 4 stats). Optional:

* `photos="plumbing"` — borrow another niche's photo folder until you add `photo_library/<niche>/original/`
* `radius=(miles, min_population)` — service-area search radius
* `audience="Drivers"` — who the reviews speak for (default "Homeowners")

Palettes live in `engine/theme.py` (`PALETTES`) — one line each; backgrounds, cards and borders are derived automatically.

## Niches (278)

Each niche has its own colour palette and wording for its business type (CTA buttons, reviews and trust lines differ for clinics, law firms, salons, auto shops and care services).

**Home & property services (194)** — `ac_installation`, `ac_repair`, `air_duct_cleaning`, `appliance_installation`, `appliance_removal`, `appliance_repair`, `arborist`, `artificial_turf`, `asbestos_removal`, `auto_detailing`, `auto_repair`, `awnings`, `backflow_testing`, `basement_finishing`, `basement_waterproofing`, `bathroom_remodeling`, `bathtub_refinishing`, `bed_bug_treatment`, `bee_removal`, `bird_control`, `boiler_repair`, `cabinet_installation`, `cabinet_refinishing`, `carpentry`, `carpet_cleaning`, `carpet_installation`, `ceiling_fan_installation`, `chimney_sweep`, `christmas_lights`, `cleaning`, `closet_organizers`, `cockroach_control`, `commercial_cleaning`, `commercial_electrician`, `commercial_hvac`, `commercial_pest_control`, `commercial_plumbing`, `commercial_roofing`, `concrete`, `concrete_repair`, `countertops`, `custom_home_builder`, `deck_building`, `deck_staining`, `demolition`, `dock_builder`, `door_installation`, `drain_cleaning`, `drainage_solutions`, `driveway_sealing`, `dryer_vent_cleaning`, `drywall`, `ductless_mini_split`, `dumpster_rental`, `electrical_panel_upgrade`, `electrician`, `emergency_plumber`, `emergency_tree_service`, `epoxy_flooring`, `ev_charger_installation`, `excavation`, `exterior_painting`, `fence_repair`, `fencing`, `fire_damage_restoration`, `fire_protection`, `flooring`, `foundation_repair`, `french_drains`, `furnace_repair`, `garage_door`, `garage_door_opener`, `garage_door_spring`, `gas_line_services`, `gate_installation`, `generator_installation`, `glass_repair`, `gravel_driveway`, `gutter_cleaning`, `gutter_guards`, `gutter_installation`, `handyman`, `hardscaping`, `hardwood_refinishing`, `heat_pump`, `hedge_trimming`, `home_additions`, `home_inspection`, `home_rewiring`, `hood_cleaning`, `hot_tub_repair`, `house_washing`, `hvac`, `indoor_air_quality`, `insulation`, `interior_painting`, `irrigation`, `junk_removal`, `kitchen_remodeling`, `land_clearing`, `landscape_design`, `landscape_lighting`, `landscaping`, `lawn_aeration`, `lawn_care`, `leaf_removal`, `leak_detection`, `lighting_installation`, `locksmith`, `masonry`, `metal_roofing`, `mold_remediation`, `mosquito_control`, `moving`, `mulching`, `outdoor_kitchens`, `outdoor_lighting`, `painting`, `parking_lot_striping`, `patio_covers`, `paver_installation`, `paving_asphalt`, `pergolas`, `pest_control`, `pet_waste_removal`, `plaster_repair`, `plumbing`, `pool_construction`, `pool_repair`, `pool_resurfacing`, `pool_service`, `popcorn_ceiling_removal`, `portable_toilet_rental`, `pressure_washing`, `radon_mitigation`, `refrigerator_repair`, `remodeling`, `repiping`, `retaining_walls`, `rodent_control`, `roof_cleaning`, `roof_inspection`, `roof_repair`, `roofing`, `sandblasting`, `screen_enclosures`, `security_systems`, `septic_service`, `sewage_cleanup`, `sewer_line_repair`, `shed_builder`, `shower_glass`, `siding`, `sign_company`, `skylight_installation`, `smart_home_installation`, `snow_removal`, `sod_installation`, `soffit_fascia`, `solar_installation`, `solar_panel_cleaning`, `spray_foam_insulation`, `sprinkler_repair`, `stamped_concrete`, `storm_damage`, `stucco`, `stump_grinding`, `sump_pump`, `sunroom`, `tankless_water_heater`, `termite_control`, `tile_installation`, `towing`, `tree_planting`, `tree_removal`, `tree_service`, `tree_trimming`, `vinyl_fence`, `vinyl_plank_flooring`, `walk_in_tub`, `wallpaper_installation`, `water_damage_restoration`, `water_features`, `water_heater`, `water_treatment`, `water_well_drilling`, `welding`, `well_pump`, `wildlife_removal`, `window_cleaning`, `window_installation`, `window_tinting`, `windshield_repair`, `xeriscaping`

**Automotive (25)** — `auto_ac_repair`, `auto_body_repair`, `auto_electrical`, `boat_repair`, `brake_repair`, `car_key_replacement`, `car_wash`, `car_wrap`, `ceramic_coating`, `collision_repair`, `diesel_repair`, `fleet_maintenance`, `heavy_duty_towing`, `junk_car_removal`, `mobile_mechanic`, `mobile_tire_service`, `motorcycle_repair`, `oil_change`, `paint_protection_film`, `pre_purchase_inspection`, `roadside_assistance`, `rv_repair`, `tire_shop`, `transmission_repair`, `window_tint_auto`

**Health & clinics (16)** — `acupuncture`, `chiropractor`, `cosmetic_dentist`, `counseling`, `dentist`, `dermatologist`, `emergency_dentist`, `hearing_aids`, `massage_therapy`, `med_spa`, `optometrist`, `orthodontist`, `physical_therapy`, `podiatrist`, `urgent_care`, `veterinarian`

**Legal & professional (15)** — `accountant`, `bankruptcy_attorney`, `bookkeeping`, `criminal_defense_lawyer`, `divorce_lawyer`, `estate_planning_attorney`, `immigration_lawyer`, `insurance_agency`, `mortgage_broker`, `personal_injury_lawyer`, `photographer`, `property_management`, `real_estate_agent`, `tax_preparation`, `web_design`

**Beauty (5)** — `barber_shop`, `hair_salon`, `lash_extensions`, `nail_salon`, `tattoo_studio`

**Care, cleaning & pets (23)** — `biohazard_cleanup`, `deep_cleaning`, `dog_grooming`, `dog_training`, `estate_cleanout`, `furniture_assembly`, `hoarder_cleanup`, `home_organizing`, `house_cleaning`, `long_distance_moving`, `maid_service`, `mattress_cleaning`, `move_out_cleaning`, `odor_removal`, `personal_trainer`, `pet_sitting`, `piano_moving`, `post_construction_cleaning`, `rug_cleaning`, `senior_home_care`, `tile_grout_cleaning`, `tv_mounting`, `upholstery_cleaning`

## Address formats

All of these work: `Fresno`, `Fresno, CA`, `Fresno CA 93721`, `Street 1, Fresno`, `12 Main St Tampa FL`, `Denver, Colorado`, `143 Shawcliffe Cir SW, Calgary, AB T2Y 1J5`. The street is never used in the H1 — the city is matched against the 27,000-city database, and the state is looked up when it's missing.
