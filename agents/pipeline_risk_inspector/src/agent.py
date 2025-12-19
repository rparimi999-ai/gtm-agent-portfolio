from __future__ import annotations

from typing import Any, Dict, List


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    opp = payload.get("opportunity", {}) or {}
    stage = (opp.get("stage") or "").lower()
    amount = float(opp.get("amount") or 0)
    age_days = int(opp.get("age_days") or 0)
    security = bool(opp.get("security_review"))
    champion = bool(opp.get("champion_confirmed"))
    budget = (opp.get("budget_status") or "").lower()

    risk_score = 35
    explanation: List[str] = []
    evidence: List[str] = []
    flags: List[str] = []

    if stage in {"discovery", "scoping"} and age_days > 45:
        risk_score += 20
        explanation.append("early stage deal aging")
        evidence.append(f"stage={stage}, age_days={age_days}")

    if amount >= 500_000 and not champion:
        risk_score += 15
        explanation.append("large deal without confirmed champion")
        evidence.append(f"amount={amount}")

    if security:
        risk_score += 10
        explanation.append("security review pending")
        evidence.append("security review required")

    if budget != "approved":
        risk_score += 10
        explanation.append("budget not fully approved")
        evidence.append(f"budget_status={budget}")

    if not explanation:
        explanation.append("no material risk indicators detected")
        evidence.append("all primary risk checks passed")

    risk_score = max(0, min(100, risk_score))

    return {
        "risk_score": risk_score,
        "explanation": explanation,
        "evidence": evidence,
        "flags": flags,
        "summary": "Pipeline risk assessed using stage, age, budget, and execution signals.",
        "confidence": 0.82,
    }
