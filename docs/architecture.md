# Architecture

This repository implements a small collection of GTM-focused AI agents on a shared, policy-governed runtime.
The goal is not automation demos, but safe, explainable decision support inside real revenue workflows.

---

## High-level design

All agents share the same execution model:

1. Ingest context and artifacts
2. Read from Salesforce (mocked locally)
3. Reason and decide
4. Propose actions
5. Enforce guardrails
6. Emit structured output and eval signals

Each agent differs in logic, not in architecture.

---

## Shared runtime

All agents run on a common runtime located in `shared/runtime/`.

**Responsibilities**
- Standardize agent input and output
- Orchestrate tool calls
- Track intermediate state
- Apply policies before actions execute

**Key components**
- `orchestrator.py`. Entry point for agent execution
- `types.py`. Canonical input, output, and action schemas
- `router.py`. Routes requests to the selected agent

This keeps behavior consistent across agents and makes new agents cheap to add.

---

## Agent contract

Each agent implements the same contract.

**Inputs**
- Context. Who triggered the agent, when, and why
- Artifacts. Transcripts, notes, free text
- Salesforce data. Objects the agent is allowed to read
- History. Optional prior decisions

**Outputs**
- Summary. Human-readable explanation
- Score. Qualification score or risk score
- Decision. Explicit enum, not free text
- Explanation. Reasons plus evidence pointers
- Actions. Structured, typed proposals
- Confidence. Used by guardrails

This contract is enforced in code and validated in evals.

---

## Tools and connectors

External systems are accessed only through thin adapters in `shared/connectors/`.

**Salesforce**
- Read-only queries for leads, opportunities, and accounts
- Write actions are proposed, not executed directly
- Local runs use mocks

**Slack**
- Message formatting isolated in one place
- All output passes through redaction before posting
- Local runs use mocks

This keeps business logic independent of integration details.

---

## Guardrails and safety

All actions flow through shared policies in `shared/policies/`.

**Global guardrails**
- PII is redacted before any Slack output
- Salesforce writes require:
  - Confidence ≥ threshold
  - Action allowlisted for that agent
  - Low-risk classification
- Otherwise actions are flagged as approval-required

**Why this matters**
Agents can reason freely, but they cannot act freely.
Every write is explainable, bounded, and reviewable.

---

## Evaluation loop

Each agent ships with explicit evaluation data.

**Eval structure**
- JSONL datasets per agent
- Expected decisions, scores, or flags
- Shared eval runner and metrics

**What is measured**
- Decision accuracy
- Extraction quality
- Rule correctness
- Explainability completeness

Evals are designed to catch regressions when prompts or logic change.

---

## Observability

Lightweight observability lives in `shared/observability/`.

Tracked signals:
- Agent decisions
- Scores and confidence
- Actions proposed vs blocked
- Policy violations

This mirrors how production GTM agents would be monitored.

---

## Why this architecture

- Shared runtime avoids prompt sprawl
- Explicit contracts force clarity
- Guardrails prevent unsafe automation
- Evals make behavior testable
- Mocks keep the repo runnable anywhere

The intent is to demonstrate how AI agents fit into GTM systems, not to hide complexity behind tooling.
