# Mission history

- [Mission 0 — O-RAN migration preparation](missions/mission-0-migration.md): environment audit, version selection, isolated project preparation, and legacy preservation/retirement. Status is updated after publication and cleanup verification.
- [Mission 1 — Install and validate the ib-ORAN NR baseline](missions/mission-1-installation.md): complete; pinned stack installed and built, upstream NR toy baseline ran successfully, Python control loop and outputs verified.
- [RA-ENG-001 — G1 source feasibility audit](missions/RA-ENG-001-feasibility.md): **INCOMPLETE**; all four pinned sources are restored and the NR target plus Python bridge bindings build successfully. An isolated six-UE probe confirmed whole-cell LOS/NLOS helper behavior and repeatable mobility samples; the researcher selected whole-cell LOS/NLOS with mobility. Full-scenario runtime, applied-grant, traffic, and packet-tail evidence remains outstanding; the pinned CPU Torch wheels were unavailable from the configured index and alternate CDN.

Future work must use the [mission template](../templates/MISSION-TEMPLATE.md) and follow [AGENTS.md](../AGENTS.md).
