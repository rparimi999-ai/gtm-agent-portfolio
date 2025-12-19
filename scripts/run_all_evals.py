from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple

from shared.evals.runner import run_eval_file


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_demo_output(agent_dir: str) -> Dict[str, Any]:
    path = os.path.join(REPO_ROOT, "agents", agent_dir, "demo", "output.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _predict_from_demo_output(agent_dir: str):
    """
    Temporary predict function.
    Returns the same demo output for every case.
    This proves the eval plumbing works, even before agent logic is implemented.

    Later: replace with real agent execution.
    """
    demo_out = _load_demo_output(agent_dir)

    def _predict(_case_input: Dict[str, Any]) -> Dict[str, Any]:
        return demo_out

    return _predict


def main() -> None:
    targets = [
        ("lead_qualification", "lead_qualification"),
        ("meeting_followup", "meeting_followup"),
        ("pipeline_risk_inspector", "pipeline_risk_inspector"),
    ]

    total_pass = 0
    total_fail = 0

    print("Running evals (demo-output mode)\n")

    for agent_key, agent_dir in targets:
        eval_path = os.path.join(REPO_ROOT, "agents", agent_dir, "evals", "cases.jsonl")

        if not os.path.exists(eval_path):
            print(f"[SKIP] {agent_key}: missing eval file {eval_path}")
            continue

        predict_fn = _predict_from_demo_output(agent_dir)
        passed, failed, results = run_eval_file(agent_key, eval_path, predict_fn)

        total_pass += passed
        total_fail += failed

        print(f"{agent_key}: {passed} passed, {failed} failed")

        # Print failures with case ids and reasons
        if failed:
            for r in results:
                if not r.passed:
                    print(f"  - {r.case_id}")
                    for msg in r.failures:
                        print(f"      * {msg}")
        print("")

    print(f"TOTAL: {total_pass} passed, {total_fail} failed")

    # Exit code for CI later
    if total_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
