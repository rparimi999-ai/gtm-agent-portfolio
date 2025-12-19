# GTM Agent Portfolio

A hands-on portfolio of AI agents designed around real GTM workflows.

Each agent:
- operates on a shared runtime
- enforces explicit guardrails
- produces structured, explainable outputs
- is validated with deterministic eval cases

This repo is mock-first and runs locally. Agent behavior is inspectable, testable, and reviewable by design.

## What this repo demonstrates

This is not a collection of demos. It shows how to design **reviewable, production-ready GTM agents** with:

- clear input and output contracts
- explicit decision logic
- explainability suitable for managers and operators
- eval-driven development, where behavior is specified before automation

The goal is to make agent behavior debuggable, auditable, and trustworthy.

## Agents

### Lead Qualification Agent
Routes inbound leads, scores fit and intent, explains the decision, and proposes next actions.

**What it proves**
- deterministic scoring with bounded outputs
- ICP and intent reasoning
- guardrails around CRM updates
- explainable decisions rather than opaque labels

### Meeting Follow-up Agent
Converts unstructured meeting transcripts into structured next steps, risks, metrics, and CRM suggestions.

**What it proves**
- unstructured → structured extraction
- separation of signal from noise
- approval-gated CRM actions
- safe Slack summaries with basic PII redaction

### Pipeline Risk Inspector
Analyzes pipeline using MEDDPICC-style heuristics and flags execution risk with manager-ready explanations.

**What it proves**
- heuristic reasoning over CRM fields
- explainability with supporting evidence
- calibrated risk scoring
- consistent outputs for forecast inspection

## Repo structure

```text
agents/
  lead_qualification/
  meeting_followup/
  pipeline_risk_inspector/

shared/
  evals/
    metrics.py
    runner.py
    schemas.py

scripts/
  run_agent.py
  run_all_evals.py

Each agent exposes a single run(payload) entrypoint.
Shared eval logic enforces consistent expectations across agents.
Salesforce and Slack are modeled as actions, not live side effects.

Run evals locally
git clone https://github.com/rparimi999-ai/gtm-agent-portfolio.git
cd gtm-agent-portfolio
python scripts/run_all_evals.py

Expected output:
lead_qualification: 8 passed, 0 failed
meeting_followup: 6 passed, 0 failed
pipeline_risk_inspector: 6 passed, 0 failed
TOTAL: 20 passed, 0 failed

Evals are the contract. If behavior changes, evals fail.
This makes agent behavior explicit and regression-safe.

How to read this repo
If you have limited time:
Read this README.
Skim ARCHITECTURE.md to understand the runtime and guardrails.
Review the eval cases to see how “correct” behavior is defined.
Open any agent’s src/agent.py to see how that behavior is implemented.
This repo is meant to be read, not just executed.

Design principles
Mock before integrate
- Behavior is validated before touching real systems.

Explainability over cleverness
- Every decision produces reasons a human can review.

Guardrails before autonomy
- Risky actions are approval-gated by default.

Evals as architecture
- Tests define correctness, not just code paths.

This repo intentionally avoids end-to-end integrations to keep agent behavior auditable.

Notes for reviewers
All agents expose a single run(payload) entrypoint.
Outputs are structured and bounded.
Salesforce and Slack interactions are modeled as actions, not live integrations.
CI runs evals on every push to prevent behavioral regressions.

For deeper context, see:
ARCHITECTURE.md
PORTFOLIO_NOTES.md
