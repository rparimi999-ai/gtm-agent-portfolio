# GTM Agent Portfolio

A hands-on portfolio of AI agents designed around real GTM workflows.

Each agent:
- operates on a shared runtime
- enforces explicit guardrails
- produces structured, explainable outputs
- is validated with deterministic eval cases

This repo is mock-first and runs locally. Salesforce and Slack interactions are modeled as actions, not live integrations, so behavior is inspectable and testable.

---

## What this repo demonstrates

This is not a collection of demos. It shows how to design **production-ready GTM agents** with:

- clear input and output contracts
- explicit decision logic
- explainability suitable for managers and operators
- eval-driven development (behavior is specified before automation)

The goal is to make agent behavior reviewable, debuggable, and trustworthy.

---

## Agents

### Lead Qualification Agent
Routes inbound leads, scores fit and intent, explains the decision, and proposes next actions.

**What it proves**
- deterministic scoring with bounded outputs
- ICP and intent reasoning
- guardrails around CRM updates
- explainable decisions, not just labels

---

### Meeting Follow-up Agent
Converts unstructured meeting transcripts into structured next steps, risks, metrics, and CRM suggestions.

**What it proves**
- unstructured → structured extraction
- separation of signal vs noise
- approval-gated CRM actions
- safe Slack summaries with PII redaction

---

### Pipeline Risk Inspector
Analyzes pipeline using MEDDPICC-style heuristics and flags execution risk with manager-ready explanations.

**What it proves**
- heuristic reasoning over CRM fields
- explainability with evidence
- calibrated risk scoring
- consistent outputs for forecast inspection

---

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
---

## Run evals locally

```bash
git clone https://github.com/rparimi999-ai/gtm-agent-portfolio.git
cd gtm-agent-portfolio
python scripts/run_all_evals.py

Expected Output:
lead_qualification: 8 passed, 0 failed
meeting_followup: 6 passed, 0 failed
pipeline_risk_inspector: 6 passed, 0 failed

TOTAL: 20 passed, 0 failed
Evals are the contract. If behavior changes, evals fail.

How to read this repo

If you have limited time:

Read this README.

Skim ARCHITECTURE.md to understand the runtime and guardrails.

Open any agent’s src/agent.py and scan:

decision logic

explanation phrases

action guardrails

Review the eval cases to see how behavior is specified.

This repo is meant to be read, not just executed.

Design principles:
Mock before integrate
Behavior is validated before touching real systems.
Explainability over cleverness
Every decision produces reasons a human can review.
Guardrails before autonomy
Risky actions are approval-gated by default.
Evals as architecture
Tests define correctness, not just code paths.

Notes for reviewers
All agents expose a single run(payload) entrypoint.
Outputs are structured and bounded.
Salesforce and Slack are modeled as actions, not side effects.
CI runs evals on every push.

For deeper context, see:
ARCHITECTURE.md
PORTFOLIO_NOTES.md
