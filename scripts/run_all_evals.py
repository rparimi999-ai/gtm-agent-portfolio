from __future__ import annotations

import importlib
import os
import sys
from typing import Dict, Callable

# Ensure repo root is on path BEFORE importing shared/*
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from shared.evals.runner import run_eval_file  # noqa: E402

AGENTS = [
    ("lead_qualification", "agents.lead_qualification.src.agent"),
    ("meeting_followup", "agents.meeting_followup.src.agent"),
    ("pipeline_risk_inspector", "agents.pipeline_risk_inspector.src.agent"),
]


def _predict_fn(module_path: str) -> Callable[[Dict], Dict]:
    mod = importlib.import_module(module_path)
    if not hasattr(mod, "run"):
        raise RuntimeError(f"Missing run() in {module_path}")
    return getattr(mod, "run")


def main() -> None:
    total_pass = 0
    total_fail = 0

    print("Running evals (real agent logic)\n")

    for agent_name, module_path in AGENTS:
        eval_path = os.path.join(REPO_ROOT, "agents", agent_name, "evals", "cases.jsonl")
        if not os.path.exists(eval_path):
            print(f"[SKIP] {agent_name}: missing {eval_path}\n")
            continue

        predict = _predict_fn(module_path)
        passed, failed, results = run_eval_file(agent_name, eval_path, predict)

        total_pass += passed
        total_fail += failed

        print(f"{agent_name}: {passed} passed, {failed} failed")

        if failed:
            for r in results:
                if not r.passed:
                    print(f"  - {r.case_id}")
                    for msg in r.failures:
                        print(f"      * {msg}")
        print("")

    print(f"TOTAL: {total_pass} passed, {total_fail} failed")

    if total_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
