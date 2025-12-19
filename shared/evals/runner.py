from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from shared.evals.schemas import EvalCase, EvalResult
from shared.evals.metrics import (
    _get,
    assert_contains,
    assert_empty_list,
    assert_equals,
    assert_max,
    assert_min,
    assert_min_count,
    assert_range,
)


def load_jsonl(path: str) -> List[EvalCase]:
    cases: List[EvalCase] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "id" not in obj or "input" not in obj or "expected" not in obj:
                raise ValueError(f"Invalid JSONL case at {path}:{line_no}. Must include id/input/expected.")
            cases.append(EvalCase(id=obj["id"], input=obj["input"], expected=obj["expected"], notes=obj.get("notes")))
    return cases


def _evaluate_lead_qualification(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []

    # decision
    if "decision" in expected:
        msg = assert_equals(actual.get("decision"), expected["decision"], "decision")
        if msg: failures.append(msg)

    # score constraints
    score = actual.get("score")
    if "score_min" in expected:
        msg = assert_min(score, expected["score_min"], "score")
        if msg: failures.append(msg)
    if "score_max" in expected:
        msg = assert_max(score, expected["score_max"], "score")
        if msg: failures.append(msg)
    if "score_range" in expected:
        lo, hi = expected["score_range"][0], expected["score_range"][1]
        msg = assert_range(score, lo, hi, "score")
        if msg: failures.append(msg)

    # explanation contains themes
    if "required_reasons" in expected:
        explanation = actual.get("explanation", [])
        for rr in expected["required_reasons"]:
            msg = assert_contains(explanation, rr, f"explanation contains {rr}")
            if msg: failures.append(msg)

    # actions expectations
    if "actions" in expected:
        acts = actual.get("actions", [])
        if expected["actions"].get("slack_post") is True:
            has_slack = any(a.get("type") == "slack_post" for a in acts)
            if not has_slack:
                failures.append("actions: expected a slack_post action")
        # For portfolio v1: we only check if SF update is proposed AND whether it is approval gated correctly.
        sf_allowed = expected["actions"].get("salesforce_update_allowed")
        if sf_allowed is not None:
            has_sf_update = any(a.get("type") == "salesforce_update" for a in acts)
            if sf_allowed is False and has_sf_update:
                failures.append("actions: unexpected salesforce_update action present")

    # guardrails
    guard = expected.get("guardrails", {})
    if guard.get("pii_redacted_in_slack") is True:
        # naive check: slack message should not contain '@' or obvious phone patterns
        for a in actual.get("actions", []):
            if a.get("type") == "slack_post":
                msg_txt = (a.get("payload", {}) or {}).get("message", "") or a.get("message", "")
                if "@" in msg_txt:
                    failures.append("guardrails: slack message appears to contain an email (@ present)")
                # simple phone check
                digits = sum(ch.isdigit() for ch in msg_txt)
                if digits >= 10 and ("-" in msg_txt or "(" in msg_txt):
                    failures.append("guardrails: slack message appears to contain a phone number pattern")
    return failures


def _evaluate_meeting_followup(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []

    # extraction expectations: we look under actual["extracted"] and/or top-level fields
    extracted = actual.get("extracted", {})

    ex = expected.get("extractions", {})
    # helper to check list containment inside nested structures
    def _contains_any_text(container: Any, needle: str, label: str) -> Optional[str]:
        return assert_contains(container, needle, label)

    if "seller_actions_contains" in ex:
        seller_actions = _get(extracted, "next_steps.seller_actions") or extracted.get("seller_actions")
        for item in ex["seller_actions_contains"]:
            msg = _contains_any_text(seller_actions, item, f"seller_actions contains {item}")
            if msg: failures.append(msg)

    if "customer_actions_contains" in ex:
        customer_actions = _get(extracted, "next_steps.customer_actions") or extracted.get("customer_actions")
        for item in ex["customer_actions_contains"]:
            msg = _contains_any_text(customer_actions, item, f"customer_actions contains {item}")
            if msg: failures.append(msg)

    if "due_dates_contains" in ex:
        due_dates = _get(extracted, "next_steps.due_dates") or extracted.get("due_dates") or []
        # due_dates may be list of dicts; stringify it
        for item in ex["due_dates_contains"]:
            msg = _contains_any_text(due_dates, item, f"due_dates contains {item}")
            if msg: failures.append(msg)

    if "metrics_contains" in ex:
        # metrics could be in objectives/requirements; use whole extracted text
        for item in ex["metrics_contains"]:
            msg = _contains_any_text(extracted, item, f"metrics contains {item}")
            if msg: failures.append(msg)

    if "requirements_contains" in ex:
        for item in ex["requirements_contains"]:
            msg = _contains_any_text(extracted, item, f"requirements contains {item}")
            if msg: failures.append(msg)

    if "decision_process_contains" in ex:
        dp = extracted.get("decision_process", {})
        for item in ex["decision_process_contains"]:
            msg = _contains_any_text(dp, item, f"decision_process contains {item}")
            if msg: failures.append(msg)

    if "paper_process_contains" in ex:
        dp = extracted.get("decision_process", {})
        for item in ex["paper_process_contains"]:
            msg = _contains_any_text(dp, item, f"paper_process contains {item}")
            if msg: failures.append(msg)

    if "competition_contains" in ex:
        for item in ex["competition_contains"]:
            msg = _contains_any_text(extracted, item, f"competition contains {item}")
            if msg: failures.append(msg)

    if "risks_contains" in ex:
        risks = _get(extracted, "next_steps.risks") or extracted.get("risks") or []
        for item in ex["risks_contains"]:
            msg = _contains_any_text(risks, item, f"risks contains {item}")
            if msg: failures.append(msg)

    if ex.get("open_questions_present") is True:
        oq = _get(extracted, "next_steps.open_questions") or extracted.get("open_questions") or []
        if not isinstance(oq, list) or len(oq) == 0:
            failures.append("open_questions: expected at least 1 item")

    # guardrails expectations
    guard = expected.get("guardrails", {})
    if guard.get("salesforce_update_requires_approval") is True:
        # any SF update action must be approval gated
        for a in actual.get("actions", []):
            if a.get("type") == "salesforce_update":
                if a.get("requires_approval") is not True:
                    failures.append("guardrails: salesforce_update should require approval")

    if guard.get("pii_redacted_in_slack") is True:
        for a in actual.get("actions", []):
            if a.get("type") == "slack_post":
                msg_txt = (a.get("payload", {}) or {}).get("message", "") or a.get("message", "")
                if "@" in msg_txt:
                    failures.append("guardrails: slack message appears to contain an email (@ present)")

    # slack recap presence
    slack = expected.get("slack", {})
    if slack.get("recap_present") is True:
        has_slack = any(a.get("type") == "slack_post" for a in actual.get("actions", []))
        if not has_slack:
            failures.append("slack: expected slack_post recap action")

    return failures


def _evaluate_pipeline_risk(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []

    # This runner supports both:
    # (A) single opp evaluation output: {"flags":[...], "risk_score":...}
    # (B) portfolio output with ranked_risks: [{"flags":[...], "risk_score":...}, ...]
    flags = actual.get("flags")
    risk_score = actual.get("risk_score") or actual.get("portfolio_risk_score")

    # If expected includes flags for a specific opp, we try to match from ranked_risks by opportunity_id if present
    target_id = _get(expected, "opportunity_id") or None

    if "ranked_risks" in actual and isinstance(actual["ranked_risks"], list):
        # try to find best match: if input had opportunity id, the case likely expects checks against that one opp
        # the JSONL we generated uses "input.opportunity" format, so actual likely is single-opp output.
        pass

    if expected.get("flags_empty") is True:
        msg = assert_empty_list(actual.get("flags", []), "flags")
        if msg: failures.append(msg)

    if "flags_contains" in expected:
        actual_flags = actual.get("flags", [])
        for fl in expected["flags_contains"]:
            if fl not in actual_flags:
                failures.append(f"flags: expected to include {fl!r}, got {actual_flags!r}")

    if "risk_score_min" in expected:
        msg = assert_min(actual.get("risk_score", risk_score), expected["risk_score_min"], "risk_score")
        if msg: failures.append(msg)

    if "risk_score_max" in expected:
        msg = assert_max(actual.get("risk_score", risk_score), expected["risk_score_max"], "risk_score")
        if msg: failures.append(msg)

    if "risk_score_range" in expected:
        lo, hi = expected["risk_score_range"][0], expected["risk_score_range"][1]
        msg = assert_range(actual.get("risk_score", risk_score), lo, hi, "risk_score")
        if msg: failures.append(msg)

    # explainability checks
    exp = expected.get("explainability", {})
    if exp:
        reasons = actual.get("explanation", [])
        evidence = actual.get("evidence", [])
        if "reasons_min" in exp:
            msg = assert_min_count(reasons, exp["reasons_min"], "explanation")
            if msg: failures.append(msg)
        if "evidence_min" in exp:
            msg = assert_min_count(evidence, exp["evidence_min"], "evidence")
            if msg: failures.append(msg)

    return failures


def evaluate_case(agent: str, case: EvalCase, actual: Dict[str, Any]) -> EvalResult:
    expected = case.expected
    failures: List[str] = []

    if agent == "lead_qualification":
        failures.extend(_evaluate_lead_qualification(expected, actual))
    elif agent == "meeting_followup":
        failures.extend(_evaluate_meeting_followup(expected, actual))
    elif agent == "pipeline_risk_inspector":
        failures.extend(_evaluate_pipeline_risk(expected, actual))
    else:
        failures.append(f"Unknown agent type: {agent}")

    return EvalResult(
        case_id=case.id,
        passed=len(failures) == 0,
        failures=failures,
        debug={"agent": agent, "expected": expected, "actual_keys": sorted(list(actual.keys()))},
    )


def run_eval_file(agent: str, eval_file_path: str, predict_fn) -> Tuple[int, int, List[EvalResult]]:
    """
    predict_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
      Given case.input, returns agent output dict
    """
    cases = load_jsonl(eval_file_path)
    results: List[EvalResult] = []
    passed = 0
    failed = 0

    for case in cases:
        actual = predict_fn(case.input)
        r = evaluate_case(agent, case, actual)
        results.append(r)
        if r.passed:
            passed += 1
        else:
            failed += 1

    return passed, failed, results
