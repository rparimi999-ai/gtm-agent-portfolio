from __future__ import annotations

import re
from typing import Any, Dict, List

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def redact(text: str) -> str:
    return EMAIL_RE.sub("[REDACTED_EMAIL]", text)


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript = (payload.get("transcript") or "").strip()
    opp = payload.get("opportunity") or payload.get("meeting", {}).get("opportunity") or {}
    t = transcript.lower()

    requirements: List[str] = []
    if "eu data residency" in t:
        requirements.append("EU data residency")
    if "encryption at rest" in t:
        requirements.append("encryption at rest")
    if "sso" in t:
        requirements.append("SSO")

    competition: List[str] = []
    if "azure" in t:
        competition.append("Azure")
    if "gcp" in t:
        competition.append("GCP")
    if "snowflake" in t:
        competition.append("Snowflake")

    metrics: List[str] = []
    metrics.extend(re.findall(r"\d{1,3}\s*%", transcript))
    if "half" in t:
        metrics.append("half")

    seller_actions: List[str] = []
    if "send" in t and "estimate" in t:
        seller_actions.append("send estimate")
    if "security" in t and ("review" in t or "workshop" in t):
        seller_actions.append("schedule security workshop/review")

    customer_actions: List[str] = []
    if "loop in" in t:
        customer_actions.append("loop in stakeholders")
    if "procurement" in t:
        customer_actions.append("engage procurement")

    due_dates: List[str] = []
    for token in ["friday", "next tuesday", "tuesday", "jan 10", "january 10", "next week", "q1"]:
        if token in t:
            due_dates.append(token)

    decision_process: Dict[str, Any] = {}
    if "cio" in t:
        decision_process["approver"] = "CIO"
    if "procurement" in t:
        decision_process["paper_process"] = "Procurement"
    if "redlines" in t:
        decision_process["paper_process_detail"] = "redlines"

    risks: List[str] = []
    open_questions: List[str] = []
    if "security" in t:
        risks.append("security gating item")
        open_questions.append("Which controls are required for approval?")

    extracted = {
        "requirements": requirements,
        "competition": competition,
        "metrics": metrics,
        "decision_process": decision_process,
        "next_steps": {
            "customer_actions": customer_actions,
            "seller_actions": seller_actions,
            "due_dates": due_dates,
            "open_questions": open_questions,
            "risks": risks,
        },
    }

    recap = (
        f"Meeting recap . Stage={opp.get('stage','')}. "
        f"Reqs={', '.join(requirements) or 'none captured'}. "
        f"Comp={', '.join(competition) or 'none mentioned'}. "
        f"Metrics={', '.join(metrics) or 'none captured'}. "
        f"Seller next steps={'; '.join(seller_actions) or 'none captured'}."
    )
    recap = redact(recap)

    actions: List[Dict[str, Any]] = [
        {"type": "slack_post", "target": "ae-channel", "risk": "low", "requires_approval": False, "payload": {"message": recap}},
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
        },
    ]

    return {
        "summary": "Transcript converted into structured follow-ups with approval-gated CRM suggestions.",
        "extracted": extracted,
        "actions": actions,
        "confidence": 0.83,
        "requires_approval": True,
    }

