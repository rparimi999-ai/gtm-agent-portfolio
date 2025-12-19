# Portfolio Notes

This repo is intentionally mock-first and eval-driven.

The goal is to demonstrate agent design for GTM workflows in a way that is:
- deterministic
- explainable
- safe by default
- easy to integrate later

---

## What each agent proves

### Lead Qualification Agent
Proves:
- routing decisions based on fit + intent
- calibrated scoring (bounded, predictable)
- decision explainability with required reasons
- guardrails around system updates

Why it matters:
Qualification is where bad automation creates downstream pain. A good agent must be conservative, explain itself, and be easy to inspect.

---

### Meeting Follow-up Agent
Proves:
- unstructured transcript → structured fields
- extracting metrics, requirements, competition, and process
- separating “recap” from “CRM suggestions”
- approval-gated updates and safer Slack summaries

Why it matters:
Meeting intelligence only creates value when it becomes usable structure that fits the GTM operating model.

---

### Pipeline Risk Inspector
Proves:
- MEDDPICC-style checks expressed as simple heuristics
- calibrated risk scoring and consistent outputs
- manager-ready explanations + evidence
- minimum explainability thresholds

Why it matters:
Forecast quality improves when teams standardize what “risk” means and make inspections repeatable.

---

## Intentional constraints

- No live integrations
- No hidden state
- No “magic” LLM behavior required to pass
- Evals define the contract

This keeps the repo runnable, auditable, and easy to review.

---

## What I would build next

1) Integrations as adapters
- Slack connector
- Salesforce connector
- action executor enforcing approvals and logging

2) Observability
- structured traces per run (inputs, outputs, action decisions)
- per-agent dashboards (pass rate by eval category, drift indicators)

3) Versioning + governance
- versioned agent policies and eval suites
- change management for scoring rules and “required reasons”

4) Realistic data surfaces
- sample Salesforce objects
- sample Slack thread context
- sample call transcript artifacts

---

## How to review this repo quickly

1) Read `README.md` and `ARCHITECTURE.md`
2) Run `python scripts/run_all_evals.py`
3) Open each agent’s `src/agent.py` and scan:
   - decision logic
   - explanation phrases
   - action guardrails
4) Review `cases.jsonl` for how behavior is specified
