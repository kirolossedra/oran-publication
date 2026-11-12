# Documentation audit

**Updated:** 2026-11-12. **Portfolio:** KIRO issue #24 remains open while the integrated campaign and mission gates remain active.

## Current repository snapshot

The researcher-authored commits `9a8697c1aa31c6dcf88940c44778bed3e2ba9893` and `e85b4dc0edc25543a5ecbea61e6c4bef4e41102f` introduce the integrated campaign and then add complete editable ib-ORAN source overrides, an upstream source map, and a source checksum manifest. Earlier completed RA-ENG-001–003 reports and navigation are preserved in Git history through `fcb460f8ec3098372605635a5c40b823faff1d2d`; this update restores compact root documentation/navigation, `AGENTS.md`, the mission template, and `.gitignore` without changing campaign source or result files. The RA-ENG-004 commit was replayed safely on top of the latest remote commit. README conflicts were resolved by retaining researcher campaign text and adding mission links; local `main` is a fast-forward descendant of `origin/main`.

## RA-ENG-004 evidence audit

The [mission report](missions/RA-ENG-004-instrumentation.md) records source findings, implementation, parameters, failures, limits and commands. The [metric schema](methodology/g1-packet-grant-metrics.md) distinguishes application packets, FlowMonitor IP-layer counters, applied gNB MAC grants and radio/mobility traces. Source replay patches apply with `--unidiff-zero --whitespace=error` to clean pinned ib-ORAN and NR archives. The ns3 target built, three analyzer tests passed, and target-only/all-six/UL/DL/no-traffic/short-sink cases completed. Normal UDP application event counts reconcile with FlowMonitor; the intentionally short sink records 20 censored application receptions while FlowMonitor confirms IP-layer reception, so this is not labelled network loss. Raw evidence is preserved under ignored `simulator/logs/RA-ENG-004-20261112/`; all 55 file hashes verified.

The first local delivery commit was `43e173d`; after safe replay on the latest source snapshot, the implementation commit was `943716e`. The three-commit delivery was pushed as a fast-forward at `b75c5784d0ab928080037f6afa22ab97af359e10`; remote `main` matched on verification and the worktree was clean. No force-push or remote overwrite occurred. The post-rebase audit covered 21 paths (about 99 KB; largest 33,916 bytes), with no credential-pattern hits, generated simulator/source/build/virtualenv paths, or broken local links. GitHub issue #17 was updated with evidence and closed as completed.

## Campaign v2 evidence

The latest campaign README reports 92/160 successful cells at packaging, two incomplete attempts, and 68 not completed. The editable source overrides and source-map checksums are part of that package. Its analysis and results remain in progress; the invalidated v1 packet-tag latency/PDR summaries are explicitly excluded. This audit does not treat the RA-ENG-004 smoke runs as campaign results and does not claim formal campaign completion.

## RA-ENG-005 load calibration

The template-based [RA-ENG-005 report](missions/RA-ENG-005-load-calibration.md) preceded source inspection. Four fixed seed-11 probes ran: target-only, six-UE low, DL-only increment, and UL-only increment. The [method/results](methodology/g1-load-calibration.md) and [curated table/figures](../results/RA-ENG-005/) distinguish configured offer, generated packets, received goodput, censoring and received-packet tails. All per-flow packet counters reconcile in the six-UE cases. The DL arm shows source-evidenced queue/grant contention; the UL arm retains 448 grant rows whose RNTIs do not match its end-of-run flow map. One malformed DL grant row was excluded only from a derived parser input and retained in a cleanup record; raw stdout is unchanged. Exactly one seed per case supports calibration only. Candidate 20 kbps low and 6 Mbps one-direction high rates were returned for researcher selection, not frozen as formal factors. Full raw evidence and 76-file checksums are local under ignored `simulator/logs/RA-ENG-005-20261112/`; the integrated v2 campaign's absent local raw run tree remains separate. The delivery was pushed at `1fe55963eff05a665bac936864caa3cf6da0115d` after safe rebase from researcher-updated `bb940028f403a05433d20e1b71d6a000bfb718ab`; remote SHA matched and the worktree was clean. Staged audit found 19 paths/173,170 bytes, no credential patterns or generated source/build/virtualenv paths, and passed whitespace validation.

## RA-ENG-006 stock-scheduling probe

The template-first [mission report](missions/RA-ENG-006-stock-scheduling.md) and [source/control note](research/g1-stock-policy-controls.md) now record exact executable policy names, xApp Bypass/Clamp semantics, shared-memory and MAC grant path, source hashes, paired configuration, all six UEs' UL/DL outcomes, and the one-seed limits. A seed-11 RoundRobin/TopKCqi pair ran with all effective fields equal outside the dApp selector. Packet event counters reconcile for all 12 flows, no decision or applied-grant RNTIs are unmapped, and the per-UE applied grant distribution changed. The severe high-rate DL allocation and packet-service tradeoff is reported as observed, without treating one seed as a stable ranking. NetAnim's interleaved warning was removed losslessly during a new analysis pass; failed runner and comparator attempts remain preserved. `SHA256SUMS` under ignored `simulator/logs/RA-ENG-006-20261112/` covers run and reanalysis evidence. The code, configs, and docs are curated artifacts; simulator trees, raw logs, and derived raw-scale tables remain ignored.

The [RA-ENG-007 issue #20 gate](missions/KIRO-issue-24-execution.md) remains unsatisfied: the issue requires explicit researcher approval of channel scope, policy pair, direction, repetitions, and formal protocol. No formal campaign was started in this turn. RA-ENG-008 awaits validated formal campaign outputs; RA-ENG-009 awaits researcher-reviewed findings and authorization. Therefore KIRO #24 remains incomplete.

## Audit checks already performed for RA-ENG-004 delivery

- Three synthetic tests passed; pinned target build succeeded.
- Both source patches applied cleanly to fresh archives with zero-context replay.
- Raw run directory contained 55 hashed files; `sha256sum -c SHA256SUMS` passed.
- Before rebase, staged audit covered 18 text paths, about 130 KB; no credential-pattern hits or simulator/source/build/virtualenv/raw-output paths; `git diff --cached --check` passed and 91 local Markdown links resolved.
- The post-rebase path, size, credential, generated-artifact, whitespace, and link audit is complete. Recheck remote fast-forward state immediately before push and verify the resulting remote SHA afterward.
- RA-ENG-005 raw run checksums, malformed-grant cleanup metadata, per-UE result joins, source/config hashes and plotting outputs are included in the completed audit; staged-path and remote verification passed.
- RA-ENG-006 source/config hashes, paired-run event reconciliation, comparator output, and all run/reanalysis file checksums are included in the completed audit. Staged-path, credential, raw-data-size, source-tree, whitespace, link, and remote verification are recorded in the closeout commit after push.
