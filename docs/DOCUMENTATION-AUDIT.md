# Documentation audit

**Updated:** 2026-11-12. **Portfolio:** KIRO issue #24 remains open while the integrated campaign and mission gates remain active.

## Current repository snapshot

The researcher-authored `origin/main` commit `9a8697c1aa31c6dcf88940c44778bed3e2ba9893` introduces `campaigns/20261111-g1-integrated-v2/` and removes earlier root-level mission documentation. Earlier completed RA-ENG-001–003 reports and navigation are preserved in Git history through `fcb460f8ec3098372605635a5c40b823faff1d2d`; this update restores compact root documentation/navigation rather than changing the v2 campaign's files or results.

## RA-ENG-004 evidence audit

The [mission report](missions/RA-ENG-004-instrumentation.md) records source findings, implementation, parameters, failures, limits and commands. The [metric schema](methodology/g1-packet-grant-metrics.md) distinguishes application packets, FlowMonitor IP-layer counters, applied gNB MAC grants and radio/mobility traces. Source replay patches apply with `--unidiff-zero --whitespace=error` to clean pinned ib-ORAN and NR archives. The ns3 target built, three analyzer tests passed, and target-only/all-six/UL/DL/no-traffic/short-sink cases completed. Normal UDP application event counts reconcile with FlowMonitor; the intentionally short sink records 20 censored application receptions while FlowMonitor confirms IP-layer reception, so this is not labelled network loss. Raw evidence is preserved under ignored `simulator/logs/RA-ENG-004-20261112/`; all 55 file hashes verified.

The first delivery commit `43e173d` was created on the prior local main. While preparing publication, remote main advanced to the researcher-authored campaign snapshot. A rebase onto `origin/main` is in progress and has a README content conflict plus modify/delete conflicts for root navigation/report files that the remote snapshot removed. No force-push or remote overwrite has occurred. Final staged size/security/path audit and remote SHA verification must be repeated after conflict resolution.

## Campaign v2 evidence

The campaign README reports 90/160 successful cells at packaging, two incomplete attempts, and 70 not completed. Its analysis and results remain in progress; the invalidated v1 packet-tag latency/PDR summaries are explicitly excluded. This audit does not treat the RA-ENG-004 smoke runs as campaign results and does not claim formal campaign completion.

## Audit checks already performed for RA-ENG-004 delivery

- Three synthetic tests passed; pinned target build succeeded.
- Both source patches applied cleanly to fresh archives with zero-context replay.
- Raw run directory contained 55 hashed files; `sha256sum -c SHA256SUMS` passed.
- Before rebase, staged audit covered 18 text paths, about 130 KB; no credential-pattern hits or simulator/source/build/virtualenv/raw-output paths; `git diff --cached --check` passed and 91 local Markdown links resolved.
- Those staged totals and link results are provisional because rebase conflict resolution changes the tree; rerun the audit before final publication.
