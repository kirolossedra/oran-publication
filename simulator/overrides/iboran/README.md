# ib-ORAN modified source — authoritative Git copy

`model/` contains the **full source files** we modified from the
pinned Orange ib-ORAN revision. These tracked paths are identical on
GitHub and WSL. `SHA256SUMS` records reviewed file hashes.

The simulator at `simulator/ns-3.48/contrib/iboran/model/` is an
**ignored local dependency checkout**, not another GitHub source export.
Each file here maps to the identical `model/` relative path in the
installed ib-ORAN tree. [sanity.py](../../../experiment-scripts/sanity.py)
checks and backs up any differences before copying these files.

Never run code from an unreviewed mismatch. When modifying scheduling
or packet instrumentation, update these canonical files and hashes.
[Upstream pins](../../DEPENDENCIES.md).
