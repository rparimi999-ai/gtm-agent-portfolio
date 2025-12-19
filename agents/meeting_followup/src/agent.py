from __future__ import annotations

import re
from typing import Any, Dict, List


EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def redact(text: str) -> str:
    return EMAIL_RE.sub("[REDACTED_EMAIL]", text)


def _find_keywords(text: str, phrases: List[str]) -> List[str]:
    t = text.lower()
    hits = []
    for p in phrases:
        if p.lower() in t:
            hits.append(p)
    return hits


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript = (payload.get("transcript") or "").strip()
    opp = payload.get("opportunity") or payload.get("meeting", {}).get("opportunity") or {}
    t = transcript.lower()

    requirements = []
    for req in ["eu data residency", "encryption at rest", "sso"]:
        if req in t:
            requirements.append(req)

    competition = []
    for comp in ["azure", "gcp", "snowflake"]:
        if comp in t:
            competition.append(comp)

    # metrics
    metrics = []
    m_pct = re.findall(r"\b\d{1,3}%\b", transcript)
    metrics.extend(m_pct)
    if "half" in t:
        metrics.append("half")

    # Next steps (simple heuristics)
    seller_actions = []
    for phrase in ["send estimate", "send pricing", "send a draft plan", "send high-level migration plan", "confirm", "provide estimate"]:
        if phrase in t:
            seller_actions.append(phrase)
    if "security review" in t or "security workshop" in t or "security workshop" in transcript.lower():
        seller_actions.append("schedule security workshop/review")

    customer_actions = []
    for phrase in ["loop in", "share the final vendor list", "review internally", "get back to you", "book a workshop", "schedule a security review"]:
        if phrase in t:
            customer_actions.append(phrase)

    # due dates (capture common tokens, keep as strings)
    due_dates = []
    for token in ["friday", "next tuesday", "tuesday", "jan 10", "january 10", "next week", "february", "q1"]:
        if token in t:
            due_dates.append(token)

    # decision process signals
    decision_process = {}
    if "cio" in t:
        decision_process["approver"] = "CIO"
    if "procurement" in t:
        decision_process["paper_process"] = "Procurement involved"
    if "redlines" in t:
        decision_process["paper_process_detail"] = "Redlines mentioned"

    # risks + open questions
    risks = []
    open_questions = []
    if "no clear timeline" in t or ("no timeline" in t):
        risks.append("no clear timeline")
        open_questions.append("What is the target timeline and decision date?")
    if "security" in t:
        risks.append("security gating item")
        open_questions.append("Which controls are required for approval?")
    if "eu data residency" in t:
        risks.append("EU data residency constraints")
        open_questions.append("Which workloads must remain in-region?")

    extracted = {
        "customer_objectives": [],
        "requirements": requirements,
        "competition": competition,
        "decision_process": decision_process,
        "next_steps": {
            "customer_actions": customer_actions,
            "seller_actions": seller_actions,
            "due_dates": due_dates,
            "open_questions": open_questions,
            "risks": risks,
        },
    }

    # Slack recap
    recap = (
        f"Meeting recap . Stage={opp.get('stage','')}. "
        f"Reqs={', '.join(requirements) or 'none captured'}. "
        f"Comp={', '.join(competition) or 'none mentioned'}. "
        f"Seller next steps={'; '.join(seller_actions) or 'none captured'}. "
        f"Customer next steps={'; '.join(customer_actions) or 'none captured'}."
    )
    recap = redact(recap)

    actions: List[Dict[str, Any]] = [
        {
            "type": "slack_post",
            "target": "ae-channel",
            "risk": "low",
            "requires_approval": False,
            "payload": {"message": recap},
        }
    ]

    # Salesforce update suggestion is always approval-gated in v1
    actions.append(
        {
            "type": "salesforce_update",
            "target": "opportunity",
            "risk": "med",
            "requires_approval": True,
            "payload": {
                "opportunity_id": opp.get("id"),
                "fields": {
                    "Next_Step__c": " . ".join(seller_actions[:3]) or "Follow up with next steps from meeting",
                    "Risks__c": " . ".join(risks[:3]) or "No explicit risks captured",
                },
            },
        }
    )

    return {
        "summary": "Transcript converted into structured follow-ups with approval-gated CRM suggestions.",
        "extracted": extracted,
        "actions": actions,
        "confidence": 0.83,
        "requires_approval": True,
    }
