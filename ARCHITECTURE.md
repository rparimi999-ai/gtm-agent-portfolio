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

## From mock agent to production system

This repo is intentionally mock-first. That is not a limitation. It is how agent behavior is stabilized before integration risk is introduced.

Moving from this portfolio to a production system would happen in clear, incremental steps.

### 1. Preserve the agent contract
The most important production artifact is not the model or the prompt. It is the contract:

- input shape
- output structure
- required explanations
- action types and approval requirements

These contracts are already defined and enforced by evals. In production, they remain unchanged. Integrations adapt to the contract, not the other way around.

---

### 2. Introduce an action executor
In this repo, agents emit actions as structured objects. In production, those actions would flow through a centralized executor responsible for:

- enforcing approval rules
- validating payloads
- executing side effects (CRM updates, Slack posts)
- logging outcomes and failures

This keeps agents focused on reasoning and prevents integration logic from leaking into agent code.

---

### 3. Swap mock connectors for real adapters
Salesforce and Slack are modeled as abstract actions here. Production introduces adapters that translate those actions into real API calls.

This layer:
- handles authentication and retries
- normalizes API failures
- emits structured telemetry

Agents do not change when adapters are introduced. Only the executor does.

---

### 4. Add observability before adding autonomy
Before increasing automation, the system would add visibility:

- per-run traces (inputs, outputs, actions)
- decision distributions over time
- eval pass rates in CI and production shadow runs

This allows teams to detect drift, regressions, and unintended behavior early.

---

### 5. Graduate automation deliberately
Only after behavior is stable and observable would autonomy increase:

- remove approval gates selectively
- automate low-risk actions first
- keep evals as a permanent regression harness

In production, evals do not disappear. They become the safety rail that allows iteration without fear.

---

The core idea is simple:  
**stabilize behavior first, integrate second, automate last.**

This repo is designed to make that progression explicit.

