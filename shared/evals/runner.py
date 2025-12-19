from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple, Callable

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
            cases.append(
                EvalCase(
                    id=obj["id"],
                    input=obj["input"],
                    expected=obj["expected"],
                    notes=obj.get("notes"),
                )
            )
    return cases


def _evaluate_lead_qualification(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []

    if "decision" in expected:
        msg = assert_equals(actual.get("decision"), expected["decision"], "decision")
        if msg:
            failures.append(msg)

    score = actual.get("score")
    if "score_range" in expected:
        lo, hi = expected["score_range"]
        msg = assert_range(score, lo, hi, "score")
        if msg:
            failures.append(msg)

    if "required_reasons" in expected:
        explanation = actual.get("explanation", [])
        for r in expected["required_reasons"]:
            msg = assert_contains(explanation, r, f"explanation contains {r}")
            if msg:
                failures.append(msg)

    if "actions" in expected:
        acts = actual.get("actions", [])
        if expected["actions"].get("salesforce_update_allowed") is False:
            if any(a.get("type") == "salesforce_update" for a in acts):
                failures.append("actions: unexpected salesforce_update action present")

    return failures


def _evaluate_meeting_followup(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    extracted = actual.get("extracted", {})
    ex = expected.get("extractions", {})

    if "metrics_contains" in ex:
        metrics = extracted.get("metrics", [])
        for m in ex["metrics_contains"]:
            msg = assert_contains(metrics, m, f"metrics contains {m}")
            if msg:
                failures.append(msg)

    if "requirements_contains" in ex:
        reqs = extracted.get("requirements", [])
        for r in ex["requirements_contains"]:
            msg = assert_contains(reqs, r, f"requirements contains {r}")
            if msg:
                failures.append(msg)

    if "competition_contains" in ex:
        comp = extracted.get("competition", [])
        for c in ex["competition_contains"]:
            msg = assert_contains(comp, c, f"competition contains {c}")
            if msg:
                failures.append(msg)

    return failures


def _evaluate_pipeline_risk(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[str]:
    failures: List[str] = []

    if "risk_score_range" in expected:
        lo, hi = expected["risk_score_range"]
        msg = assert_range(actual.get("risk_score"), lo, hi, "risk_score")
        if msg:
            failures.append(msg)

    if "explainability" in expected:
        exp = expected["explainability"]
        explanation = actual.get("explanation", [])
        if "reasons_min" in exp:
            msg = assert_min_count(explanation, exp["reasons_min"], "explanation")
            if msg:
                failures.append(msg)

    return failures


def evaluate_case(agent: str, case: EvalCase, actual: Dict[str, Any]) -> EvalResult:
    if agent == "lead_qualification":
        failures = _evaluate_lead_qualification(case.expected, actual)
    elif agent == "meeting_followup":
        failures = _evaluate_meeting_followup(case.expected, actual)
    elif agent == "pipeline_risk_inspector":
        failures = _evaluate_pipeline_risk(case.expected, actual)
    else:
        failures = [f"Unknown agent: {agent}"]

    return EvalResult(
        case_id=case.id,
        passed=len(failures) == 0,
        failures=failures,
        debug={"agent": agent},
    )


def run_eval_file(
    agent: str,
    eval_file_path: str,
    predict_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Tuple[int, int, List[EvalResult]]:
    cases = load_jsonl(eval_file_path)
    passed = failed = 0
    results: List[EvalResult] = []

    for case in cases:
        actual = predict_fn(case.input)
        result = evaluate_case(agent, case, actual)
        results.append(result)
        if result.passed:
            passed += 1
        else:
            failed += 1

    return passed, failed, results

