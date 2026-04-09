# HANDOFF

**Last updated:** 2026-04-09 (Sprint 9 complete — Claude)

---

## Immediate Next Steps (Start Here)

**Sprint 9 is complete. The app is live.**

- Frontend: `https://cory-garms.github.io/proposal-pilot/`
- Backend: Render `proposalpilot-api` (Oregon, Starter plan)
- DB: uploaded from local (824 solicitations, 5 profiles, 4 users)
- Beta user credentials in DB: `Welcome!2026` temp password for rpanfili, dstelter, rtaylor

**Sprint 10 goal: beta tester handoff by end of day 5.**

### Sprint 10 Plan

**Day 1 — Smoke test the live app**
- Login as cgarms, verify dashboard, solicitation list, capabilities, alignment
- Login as each beta persona (use incognito) — confirm they see only their own profile + Spectral Sciences shared profile
- Verify score button works, generate a draft end-to-end, export PDF/DOCX
- Check Render logs for any errors during normal use

**Day 2 — Fix bugs found in smoke test**
- Triage anything broken; fix before inviting beta users

**Day 3 — Scrape fresh solicitations on Render**
- Trigger SAM scrape from Admin page (live Render backend, real API)
- Run alignment for Spectral Sciences shared profile
- Verify nightly scheduler is showing a next-run time in Admin

**Day 4 — Beta onboarding prep**
- Write the beta invite email (URL, temp password, 3-step quick-start)
- Consider a one-page `BETA_GUIDE.md` or in-app tooltip if onboarding looks rough

**Day 5 — Send invites, monitor**
- Email rpanfili@spectral.com, dstelter@spectral.com, rtaylor@spectral.com
- Monitor Render logs for 401s, errors, slow queries
- Be available to reset passwords if needed (`python -m backend.scraper.reset_beta_users` locally then re-upload, or use Render Shell to run it directly)

### Known Issues to Address in Sprint 10
- **Capability auto-score on edit** — `PATCH /capabilities/{id}` triggers background alignment but not verified end-to-end on production
- **SAM CSV import** — `POST /solicitations/import/sam-csv` exists but untested; don't expose in beta
- **Password reset flow** — no self-service; admin must use `reset_beta_users.py` or Render Shell

### Render Operations Reference
```bash
# SSH into Render (add your public key in Render Account Settings → SSH Keys first)
ssh srv-d7buv6fkijhs73b1mkfg@ssh.oregon.render.com

# Upload a new DB from WSL
sqlite3 proposalpilot.db "PRAGMA wal_checkpoint(FULL);"
scp -i ~/.ssh/id_rsa_personal proposalpilot.db \
    srv-d7buv6fkijhs73b1mkfg@ssh.oregon.render.com:/data/proposalpilot.db
# Then restart service in Render dashboard

# Reset beta users via Render Shell tab
python -m backend.scraper.reset_beta_users
```

---

## What Was Built This Session (Sprint 8)

### Bug Fixes
- **Capability delete** — was failing silently due to FK constraint on `solicitation_capability_scores`. Fixed: delete scores first, then capability.
- **Admin profile dropdown** — only showed admin's own + shared profiles. Fixed: `get_all_profiles(include_all=True)` for admin users.
- **Score button on shared profile** — 403 at backend. Fixed: button disabled when selected profile has `shared=1`.
- **Trailing "0" on profile heading** — `profile.shared` is SQLite integer `0`; React rendered it as text. Fixed: `!!profile.shared`.

### Capability Generator
- **Broader categories** — prompt now instructs LLM to use wide domain names and include both specific + parent terms in keywords. Fixes low match rate.
- **Google Scholar extractor** — `_extract_google_scholar()` in `extractor.py`: name, interests, publication list.
- **ResearchGate extractor** — `_extract_researchgate()`: scrapes HTML; graceful error when Cloudflare blocks.
- **Auto-routing** — `extract_from_url()` detects hostname and routes to specialized extractor.

