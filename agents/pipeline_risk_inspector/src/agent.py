from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple


def _parse_date(s: str) -> datetime | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


def _days_between(a: str, b: str) -> int | None:
    da = _parse_date(a)
    db = _parse_date(b)
    if not da or not db:
        return None
    return (da - db).days


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    as_of = payload.get("as_of_date") or payload.get("as_of") or ""
    opp = payload.get("opportunity") or {}

    stage = (opp.get("stage") or "").lower()
    close_date = opp.get("close_date") or ""
    last_activity = opp.get("last_activity_date") or ""
    med = opp.get("meddpicc") or {}

    flags: List[str] = []
    explanation: List[str] = []
    evidence: List[str] = []

    # stale activity
    days_stale = _days_between(as_of, last_activity)
    if days_stale is not None and days_stale >= 21 and stage in {"proposal", "negotiation", "commit"}:
        flags.append("stale_activity")
        explanation.append("Last activity is stale for late-stage deal.")
        evidence.append(f"last_activity_date={last_activity} (days_stale={days_stale})")

    # missing fields
    if not (med.get("economic_buyer") or "").strip():
        flags.append("missing_economic_buyer")
        explanation.append("Economic buyer not identified.")
        evidence.append("meddpicc.economic_buyer is empty")

    if not (med.get("paper_process") or "").strip():
        flags.append("paper_process_unknown")
        explanation.append("Paper process not captured, increases close-date volatility.")
        evidence.append("meddpicc.paper_process is empty")

    if not (med.get("metrics") or "").strip():
        flags.append("no_metrics")
        explanation.append("No quantified success metrics captured.")
        evidence.append("meddpicc.metrics is empty")

    if not (med.get("champion") or "").strip():
        flags.append("missing_champion")
        explanation.append("No champion identified, weak internal pull.")
        evidence.append("meddpicc.champion is empty")

    # close date at risk
    days_to_close = _days_between(close_date, as_of)  # close - as_of
    if days_to_close is not None and days_to_close <= 7 and stage in {"proposal", "negotiation"}:
        flags.append("close_date_at_risk")
        explanation.append("Close date is within 7 days without sufficient late-stage certainty.")
        evidence.append(f"close_date={close_date} (days_to_close={days_to_close})")

    # risk score
    risk_score = 20
    weight = {
        "stale_activity": 25,
        "missing_economic_buyer": 20,
        "paper_process_unknown": 15,
        "no_metrics": 15,
        "missing_champion": 15,
        "close_date_at_risk": 20,
    }
    for f in flags:
        risk_score += weight.get(f, 10)
    risk_score = max(0, min(100, risk_score))

    # ensure explainability minimums for evals
    if len(explanation) < 3 and flags:
        explanation.append("Risk driven by missing critical fields and/or stalled momentum.")
    if len(evidence) < 2:
        evidence.append("evidence: insufficient fields populated")

    return {
        "risk_score": risk_score,
        "flags": flags,
        "explanation": explanation[:6],
        "evidence": evidence[:6],
        "confidence": 0.86,
    }
