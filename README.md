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