### Dev Tooling
- `backend/scraper/reset_beta_users.py` — wipes all non-admin users/profiles/capabilities, recreates the three betas with `Welcome!2026`.

### Infrastructure
- **Content-hash deduplication** — `solicitations.content_hash` (SHA-256 title+description), `solicitation_capability_scores.scored_hash`. `get_scored_pairs()` now invalidates stale pairs on re-scrape. Eliminates redundant LLM calls when solicitation content hasn't changed.
- **CORS** — `CORS_ORIGINS` env var in `config.py`. Defaults to `*` locally; `render.yaml` sets it to `https://cgarms.github.io`.
- **GitHub Actions** — `.github/workflows/deploy-frontend.yml`. Triggers on `frontend/` changes to `main`. Uses `VITE_API_BASE_URL` secret + `VITE_BASE_PATH` variable.
- **SPA routing** — `frontend/public/404.html` + `index.html` inline redirect script. Handles direct-URL access on GitHub Pages without hash routing.
- **Render manifest** — `render.yaml`: web service + 1 GB persistent disk at `/data`. Starter plan ($7/mo) required for disk.

---

## Current State

### Database (local dev — `proposalpilot.db`)
| Table | Count |
|-------|-------|
| solicitations | 824 |
| scored pairs | 324 |
| capabilities | 39 |
| profiles | 5 |
| users | 4 |
| active keywords | 776 |

### Profiles
| ID | Name | Owner | Capabilities |
|----|------|-------|-------------|
| 1 | Cory Garms | cgarms (admin) | 11 |
| 2 | Spectral Sciences | shared (all users) | 10 |
| 3 | Panfili | rpanfili | 6 |
| 4 | David Stelter | dstelter | 6 |
| 5 | Ramona Taylor | rtaylor | 6 |

### Users
| Email | Role |
|-------|------|
| cgarms@spectral.com | admin |
| rpanfili@spectral.com | user |
| dstelter@spectral.com | user |
| rtaylor@spectral.com | user |

---

## How to Run (Local Dev)

```bash
cd proposal-pilot

# Backend
source backend/.ppEnv/bin/activate
uvicorn backend.main:app --reload

# Frontend (separate terminal)
export PATH="$HOME/.fnm:$PATH" && eval "$(fnm env)"
cd frontend && npm run dev

# Open http://localhost:5173
# Login: cgarms@spectral.com
```

### Useful dev commands
```bash
# Reset beta users to never-logged-in state
python -m backend.scraper.reset_beta_users

# Re-seed users if DB is fresh
python -m backend.scraper.seed_users

# Trigger scrape + full alignment
curl -X POST http://localhost:8000/solicitations/scrape/sam \
  -H 'Authorization: Bearer <token>' \
  -d '{"max_results": 100}'

curl -X POST 'http://localhost:8000/align/run?skip_scored=true' \
  -H 'Authorization: Bearer <token>'
```

---

## Architecture Overview

```
frontend/                    React + Vite + TailwindCSS v4
  src/
    views/                   Dashboard, SolicitationList, Capabilities,
                             Keywords, Admin, GenerateCapabilities,
                             ChangePassword, Login, DraftEditor
    components/NavBar.jsx
    api/client.js            Axios instance with JWT interceptors

backend/
  main.py                    FastAPI app, lifespan, CORS, router registration
  config.py                  All env vars (LLM, DB, auth, CORS, scheduler)
  database.py                SQLite connection, WAL mode, additive migrations
  scheduler.py               APScheduler nightly alignment
  llm/                       Provider abstraction (Anthropic, OpenAI-compat)
  routers/
    auth.py                  JWT login/register/me/password-change
    capabilities.py          Profiles, capabilities CRUD, alignment triggers
    dashboard.py             Per-user lifecycle buckets (TPOC, open, closing…)
    solicitations.py         List, detail, watch, scrape triggers
    keywords.py              Keyword CRUD
    generate_capabilities.py URL + file → LLM → capability suggestions
    projects.py              Draft generation
  db/crud.py                 All DB operations
  capabilities/
    aligner.py               Two-pass keyword+LLM scoring
    prompts.py               Alignment prompt templates
  rag/
    extractor.py             ORCID API, Google Scholar, ResearchGate, PDF, DOCX
    capability_generator.py  LLM → structured capability list
    generator.py             Draft generation
    context_builder.py       RAG context assembly
  scraper/
    seed_users.py            Create admin + beta accounts
    reset_beta_users.py      Dev reset — wipe non-admin users
```

