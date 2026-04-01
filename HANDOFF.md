# HANDOFF

**Last updated:** 2026-04-01 (Sprint complete - all 5 days done)

---

## Current State

MVP is complete and fully functional. Backend + frontend end-to-end demo works.

- 98 solicitations scraped and scored
- 3 capabilities seeded (Remote Sensing, 3D Point Clouds, Edge Computing)
- 2 projects created with Technical Volume drafts (16-17k chars each)
- React frontend: 3 views, fully wired to backend

---

## How to Run

### Backend
```bash
cd /home/cgarms/Projects/proposal_pilot
source backend/.venv/bin/activate
uvicorn backend.main:app --reload
# http://localhost:8000/docs  <- interactive API docs
```

### Frontend
```bash
export PATH="$HOME/.fnm:$PATH" && eval "$(fnm env)"
cd frontend && npm run dev
# http://localhost:5173
```

### Seed + scrape fresh data
```bash
python -m backend.capabilities.seed_capabilities          # only needed once
python backend/scraper/run_scrape.py --max-pages 10 --max-detail 100
python -c "from backend.capabilities.aligner import run_alignment; run_alignment()"
```

---

## Good Demo Solicitations

| ID | Title | Top Score | Capability |
|----|-------|-----------|------------|
| 81 | Cognitive Mapping for Counter-WMD (DTRA254-002) | 0.850 | 3D Point Clouds |
| 103 | Shop Floor Human Detection (AF254-D0823) | 0.850 | 3D Point Clouds |
| 50 | Real-Time Detection and Tracking | 0.700 | Edge Computing |
| 79 | PEO SOF Visual Augmentation Systems | 0.700 | Edge Computing |

---

## Next Sprint Ideas (Post-MVP)

### Solicitation Timing and Date Awareness
- **Parse and store open_date + close_date as ISO dates** in the `solicitations` table (currently stored as free-text strings from the scraper). Normalize on ingest so they can be sorted and filtered numerically.
- **Time-remaining sort columns** in the solicitation list: days until open, days until close. Filter out expired topics by default (close_date < today), with an option to include them.
- **TPOC contact window indicator**: open_date is the cutoff for direct contact with the Technical Point of Contact. Flag solicitations where open_date is approaching (e.g., within 7 days) as a distinct status — this is a high-priority action window for the user.
- **Status normalization**: derive a computed status field (upcoming / open / closing-soon / closed) from open_date and close_date relative to current date, rather than relying on the scraped "Closed"/"Open" badge which may lag.

### Expanded Capability Categories + Multi-User Customization
- **Add 6 new capabilities** aligned with forestry, agriculture, and imaging domains:
  - Forestry and Invasive Species Management (keywords: forest inventory, invasive species, canopy mapping, tree detection, biomass, phenology, species classification)
  - Precision Agriculture (keywords: crop monitoring, yield prediction, soil moisture, NDVI, variable rate application, drone scouting, field mapping)
  - Novel Camera and Sensor Systems (keywords: focal plane array, CMOS, event camera, neuromorphic sensor, low-SWaP camera, sensor fusion, optical design)
  - Hyperspectral and Hypertemporal Imaging (keywords: hyperspectral, hypertemporal, spectral unmixing, time-series imagery, phenological change, VNIR, SWIR, continuous monitoring)
  - GIS Software Development (keywords: GIS, geospatial, spatial analysis, vector data, raster processing, QGIS, ArcGIS, geodatabase, OGC standards, web mapping)
  - 3D Point Clouds (already exists - extend keyword list with forestry/ag terms: canopy height model, CHM, tree segmentation, crop structure)
- **Multi-tenant capability profiles**: allow named profiles (e.g., "Remote Sensing Lab", "AgTech Partner") each with their own capability set. `capabilities` table needs a `profile_id` FK. UI lets users switch profiles or create new ones without affecting others.
- **Capability import/export**: JSON export of a capability profile so colleagues can share or fork a configuration.

### Agency Release Calendar Dashboard
- **Research and hardcode annual release schedules** for major SBIR agencies (DoD topics typically release in batches: BAA releases ~Oct, ~Jan, ~Apr; USDA ~Feb; NASA ~Oct; NSF ~rolling). Store in a `agency_release_schedule` table: `(agency, solicitation_cycle, expected_release_month, expected_open_month, notes)`.
- **New frontend page `/dashboard`**: agency release calendar view showing:
  - Newly released (open_date within last 14 days)
  - Open now (between open_date and close_date)
  - Closing soon (close_date within 30 days)
  - Coming soon (expected_release_month approaching based on calendar)
  - Recently closed (close_date within last 60 days - still worth tracking for next cycle)
- **NavBar link** to Dashboard alongside Solicitations.
- This page is the highest-value addition for planning — it answers "what should I be working on right now?"

### Other Carry-Forward Ideas
- **More agencies**: USDA, NASA, NSF solicitation scrapers
- **Alignment re-run on demand**: per-solicitation re-score button in UI
- **Draft editing**: inline editing of generated sections, save revisions
- **Export**: PDF or DOCX export of full Technical Volume
- **Agency filter**: filter solicitation list by agency in UI
- **SOTA validation**: auto-pull related papers from arXiv/Semantic Scholar to ground technical claims

---

## Full API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /solicitations?limit=N&offset=N&agency=X | List solicitations |
| GET | /solicitations/{id} | Single solicitation |
| POST | /solicitations/scrape | Trigger background scrape |
| GET | /solicitations/scrape/status | Scrape job status |
| GET | /solicitations/{id}/alignment | Alignment scores |
| GET | /capabilities | List capabilities |
| POST | /capabilities | Add capability |
| POST | /align/run | Trigger alignment pass |
| GET | /align/status | Alignment job status |
| POST | /projects | Create project |
| GET | /projects/{id} | Get project + scores |
| POST | /projects/{id}/generate | Generate draft section |
| GET | /projects/{id}/drafts | List drafts |

## Schema

```
solicitations(id, agency, title, topic_number, description, deadline, url UNIQUE, raw_html, scraped_at)
capabilities(id, name UNIQUE, description, keywords_json)
projects(id, solicitation_id FK, title, status, created_at)
drafts(id, project_id FK, section_type, content, model_version, generated_at)
solicitation_capability_scores(solicitation_id FK, capability_id FK, score, rationale, scored_at)
```
