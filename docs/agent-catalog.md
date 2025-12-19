# Agent Catalog

| Agent | Trigger | Salesforce Reads | Salesforce Writes | Slack Output | Eval Focus |
|---|---|---|---|---|---|
| Lead Qualification | New or updated lead | Lead, Account | Lead status, score (guarded) | AE summary + next step | Decision accuracy, calibration |
| Meeting Follow-up | Meeting completed | Opportunity, Contacts | Suggested updates (approval) | Structured recap | Extraction precision, grounding |
| Pipeline Risk Inspector | Scheduled or on-demand | Opportunity | Task suggestions (approval) | Risk digest | Rule correctness, explainability |

All agents share a common runtime, guardrails, and eval harness.
