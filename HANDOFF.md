# HANDOFF

**Last updated:** 2026-04-02 (Added Spectral Sciences capabilities + Planned Grants.gov/SAM.gov scrapers — Gemini)

---

## What Was Built This Session (Gemini)

- **Spectral Sciences Profile**: Updated `backend/capabilities/seed_capabilities.py` to seed two profiles: "Cory Garms" and "Spectral Sciences".
- The "Spectral Sciences" profile includes 5 custom capabilities derived from analyzing `ssi_sbir_history.csv`: Hypersonics and Aerothermodynamics, Physics-Informed AI/ML, Synthetic Data and Scene Generation (M&S), Counter-UAS and Advanced Threat Tracking, and Atmospheric Modeling and Space Weather.
- These profiles are immediately available in the frontend `NavBar.jsx` drop-down for dynamic context switching during draft generation.

## Current Plan / Unfinished Business

- We drafted an `implementation_plan.md` to build out non-SBIR/STTR scrapers (Grants.gov and SAM.gov) to capture BAAs, OTAs, and conventional grants.
- **Pending Questions for Claude/User**:
  - Should we obtain a SAM.gov API key or rely on parsing their daily bulk CSV extracts?
  - Should we update the `solicitations` schema to include a `vehicle_type` column (to distinguish SBIR vs BAA vs OTA)?
  - Should Grants.gov scraping be filtered by a specific list of technical keywords to avoid ingesting irrelevant grants?

---

## Current State

The app is fully functional end-to-end. All Sprint 3 features are shipped and the
database contains real, scored solicitations ready for a demo.

### DB Snapshot
- **174 solicitations** total (24 active DOD 2025.4 cycle, rest historical)
- **30 scored** with live alignment (24 current + 6 historical)
- **11 capabilities** in Default Profile (1 profile)
- **3 projects / 3 drafts** from test runs

### Top alignment scores (live, API-verified)
| Score | Topic | Capability |
|-------|-------|------------|
| 0.85 | HR0011SB20254-15 — Unbiased Behavioral Discovery | Computer Vision |
| 0.70 | SF254-D1207 — Affordable IR Sensors for pLEO | On-Orbit Sensors |
| 0.70 | SF25D-T1201 — Adaptive and Intelligent Space (AIS) | Edge Computing |
| 0.70 | SOCOM254-007 — AURORA (UAS acoustic) | UAV/UAS and Drones |

**Best demo topic: SF254-D1207** — Space Force, IR sensors for pLEO constellation,
0.70 on On-Orbit Sensors. Clear technical narrative, strong Phase I feasibility angle.

---

## What Was Built This Sprint

### Sprint 3 features (commit `62ed3e5`)
- **SOTA Validation** — `backend/rag/sota.py` queries arXiv at draft-gen time;
  injects `=== RELEVANT PRIOR ART ===` block; prompts require citations by author/year
- **Inline Draft Editing** — `PATCH /projects/{id}/drafts/{draft_id}`; Edit/Save/Cancel
  in DraftEditor toolbar; saves to DB, updates state in place
- **PDF/DOCX Export** — `backend/export/docx_writer.py` + `pdf_writer.py`;
  two GET export routes; PDF and DOCX download links in toolbar (read mode only)
- **Draft Settings** — `tone` (technical / executive / persuasive) and `focus_area`
  (balanced / innovation / feasibility / commercialization) dropdowns;
  appended as modifier block to user prompt; zero overhead at defaults
- **DOD Scraper rewrite** — dropped Playwright, pure `urllib` against public JSON API;
  pagination fixed: was fetching 10 (page 0 only), now fetches all 24

### DOD detail fix (commit `f4c6395`)
- Discovered `/topics/api/public/topics/{topicId}/details` endpoint (unauthenticated)
  returns `description`, `objective`, `phase1Description`, `keywords`, `technologyAreas`
- Rewrote `dod_scraper.py` to call `/details` for every topic after the search pass
- Topic descriptions went from 59 chars (title only) to 3–6k chars of real content
- All 24 current topics re-upserted with full descriptions; alignment re-run; scores live

---

## How to Run

### Backend
```bash
cd /home/cgarms/Projects/proposal_pilot
source backend/.venv/bin/activate
uvicorn backend.main:app --reload
# http://localhost:8000/docs
```

### Frontend
```bash
export PATH="$HOME/.fnm:$PATH" && eval "$(fnm env)"
cd frontend && npm run dev
# http://localhost:5173
```

### Refresh data (next cycle / new scrape)
```bash
source backend/.venv/bin/activate
python backend/scraper/run_scrape.py --max-pages 5 --max-detail 50
python -c "from backend.capabilities.aligner import run_alignment; run_alignment()"
```

