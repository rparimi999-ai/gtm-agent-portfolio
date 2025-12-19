from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from typing import Any, Dict


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)


AGENT_MODULES = {
    "lead_qualification": "agents.lead_qualification.src.agent",
    "meeting_followup": "agents.meeting_followup.src.agent",
    "pipeline_risk_inspector": "agents.pipeline_risk_inspector.src.agent",
}


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a GTM agent locally.")
    parser.add_argument("--agent", required=True, choices=sorted(AGENT_MODULES.keys()))
    parser.add_argument("--demo", action="store_true", help="Run using agents/<agent>/demo/input.json")
    parser.add_argument("--input", help="Path to JSON input file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    agent_dir = args.agent
    if args.demo:
        input_path = os.path.join(REPO_ROOT, "agents", agent_dir, "demo", "input.json")
    elif args.input:
        input_path = args.input
        if not os.path.isabs(input_path):
            input_path = os.path.join(os.getcwd(), input_path)
    else:
        raise SystemExit("Provide --demo or --input <path>")

    payload = load_json(input_path)

    mod = importlib.import_module(AGENT_MODULES[args.agent])
    if not hasattr(mod, "run"):
        raise SystemExit(f"Agent module {AGENT_MODULES[args.agent]} is missing run(input_dict)->output_dict")

    out = mod.run(payload)

    if args.pretty:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
