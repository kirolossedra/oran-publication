# WSL–GitHub parity: safe recovery of the broken checkout

**Observed:** Codex reported an empty `.git` directory in the previous WSL
workspace. Remote GitHub is being restructured into one tracked layout.
**No WSL synchronization has been performed or verified by this document.**

## Recovery sequence

1. Inventory processes, local paths, Git metadata, disk space and all
   source modifications. Do not modify a running simulation.
2. Keep the **entire original WSL directory intact**. Record its path,
   file hashes, original simulator dependency versions, and all raw runs.
   Create a separate timestamped preservation directory for local edits.
3. Clone GitHub `main` into an **adjacent clean sibling directory**,
   not on top of the broken `.git` tree. Check `git status`,
   `git rev-parse HEAD` and the new [root index](../README.md).
4. Compare tracked-like local files with the new clone; preserve any
   divergent copies rather than overwriting them. Legacy dated
   `campaigns/20261111-g1-integrated-v2/` and `scripts/` are retired.
   New authoritative paths: `experiment-scripts/`, `configs/`,
   `simulator/overrides/iboran/model/`, `docs/` and `tests/`.
5. Reattach local **ignored** `simulator/ns-3.48/`, `tooling/`,
   `runs/`, and `logs/` only after checking for collisions and
   absolute build-path assumptions. Existing pinned simulator checkouts
   are separate upstream Git repositories and must not become this
   research repository's tracked contents.
6. Promote the clean checkout to the desired working directory only
   when the old directory has been preserved and there are no active
   processes using it. Do not delete original evidence.
7. Verify `git status` and `git ls-files`; compare all tracked paths
   to GitHub `main`. Document intentional local-only dependency,
   build/env/raw/run/log exceptions.
8. Inspect copied ib-ORAN source against
   `simulator/overrides/iboran/model/`, then run
   `bash experiment-scripts/sanity.sh --apply-overrides`
   only after reviewing differences. Compile and run the 20-cell
   sanity; do not start the 160-cell campaign yet.

**Forbidden:** blind `git pull` or `git init` into empty `.git`,
hard reset, force-push, deleting local research outputs, overwriting
unknown modifications, or treating ignored upstream code as an
independent canonical version of this experiment.

**Acceptance:** GitHub and WSL have identical tracked file paths and
contents; old generated/third-party directories remain local-only;
no duplicate active date-coded export; preserved raw runs are untouched;
and the bounded sanity script executes with trustworthy high-throughput,
latency and starvation measurements.
