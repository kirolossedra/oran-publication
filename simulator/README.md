# Simulator index — why WSL and GitHub look different

**There is one tracked structure, plus deliberately excluded dependencies.**

| Path | In GitHub? | What is happening |
|---|---|---|
| [overrides/iboran](overrides/iboran/README.md) | Yes | **Canonical modified ib-ORAN source**, mirrored to WSL |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Yes | Exact upstream project source pins |
| `ns-3.48/` | No | Locally installed ns-3, NR, ns3-ai, ib-ORAN and build products |
| `tooling/` | No | Local activation/provisioning scripts |
| `runs/`, `logs/` | No | Raw experiment and diagnostics, kept locally |

It is unsafe to track the whole `ns-3.48/` directory in this parent Git
repository: it contains third-party nested repositories and massive builds.
The **tracked source of our modifications** resides instead at
`simulator/overrides/iboran/model/`, with the exact same WSL/GitHub path.
Before running, [sanity.py](../experiment-scripts/sanity.py) compares
that version to the local upstream installation, backs up differences and
copies the tracked version into the ignored checkout if authorized.

No other independent tracked export of source is permitted.
If fixing a simulator issue, update this tracked override and checksum
manifest, not just the ignored installed copy.
