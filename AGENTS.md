# Research governance

This repository prepares a separate O-RAN/5G RAN resource-allocation study. The human researcher owns research questions, hypotheses, priorities, and scientific interpretation. Work only within this project unless specifically authorized. Do not reuse or link the historical NR-U simulator tree or its compiler patches.

## Mission lifecycle and documentation gate

Every mission must begin with a report based on `templates/MISSION-TEMPLATE.md`, documenting its objective, scope, rationale, requirements, and acceptance criteria. Identify existing architecture/components, risks, dependencies, and verification evidence before implementation. Explain important alternatives and decisions, distinguishing recorded reasons from retrospective inference.

Document every source/configuration change, its purpose and effect, dependencies and versions, effective parameters, commands, seeds, statistical methods, results, failures, troubleshooting, limitations, and unresolved questions. Preserve full logs and immutable raw outputs under unique run-specific locations. Do not overwrite earlier data. Include GitHub-compatible Mermaid diagrams for architecture, topology, data flow, algorithms, or workflow changes; explain and label conceptual diagrams.

Classify claims as source-verified, observed, interpretation, hypothesis, planned, or unverified. Never invent results, standards compliance, causal mechanisms, or real-world validity. Separate offered traffic from achieved throughput. Report loss/censoring with received-packet latency distributions.

Update canonical docs rather than creating conflicting accounts, and maintain links in the root README, `docs/README.md`, and `docs/MISSIONS.md`. Update `docs/DOCUMENTATION-AUDIT.md` and the relevant mission report. A mission remains INCOMPLETE until its implementation/blocker, verification, evidence, documentation, reproduction instructions, audit, and checklist are complete.

## Version control and data integrity

After each completed mission, audit staged paths, sizes, credentials, generated artifacts, and upstream source trees; make a descriptive Git commit and push to `main` unless the researcher explicitly says otherwise. Inspect remote history and use only safe fast-forward-compatible reconciliation. Never force-push, delete prior evidence, switch branches as a workaround, or commit credentials, simulator source/build trees, virtual environments, or large generated output. Record commit and remote verification in the report.

Before significant downloads/builds/runs, check free space. Keep the O-RAN simulator in a separate, explicitly pinned environment. Never copy legacy NR-U/ns-3.35/NR-v1.2 patches into the modern environment.
