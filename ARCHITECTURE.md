# Architecture

This repo is a portfolio of GTM agents built around one idea. Make agent behavior reviewable.

Agents are implemented as pure functions with a single entrypoint:

- `run(payload) -> result`

Where `payload` is a plain dict and `result` is a structured dict with:
- a decision or assessment
- an explanation suitable for a human reviewer
- a list of proposed actions (Slack posts, Salesforce updates), with approval requirements

No network calls are required to run the repo. The “integration surface” is modeled as action objects, which is the seam where real adapters would plug in later.

---

## Runtime model

### 1. Inputs
Each agent receives a minimal payload that represents the GTM artifact it reasons over:
- lead record
- meeting transcript + opportunity context
- opportunity fields + MEDDPICC-style signals

Inputs are intentionally small and explicit so behavior is deterministic and testable.

---

### 2. Reasoning + heuristics
Each agent applies bounded logic:
- scoring bands rather than open-ended grading
- heuristics that map to real operator checks
- explicit phrases in explanations so reviewers can see “why”

---

### 3. Guardrails
Actions that can change systems are treated as higher risk:
- CRM updates are typically approval-gated
- summaries redact obvious PII patterns
- outputs are bounded and predictable (no unstructured blobs)

The point is not “perfect safety.” The point is explicit, inspectable safety.

---

### 4. Actions as an integration seam
Agents emit actions like:

- `{"type": "slack_post", ...}`
- `{"type": "salesforce_update", ...}`

These actions are not executed in this repo. They are the stable contract that makes integrations swappable:
- mock executor for local demos
- real connector for production
- logging/telemetry wrapper for observability

---

## Evaluation architecture

Evals are not an afterthought. They define the expected behavior contract:
- required explanation phrases
- score bands
- approval requirements
- minimum explainability counts

`scripts/run_all_evals.py` runs the suite across all agents and prints a pass/fail summary. If behavior changes, evals fail.

---

## How this would extend to production

If you wanted to productionize:
- add connectors for Slack and Salesforce
- add an action executor that enforces guardrails centrally
- add structured telemetry (inputs, outputs, action decisions)
- add versioning for prompts/heuristics and eval cases

The repo is built to make that path straightforward.
