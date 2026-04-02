"""
Seed search_keywords from two sources:
  1. All keywords in the capabilities table (both profiles)
  2. Research Area Keywords column in ssi_sbir_history.csv

Run:
    python -m backend.scraper.seed_keywords [--csv PATH]

Safe to re-run; uses INSERT OR IGNORE so existing rows are never overwritten.
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.database import init_db
from backend.db.crud import get_all_capabilities, get_all_keywords, upsert_keyword

# ---------------------------------------------------------------------------
# Internal program / tool names that are not useful as Grants.gov search terms
# ---------------------------------------------------------------------------
_BLOCKLIST = {
    "samm", "samm2", "flites", "osf", "osic", "mcscene", "modtran", "socrates",
    "aristotle", "leedr", "afwa", "ptss", "sbirs", "opir", "sag", "raes", "quid",
    "jsis", "obac", "ssgm", "morph", "fead", "hwil", "aces-hy", "us3d",
    "faspec", "tracer", "flaash", "quac", "ebs", "nitfs", "dsmc", "brdf",
    "mrtd", "mtf", "ndi", "ndt", "tps", "dems", "dsm", "dem", "cho", "bmi",
    "stat", "frames", "checkpoint", "restart", "playback",
    # overly generic single words that return noise on any grants portal
    "model", "models", "sensor", "sensors", "data", "system", "systems",
    "software", "tools", "database", "method", "methods", "approach",
    "analysis", "performance", "design", "development", "research", "testing",
    "application", "simulation", "simulations", "algorithm", "algorithms",
    "technique", "techniques", "processing", "advanced", "novel", "new",
    "enhanced", "improved", "robust", "efficient", "accurate", "high",
}

# Regex to strip parenthetical suffixes like "(cfd)" or "(see also ...)"
_PARENS_RE = re.compile(r"\s*\(.*?\)\s*$")
# Strip trailing punctuation / whitespace artifacts
_CLEAN_RE = re.compile(r"[;,?.'\u2019\u2018]+$")


def _normalize(raw: str) -> str | None:
    """Return a cleaned keyword string, or None if it should be dropped."""
    kw = raw.strip().lower()
    kw = _PARENS_RE.sub("", kw)
    kw = _CLEAN_RE.sub("", kw).strip()

    # Drop if too short or in blocklist
    if len(kw) < 4:
        return None
    if kw in _BLOCKLIST:
        return None
    # Drop sentence fragments that start with conjunctions / conditionals
    if re.match(r"^(and|or|if|the|for|with|from|this|that)\b", kw):
        return None
    # Drop if it looks like a sentence fragment (>6 words)
    if len(kw.split()) > 6:
        return None
    # Drop if any token is a blocklisted program name (catches "backgrounds samm")
    if any(tok in _BLOCKLIST for tok in kw.split()):
        return None
    # Drop if it's a pure number or version string
    if re.fullmatch(r"[\d\.\-]+", kw):
        return None
    return kw


def _from_capabilities() -> list[str]:
    caps = get_all_capabilities()
    terms = []
    for cap in caps:
        try:
            kws = json.loads(cap.get("keywords_json") or "[]")
        except (ValueError, TypeError):
            kws = []
        terms.extend(kws)
    return terms


def _from_csv(csv_path: str) -> list[str]:
    terms = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw = row.get("Research Area Keywords", "")
            for part in raw.split(","):
                terms.append(part.strip())
    return terms


def seed(csv_path: str | None = None) -> None:
    init_db()

    if csv_path is None:
        # Default: look alongside project root
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "ssi_sbir_history.csv",
        )

    cap_terms = _from_capabilities()
    csv_terms = _from_csv(csv_path) if os.path.exists(csv_path) else []

    cap_added = csv_added = skipped = 0

    for raw in cap_terms:
        kw = _normalize(raw)
        if kw:
            before = len(get_all_keywords())
            upsert_keyword(kw, source="capability")
            if len(get_all_keywords()) > before:
                cap_added += 1
            else:
                skipped += 1
        else:
            skipped += 1

    for raw in csv_terms:
        kw = _normalize(raw)
        if kw:
            before = len(get_all_keywords())
            upsert_keyword(kw, source="csv")
            if len(get_all_keywords()) > before:
                csv_added += 1
            else:
                skipped += 1
        else:
            skipped += 1

    total = len(get_all_keywords())
    print(f"Keywords added from capabilities : {cap_added}")
    print(f"Keywords added from CSV          : {csv_added}")
    print(f"Dropped / already existed        : {skipped}")
    print(f"Total active keywords in DB      : {total}")


if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    seed(csv_arg)