---

## Demo Script

1. **Dashboard** (`/`) — 24 active DOD topics in "Open Now", closing 2026-05-13
2. **Solicitations** (`/solicitations`) — filter DOD, sort by alignment descending
3. Open **SF254-D1207** (IR Sensors for pLEO, score 0.70) — show capability cards
4. Click **Re-run Alignment** to demonstrate live rescoring
5. Click **Create Project**
6. In **Draft Editor**: set Tone=Persuasive, Focus=Innovation → **Generate**
7. Show arXiv citations in the Background/Innovation sections of the draft
8. Click **Edit** → make a change → **Save**
9. Click **PDF** or **DOCX** — file downloads immediately

---

## Full API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /solicitations | List (filter, sort, paginate) |
| GET | /solicitations/{id} | Single solicitation |
| POST | /solicitations/scrape | Trigger background scrape |
| GET | /solicitations/scrape/status | Scrape job status |
| GET | /dashboard | Lifecycle buckets + agency calendar |
| GET | /profiles | List profiles |
| POST | /profiles | Create profile |
| GET | /capabilities?profile_id=X | List capabilities |
| POST | /capabilities | Add capability |
| POST | /align/run | Global alignment pass |
| GET | /align/status | Alignment job status |
| GET | /solicitations/{id}/alignment | Scores for a solicitation |
| POST | /solicitations/{id}/align | Re-run alignment |
| POST | /projects | Create project |
| GET | /projects/{id} | Get project + scores |
| POST | /projects/{id}/generate | Generate draft (tone, focus_area) |
| GET | /projects/{id}/drafts | List drafts |
| PATCH | /projects/{id}/drafts/{draft_id} | Update draft content |
| GET | /projects/{id}/drafts/{draft_id}/export/pdf | Download PDF |
| GET | /projects/{id}/drafts/{draft_id}/export/docx | Download DOCX |

---

## Recommended Next Steps

Ordered by value-to-effort ratio. Items 1–3 are the most impactful for the core loop.

### 1. Score historical solicitations (high value, low effort)
`run_alignment()` only scores non-expired solicitations. 144 historical records have no
scores, including many domain-relevant topics (Lidar Tomography, UAS ISR, Remote Sensing
Satellite, etc.) from prior cycles. These are the best demo candidates for draft generation.

Fix: add `exclude_expired=False` option to the aligner, or run a one-time backfill:
```python
from backend.capabilities.aligner import run_alignment, score_solicitation
# then call with solicitation_ids=[395, 410, 413, ...] 
```
Or change `get_all_solicitations(limit=10000)` in `aligner.py` to pass
`exclude_expired=False`.

### 2. Solicitation Watch List / Bookmarks (high value, medium effort)
Users need to track specific topics without creating a full project. Add a `watched`
boolean column to `solicitations` or a separate `watches` table (solicitation_id, notes,
added_at). Surface as a "Saved" tab on the Solicitations list and a star/bookmark icon
on each card. This mirrors how real proposal managers work — they track 10–20 topics
and decide which 2–3 to pursue.

### 3. Expanded scrapers — USDA, NASA (medium value, medium effort)
The DOD scraper approach (find the hidden JSON API, call it directly) should work for
other agencies. NASA SBIR uses `sbir.nasa.gov`; USDA uses `nifa.usda.gov`. These are
high-priority for the user's domain (forestry, precision ag, remote sensing for
agriculture). Pattern from `dod_scraper.py` is reusable.

### 4. DOD topic detail enrichment on re-scrape (low effort, already architected)
The `run_scrape.py` → `run_sync()` path already calls `/details` for every topic.
But the SBIR.gov scraper path still uses title-only for DOD topics that appear there.
Consider deduplicating: after scraping SBIR.gov, if `agency=DOD` and the topic
already has a description from the DOD scraper, don't overwrite it.

### 5. User authentication (medium effort, needed before multi-user)
Currently single-user, no auth. JWT + FastAPI is straightforward. Profiles are already
multi-tenant in the schema — just need a `users` table and FK on `profiles`. Needed
before sharing the app with a second person.

### 6. Draft revision history UI (low effort)
Backend already stores all drafts with timestamps. The sidebar Draft History list is
present but minimal. Add section_type badge, char count, and a diff view between
revisions (simple line-by-line diff using Python's `difflib`, rendered in the UI).

### 7. SOTA caching (low effort, cost reduction)
`sota.py` calls arXiv on every draft generation for the same solicitation. Add a
`sota_cache` table (solicitation_id, query, papers_json, fetched_at) with a 7-day TTL.
Eliminates redundant fetches and makes draft gen faster.
