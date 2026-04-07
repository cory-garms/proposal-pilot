from fastapi import APIRouter
from backend.db.crud import get_all_solicitations
from backend.database import get_connection
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

PROFILE_CORY = 1
PROFILE_SSI = 2
MIN_SCORE = 0.40       # only show solicitations where at least one profile scores >= this
MAX_PER_SECTION = 12   # cap cards per dashboard section


def get_agency_schedules():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM agency_release_schedule").fetchall()
    return [dict(r) for r in rows]


def _bulk_top_scores(profile_id: int, n: int = 3) -> dict:
    """Return {solicitation_id: [top-n score dicts]} for all solicitations, one profile."""
    sql = """
        SELECT sc.solicitation_id, sc.score, c.name AS capability
        FROM solicitation_capability_scores sc
        JOIN capabilities c ON c.id = sc.capability_id
        WHERE c.profile_id = ?
        ORDER BY sc.solicitation_id, sc.score DESC
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (profile_id,)).fetchall()

    result: dict = {}
    for row in rows:
        r = dict(row)
        sid = r["solicitation_id"]
        if sid not in result:
            result[sid] = []
        if len(result[sid]) < n:
            result[sid].append({"score": r["score"], "capability": r["capability"]})
    return result


def _score_color(score: float | None) -> str:
    if score is None or score == 0:
        return "gray"
    if score >= 0.7:
        return "green"
    if score >= 0.4:
        return "yellow"
    return "gray"


@router.get("")
def get_dashboard_summary():
    solicitations = get_all_solicitations(
        limit=1000,
        exclude_expired=False,
        profile_id=str(PROFILE_CORY),
    )

    # Two bulk queries instead of 2×N per-row queries
    cory_map = _bulk_top_scores(PROFILE_CORY)
    ssi_map = _bulk_top_scores(PROFILE_SSI)

    today = datetime.now()
    two_weeks_ago = (today - timedelta(days=14)).strftime("%Y-%m-%d")
    sixty_days_ago = (today - timedelta(days=60)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    thirty_days_from_now = (today + timedelta(days=30)).strftime("%Y-%m-%d")

    newly_released = []
    tpoc_window = []
    open_now = []
    closing_soon = []
    recently_closed = []

    for sol in solicitations:
        c_date = sol.get("close_date") or sol.get("deadline")
        o_date = sol.get("open_date") or sol.get("release_date")
        r_date = sol.get("release_date")

        if c_date and c_date < sixty_days_ago:
            continue

        cory_scores = cory_map.get(sol["id"], [])
        ssi_scores = ssi_map.get(sol["id"], [])
        cory_best = max((s["score"] for s in cory_scores), default=0)
        ssi_best = max((s["score"] for s in ssi_scores), default=0)
        best = max(cory_best, ssi_best)

        if best < MIN_SCORE:
            continue

        sol["cory_scores"] = [s for s in cory_scores if s["score"] > 0]
        sol["ssi_scores"] = [s for s in ssi_scores if s["score"] > 0]
        sol["cory_top"] = cory_best
        sol["ssi_top"] = ssi_best
        sol["score_color"] = _score_color(best)

        is_closed = bool(c_date and c_date < today_str)
        is_open = not is_closed and (not o_date or o_date <= today_str)
        in_tpoc = bool(
            not is_closed and not is_open
            and r_date and r_date <= today_str
            and o_date and o_date > today_str
        )

        if is_closed and c_date >= sixty_days_ago:
            recently_closed.append(sol)

        if not is_closed:
            if o_date and two_weeks_ago <= o_date <= today_str:
                newly_released.append(sol)
            if in_tpoc:
                tpoc_window.append(sol)
            if is_open:
                open_now.append(sol)
            if c_date and c_date <= thirty_days_from_now:
                closing_soon.append(sol)

    def by_score(lst):
        scored = sorted(lst, key=lambda s: max(s.get("cory_top", 0), s.get("ssi_top", 0)), reverse=True)
        return scored[:MAX_PER_SECTION]

    schedules = get_agency_schedules()

    return {
        "tpoc_window": by_score(tpoc_window),
        "newly_released": by_score(newly_released),
        "open_now": by_score(open_now),
        "closing_soon": by_score(closing_soon),
        "recently_closed": by_score(recently_closed),
        "coming_soon": schedules,
    }