---

## Known Issues / Deferred Work

### Sprint 9 backlog
- **Embedding-based pre-filter** — replace keyword threshold with cosine similarity on `text-embedding-3-small` vectors. Cuts LLM scoring calls ~60%. Defer until production traffic data shows whether content-hash fix is sufficient.
- **Render cold-start** — free Render tier spins down after 15 min idle (~30s cold start). Starter plan ($7/mo, already required for disk) stays warm.
- **`bcrypt<4.0.0` pin** — `passlib 1.7.4` breaks with `bcrypt>=4`. Pin is in `requirements.txt`. Don't upgrade bcrypt.
- **SAM CSV import** — `backend/scraper/sam_csv_parser.py` and `POST /solicitations/import/sam-csv` exist but are untested. May need validation before relying on it.
- **Capability auto-score on edit** — `PATCH /capabilities/{id}` now triggers background alignment (added this session). Not yet verified end-to-end.

### API auth table (updated)
Routes that require auth (`require_user` or stricter):

| Method | Path | Auth |
|--------|------|------|
| POST | /auth/password | require_user |
| POST | /profiles | require_user |
| POST | /capabilities | require_user (own profile) |
| PATCH | /capabilities/{id} | require_user (own profile) |
| DELETE | /capabilities/{id} | require_user (own profile) |
| POST | /align/run | require_own_profile_or_admin |
| POST | /solicitations/scrape* | require_admin |
| POST | /solicitations/import/sam-csv | require_admin |
| POST | /capabilities/generate/* | require_user |
| POST | /projects | require_user |
| POST | /projects/{id}/generate | require_user |
| PATCH | /projects/{id}/drafts/{id} | require_user |

---

## File Inventory (changed this sprint)

| File | Change |
|------|--------|
| `backend/database.py` | +2 migrations: `solicitations.content_hash`, `solicitation_capability_scores.scored_hash` |
| `backend/config.py` | +`CORS_ORIGINS` |
| `backend/main.py` | CORS reads from `CORS_ORIGINS` config |
| `backend/db/crud.py` | `_content_hash()`, `get_all_profiles(include_all)`, `delete_capability` cascades scores, `get_scored_pairs` hash-aware, `upsert_score` stores hash, `upsert_solicitation` stores hash |
| `backend/capabilities/aligner.py` | passes `content_hash` to `upsert_score` |
| `backend/rag/extractor.py` | Google Scholar + ResearchGate extractors; `extract_from_url` routes by hostname |
| `backend/rag/capability_generator.py` | Broader keyword/category prompt |
| `backend/routers/capabilities.py` | Admin sees all profiles; `edit_capability` triggers background alignment |
| `frontend/src/views/Capabilities.jsx` | Score button respects `shared`; `!!profile.shared` fix |
| `frontend/index.html` | Title fix; SPA redirect script |
| `frontend/public/404.html` | GitHub Pages 404 redirect |
| `frontend/vite.config.js` | `base` from `VITE_BASE_PATH` |
| `.env.example` | +`CORS_ORIGINS`, +`DB_PATH` production example |
| `.github/workflows/deploy-frontend.yml` | **new** — GitHub Actions deploy |
| `render.yaml` | **new** — Render Blueprint |
| `backend/scraper/reset_beta_users.py` | **new** — dev reset script |
