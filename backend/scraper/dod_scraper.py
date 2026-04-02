"""
DOD SBIR/STTR scraper — hits the dodsbirsttr.mil public JSON API directly.
No Playwright required. Both endpoints are unauthenticated.

Two-step fetch per topic:
  1. /topics/api/public/topics/search  -> list of all active topics (metadata + topicId)
  2. /topics/api/public/topics/{topicId}/details -> full description, objective, keywords
"""
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime

BASE = "https://www.dodsbirsttr.mil"
SEARCH_URL = f"{BASE}/topics/api/public/topics/search"
DETAIL_URL = f"{BASE}/topics/api/public/topics/{{topicId}}/details"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

SEARCH_PARAM = {
    "searchText": None,
    "components": None,
    "programYear": None,
    "solicitationCycleNames": ["openTopics"],
    "releaseNumbers": [],
    "topicReleaseStatus": [591, 592],
    "modernizationPriorities": None,
    "sortBy": "finalTopicCode,asc",
}


def _ts_to_iso(ts) -> str | None:
    if not ts:
        return None
    return datetime.fromtimestamp(ts / 1000.0).strftime("%Y-%m-%d")


def _strip_html(html: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def _fetch_json(url: str) -> dict | list:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _fetch_detail(topic_id: str) -> dict:
    """
    Fetch full topic detail from the /details endpoint.
    Returns a dict with cleaned text fields; never raises.
    """
    try:
        data = _fetch_json(DETAIL_URL.format(topicId=topic_id))
        description = _strip_html(data.get("description", ""))
        objective = _strip_html(data.get("objective", ""))
        phase1 = _strip_html(data.get("phase1Description", ""))

        # Build a rich description block from the available sections
        parts = []
        if objective:
            parts.append(f"OBJECTIVE: {objective}")
        if description:
            parts.append(f"DESCRIPTION: {description}")
        if phase1:
            parts.append(f"PHASE I: {phase1}")

        keywords = data.get("keywords") or ""
        tech_areas = ", ".join(data.get("technologyAreas") or [])

        return {
            "description": "\n\n".join(parts),
            "keywords_extra": keywords,
            "tech_areas": tech_areas,
        }
    except Exception as e:
        print(f"[dod_scraper] detail fetch failed for {topic_id}: {e}")
        return {"description": "", "keywords_extra": "", "tech_areas": ""}


def _fetch_search_page(page: int, size: int) -> dict:
    params = urllib.parse.urlencode({
        "searchParam": json.dumps(SEARCH_PARAM),
        "size": size,
        "page": page,
    })
    return _fetch_json(f"{SEARCH_URL}?{params}")


def _build_record(item: dict, detail: dict) -> dict:
    c_date = _ts_to_iso(item.get("topicEndDate"))
    title = item.get("topicTitle", "")
    topic_id = item.get("topicId", "")
    description = detail["description"] or title  # fall back to title if detail failed

    return {
        "agency": "DOD",
        "title": title,
        "topic_number": item.get("topicCode", ""),
        "description": description,
        "deadline": c_date,
        "open_date": _ts_to_iso(item.get("topicStartDate")),
        "close_date": c_date,
        "release_date": _ts_to_iso(item.get("topicPreReleaseStartDate")),
        "url": f"{BASE}/topics-app/?topicId={topic_id}",
        "raw_html": "",
    }


async def run(max_pages: int = 1, enrich: bool = False, max_detail: int = 50) -> list[dict]:
    """Async-compatible wrapper — the implementation is synchronous urllib."""
    return run_sync()


def run_sync() -> list[dict]:
    print("[dod_scraper] Fetching DOD topics from dodsbirsttr.mil API...")
    items_all = []
    page, page_size = 0, 100

    while True:
        try:
            data = _fetch_search_page(page, page_size)
        except Exception as e:
            print(f"[dod_scraper] search API error on page {page}: {e}")
            break

        items = data.get("data") or []
        total = data.get("total", 0)
        items_all.extend(items)
        print(f"[dod_scraper] Search page {page}: {len(items)} topics (total: {total})")

        if len(items_all) >= total or not items:
            break
        page += 1

    print(f"[dod_scraper] Fetching full descriptions for {len(items_all)} topics...")
    results = []
    for i, item in enumerate(items_all):
        topic_id = item.get("topicId", "")
        detail = _fetch_detail(topic_id)
        results.append(_build_record(item, detail))
        if (i + 1) % 5 == 0 or (i + 1) == len(items_all):
            print(f"[dod_scraper] Detail fetch progress: {i + 1}/{len(items_all)}")

    print(f"[dod_scraper] Successfully extracted {len(results)} DOD topics with full descriptions.")
    return results


if __name__ == "__main__":
    topics = run_sync()
    for t in topics:
        print(f"\n{t['topic_number']} | {t['title']}")
        print(f"  {t['description'][:200]}")
