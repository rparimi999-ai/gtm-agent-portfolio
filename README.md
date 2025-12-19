# gtm-agent-portfolio
# GTM Agent Portfolio

A portfolio of AI agents designed for real GTM workflows.
Each agent runs on a shared runtime, enforces guardrails, produces structured outputs, and is evaluated with explicit test cases.

This repo is mock-first and runs locally. Salesforce and Slack integrations are isolated and swappable.

---

## Agents

**Lead Qualification Agent**  
Routes inbound leads, scores fit and intent, explains the decision, and proposes next actions.

**Meeting Follow-up Agent**  
Turns unstructured meeting transcripts into structured next steps, risks, and CRM suggestions.

**Pipeline Risk Inspector**  
Analyzes late-stage pipeline using MEDDPICC-style heuristics and flags risk with manager-ready explanations.

---

## Quickstart (local, mock mode)

Run a single agent demo:
```bash
python scripts/run_agent.py --agent lead_qualification --demo
