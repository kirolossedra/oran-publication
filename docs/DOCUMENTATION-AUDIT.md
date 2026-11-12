# Documentation audit

**Updated:** 2026-11-12. **Portfolio:** KIRO issue #24 remains open while the integrated campaign and mission gates remain active.

## Current repository snapshot

The researcher-authored commits `9a8697c1aa31c6dcf88940c44778bed3e2ba9893` and `e85b4dc0edc25543a5ecbea61e6c4bef4e41102f` introduce the integrated campaign and then add complete editable ib-ORAN source overrides, an upstream source map, and a source checksum manifest. Earlier completed RA-ENG-001–003 reports and navigation are preserved in Git history through `fcb460f8ec3098372605635a5c40b823faff1d2d`; this update restores compact root documentation/navigation, `AGENTS.md`, the mission template, and `.gitignore` without changing campaign source or result files. The RA-ENG-004 commit was replayed safely on top of the latest remote commit. README conflicts were resolved by retaining researcher campaign text and adding mission links; local `main` is a fast-forward descendant of `origin/main`.

## RA-ENG-004 evidence audit

The [mission report](missions/RA-ENG-004-instrumentation.md) records source findings, implementation, parameters, failures, limits and commands. The [metric schema](methodology/g1-packet-grant-metrics.md) distinguishes application packets, FlowMonitor IP-layer counters, applied gNB MAC grants and radio/mobility traces. Source replay patches apply with `--unidiff-zero --whitespace=error` to clean pinned ib-ORAN and NR archives. The ns3 target built, three analyzer tests passed, and target-only/all-six/UL/DL/no-traffic/short-sink cases completed. Normal UDP application event counts reconcile with FlowMonitor; the intentionally short sink records 20 censored application receptions while FlowMonitor confirms IP-layer reception, so this is not labelled network loss. Raw evidence is preserved under ignored `simulator/logs/RA-ENG-004-20261112/`; all 55 file hashes verified.

The first local delivery commit was `43e173d`; after safe replay on the latest source snapshot, the implementation commit was `943716e`. The three-commit delivery was pushed as a fast-forward at `b75c5784d0ab928080037f6afa22ab97af359e10`; remote `main` matched on verification and the worktree was clean. No force-push or remote overwrite occurred. The post-rebase audit covered 21 paths (about 99 KB; largest 33,916 bytes), with no credential-pattern hits, generated simulator/source/build/virtualenv paths, or broken local links. GitHub issue #17 was updated with evidence and closed as completed.

## Campaign v2 evidence

The latest campaign README reports 92/160 successful cells at packaging, two incomplete attempts, and 68 not completed. The editable source overrides and source-map checksums are part of that package. Its analysis and results remain in progress; the invalidated v1 packet-tag latency/PDR summaries are explicitly excluded. This audit does not treat the RA-ENG-004 smoke runs as campaign results and does not claim formal campaign completion.

## RA-ENG-005 load calibration pre-implementation gate

The template-based [RA-ENG-005 report](missions/RA-ENG-005-load-calibration.md) was created before source inspection. The campaign v2 runner and analyzer expose configured per-UE rates, packet events, applied grants, and MAC demand records; the dApp trace records buffer bytes, CQI, achievable rate, and actual throughput at each control opportunity. This is source/code availability only: no campaign v2 raw run directories are present in this local workspace, so the remote package's 92 successful-cell count cannot be analyzed here. Disk check before additional runs found 494 GiB available. Detailed compatibility, per-UE target-only traffic construction, and bounded calibration design remain under audit; no #18 source changes or runs are claimed yet.

## Audit checks already performed for RA-ENG-004 delivery

- Three synthetic tests passed; pinned target build succeeded.
- Both source patches applied cleanly to fresh archives with zero-context replay.
- Raw run directory contained 55 hashed files; `sha256sum -c SHA256SUMS` passed.
- Before rebase, staged audit covered 18 text paths, about 130 KB; no credential-pattern hits or simulator/source/build/virtualenv/raw-output paths; `git diff --cached --check` passed and 91 local Markdown links resolved.
- The post-rebase path, size, credential, generated-artifact, whitespace, and link audit is complete. Recheck remote fast-forward state immediately before push and verify the resulting remote SHA afterward.
