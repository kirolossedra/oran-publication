# D-002 — Keep O-RAN simulator isolated from legacy NR-U

- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** historical project uses ns-3.35/NR v1.2 plus a separate NR-U extension and local compatibility patches.
- **Alternatives:** reuse/upgrade legacy checkout; install a new stack in place; create a separate project and simulator root.
- **Decision:** separate `oran-publication` Git repository and future ignored `simulator/` directory; never carry over old patches.
- **Reason:** preserve historical reproducibility and prevent stale headers, libraries, or patches contaminating the modern stack. This is a retrospective rationale based on repository separation and compatibility risk.
- **Consequences:** duplicate checkout/build storage will be needed when installation is authorized; stronger boundary and clean provenance.
- **Evidence:** [legacy manifest in historical archive](https://github.com/kirolossedra/nru-publication/blob/main/manifests/commits.txt), this repository's [environment manifest](../../manifests/environment.json).
