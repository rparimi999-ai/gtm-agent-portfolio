from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

TARGET_INDUSTRIES = {"manufacturing", "healthcare", "financial services", "retail", "logistics", "software"}
SENIOR_TITLES = {"cio", "cto", "vp", "vice president", "director", "head", "chief"}

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\(\) ]{8,}\d)")


def redact(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text


def _kw_present(s: str, kws: List[str]) -> bool:
    s = (s or "").lower()
    return any(k in s for k in kws)


def _budget_status(budget: str) -> str:
    b = (budget or "").lower()
    # IMPORTANT: check "not approved" before "approved"
    if "not approved" in b or "unapproved" in b:
        return "not_approved"
    if "approved" in b:
        return "approved"
    if "planning" in b or "tbd" in b:
        return "planning"
    return "unknown"


def _timeline_bucket(timeline: str) -> str:
    t = (timeline or "").lower()
    if any(x in t for x in ["60", "90", "120", "q1", "q2", "next month", "this quarter"]):
        return "near"
    if any(x in t for x in ["6-9", "6 to 9", "6 months", "9 months", "2 quarters"]):
        return "mid"
    if any(x in t for x in ["2027", "24 months", "2 years", "18 months", "next year"]):
        return "long"
    return "unknown"


def score_lead(lead: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    industry = (lead.get("industry") or "").lower().strip()
    employees = int(lead.get("employees") or 0)
    region = (lead.get("region") or "").lower()
    title = (lead.get("title") or "").lower()
    use_case = (lead.get("use_case") or "").strip()
    budget_raw = lead.get("budget") or ""
    timeline_raw = lead.get("timeline") or ""
    notes = (lead.get("notes") or "")

    budget = _budget_status(budget_raw)
    timeline = _timeline_bucket(timeline_raw)
    if budget == "approved" and timeline == "near":
        reasons.append("budget and timeline")

    fit = 0
    intent = 0
    reasons: List[str] = []

    # FIT
    if industry in TARGET_INDUSTRIES:
        fit += 15
        reasons.append("ICP fit: fit present")
    else:
        reasons.append("ICP fit: outside ICP")

    if employees >= 2000:
        fit += 20
    elif employees >= 500:
        fit += 15
    elif employees >= 50:
        fit += 10
    else:
        fit += 2

    is_senior = any(t in title for t in SENIOR_TITLES)
    if is_senior:
        fit += 10
        reasons.append("senior buyer")
    else:
        fit += 4

    if region in {"na", "eu"}:
        fit += 5

    # INTENT
    has_migration_intent = _kw_present(use_case, ["migrat", "cloud", "moderniz", "workload"])
    if use_case:
        reasons.append("clear use case: use case present")
    else:
        reasons.append("clear use case: missing use case")

    if has_migration_intent:
        intent += 15
    else:
        reasons.append("no migration intent")

    if _kw_present(use_case + " " + notes, ["security", "infosec", "compliance", "data residency"]):
        reasons.append("security as gating item")

    if budget == "approved":
        intent += 15
    elif budget == "planning":
        intent += 5
        reasons.append("timeline longer or budget not approved")
    elif budget == "not_approved":
        intent += 2
        reasons.append("budget not approved")
        reasons.append("timeline longer or budget not approved")
    else:
        intent += 3

    if timeline == "near":
        intent += 10
    elif timeline == "mid":
        intent += 5
        reasons.append("timeline longer or budget not approved")
    elif timeline == "long":
        intent += 0
        reasons.append("timeline too long")
        reasons.append("timeline longer or budget not approved")
    else:
        intent += 2

    if not use_case:
        intent = min(intent, 6)
        reasons.append("insufficient intent")

    score = max(0, min(100, fit + intent))

    if fit >= 40:
        reasons.append("strong fit")

    reasons = list(dict.fromkeys(reasons))

    return score, {
        "reasons": reasons,
        "fit": fit,
        "intent": intent,
        "budget": budget,
        "timeline": timeline,
        "has_migration_intent": has_migration_intent,
        "is_senior": is_senior,
    }


def decide(score: int, meta: Dict[str, Any]) -> Tuple[str, float]:
    if meta["budget"] == "approved" and meta["timeline"] == "near" and meta["has_migration_intent"] and meta["is_senior"]:
        if score >= 75:
            return "qualify", 0.9
        return "nurture", 0.75

    if score < 35:
        return "disqualify", 0.75

    return "nurture", 0.8


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    lead = payload.get("lead", {}) or {}
    score, meta = score_lead(lead)
    decision, confidence = decide(score, meta)

    explanation = meta["reasons"][:10]

    slack_msg = (
        f"{decision.upper()} lead ({int(score)}). "
        f"{lead.get('industry','')}, {lead.get('title','')}. "
        f"Use case: {lead.get('use_case','')}. Next step: discovery or nurture."
    )
    slack_msg = redact(slack_msg)

    actions: List[Dict[str, Any]] = [
        {"type": "slack_post", "target": "ae-channel", "risk": "low", "requires_approval": False, "payload": {"message": slack_msg}}
    ]

    requires_approval = True
    if decision == "qualify":
        requires_approval = False
        actions.append(
            {
                "type": "salesforce_update",
                "target": "lead",
                "risk": "low",
                "requires_approval": False,
                "payload": {"fields": {"Lead_Status__c": "Qualified", "Qualification_Score__c": int(score), "Next_Step__c": "Schedule discovery"}},
            }
        )

    return {
        "decision": decision,
        "score": int(score),
        "summary": "Lead triaged with fit/intent scoring and guardrails applied.",
        "explanation": explanation,
        "actions": actions,
        "confidence": round(float(confidence), 2),
        "requires_approval": requires_approval,
    }
