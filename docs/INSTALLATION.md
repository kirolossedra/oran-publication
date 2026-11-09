# Installation and reproducibility

This page records the upstream procedure and the verified Mission 1 installation. Full outputs remain under the ignored local simulator/ directory; this repository commits only the manifest and small curated KPI evidence.

## Selected and used layout

    self-research/oran-publication/
    ├── simulator/                     # ignored local installation
    │   ├── ns-3.48/
    │   │   ├── contrib/nr/             # 5G-LENA v5.1
    │   │   ├── contrib/ai/             # pinned ns3-ai
    │   │   └── contrib/iboran/         # pinned Orange ib-ORAN
    │   ├── envs/cpp/                   # local micromamba C++ dependency prefix
    │   ├── tooling/                    # local dependency bootstrap tooling
    │   ├── logs/                       # configure, build, install and run logs
    │   └── runs/<unique-id>/           # immutable run outputs
    └── docs, manifests, results/       # versioned research assets

No symlink, include path, or runtime library in this project points to the legacy NR-U checkout.

## Requirements and decisions

The official ib-ORAN install guide specifies ns-3.48, NR v5.1, ns3-ai main, Python 3.11+, GCC 11.1+ or Clang 17+, CMake 3.25+, Boost 1.89+, Protobuf 6.33+, pybind11 3.0+, and yaml-cpp. Installed revisions and versions appear in the environment manifest.

Host Python 3.12.3, GCC 13.3.0, and CMake 3.28.3 met those documented floors. Instead of changing system packages, Boost 1.89.0, Protobuf 6.33.5/protoc 33.5, and yaml-cpp 0.8 were provisioned under simulator/envs/cpp; pybind11 3.1.0 and the Python stack were installed into simulator/ns-3.48/.venv. CPU Torch 2.9.1 and torchvision 0.24.1 were selected because this baseline has no GPU requirement; the upstream requirements do not pin Torch and unconstrained pip resolution began selecting CUDA packages. That attempt was cancelled before installing Torch/CUDA, and evidence is retained locally. No system package was modified.

Upstream quick setup was inspected but not run blindly: it checks system include paths for Boost, installs broad Python requirements, registers an iboran.pth, builds, and offers an interactive test. The equivalent steps were carried out locally with explicit pins. ns3-ai examples were excluded as the upstream guide notes they do not build with ns-3.48; their source remained otherwise unmodified.

## Build and binding commands

All commands ran from simulator/ns-3.48 with CMAKE_PREFIX_PATH and LD_LIBRARY_PATH pointing to simulator/envs/cpp (and the pybind11 package directory), and the local Python venv activated.

    ./ns3 configure --enable-examples --enable-tests
    ./ns3 build ns3iboran_nr -j 2
    ninja -C cmake-cache -j2 proto-objects
    ninja -C cmake-cache -j2 iboran_shm_structure_py_binding

The supported ns-3 wrapper did not expose iboran_shm_structure_py_binding as a target, so its existing generated Ninja target was used. Protobuf objects were built first because the binding includes generated messages.pb.h. No upstream source file was modified. The NR target completed successfully, 1086/1086 steps. One nonfatal signed/unsigned comparison warning occurred in upstream ib-ORAN; ns3-ai emitted a nonfatal extra-semicolon warning. Full configure/build logs are under simulator/logs/. The Python extension and ns3ai_utils.Experiment import were verified in the project venv.

The manifest identifies the four exact upstream source revisions. The annotated ns-3 and NR tag object hashes are recorded separately from the peeled source commit hashes. The small [Python freeze](../manifests/python-environment-lock.txt) pins every installed Python package and editable ns3-ai commit; the [Linux C++ explicit lock](../manifests/cpp-environment-lock.txt) records exact conda-forge package artifacts.

## Baseline reproduction

Run from simulator/ns-3.48/contrib/iboran/model/iboran_campaign with the venv active and local C++ library path set:

    python3 iboran_run.py --rat_type=NR --k=3 --dapp_algo_ue_selection=ibTopKCqi --rng_run=5 --save_dapp_log=true

This completed as run 20261109-nr-toy-ibTopKCqi-k3-seed5, exit status 0. The default config uses six UEs, one gNB, 3.5 GHz, 10 MHz, one CC/BWP, numerology 1, 20 simulated seconds, TDD pattern DL|DL|DL|DL|F|UL|UL|UL|UL|F|, 512-byte UDP packets, 2 Mbps downlink and 1 Mbps uplink offered application bit rates, toy image data encoded to CLIP embeddings, dApp ibTopKCqi, xApp Bypass, and run/seed 5. Complete effective config, full execution output, scheduler trace, recovered payloads, NetAnim output, and exit marker are preserved in the ignored run directory. The exact pre-run default and effective config are both preserved.

The runner extracts FlowMonitor values and then deletes its transient .flowstats/iboran-flowstats.xml during successful cleanup. It does not leave packet-level records. A small KPI JSON, config and provenance summary are committed under results/mission1-nr-baseline/; full logs and potentially large files remain local. Do not rerun into an existing run directory.

## Host resources and logs

Before significant installation, free disk was 20 GiB and available RAM about 9 GiB of 15 GiB; build parallelism was limited to two jobs. After installation, build and run, 13 GiB remained. The source fetch, micromamba dependency transaction, pip requirements, CPU Torch install, Python freeze, configure, build, Protobuf generation, binding build, and run evidence logs are all local in simulator/logs/ and simulator/runs/<run-id>/.

## Practical reproduction

This is a record, not a one-command clean-room bootstrap script. Clone the four exact revisions, provision the recorded local C++ and Python dependencies, register the ib-ORAN pth, configure/build as above, generate the ns3-ai protobuf objects and extension, then run the command above. The exact local commands, environment variables, output paths, and troubleshooting are recorded in the Mission 1 report. Before rerunning, choose a new run ID and copy the produced output before upstream cleanup if retaining the transient FlowMonitor XML is needed; do not overwrite preserved run directories.

## Limitations

Package availability can change; reproduce the local C++ and Python environment from the committed lock manifests and full local install logs. The C++ lock is for linux-64 and Torch CPU wheels came from the PyTorch CPU index, so platform and index assumptions matter. Exact build flags and environment settings are recorded in the Mission 1 report. Upstream run cleanup removes FlowMonitor XML; if that raw transient file is needed in a later mission, add a preservation hook before cleanup and document the source change.

## Clean local reconstruction commands

These commands show the source placement and lock inputs for a linux-64 host with micromamba installed. They create a new isolated local tree and do not touch system packages. They have not been rerun on a second machine; package URLs and model hosting can change.

    mkdir -p simulator/ns-3.48/contrib
    git clone https://gitlab.com/nsnam/ns-3-dev.git simulator/ns-3.48
    git -C simulator/ns-3.48 checkout d2add90b452d600cfb4859baed8e9ea633519447
    git clone https://gitlab.com/cttc-lena/nr.git simulator/ns-3.48/contrib/nr
    git -C simulator/ns-3.48/contrib/nr checkout cedceadda17392c90587fb9400eb9b1f8c236713
    git clone https://github.com/hust-diangroup/ns3-ai.git simulator/ns-3.48/contrib/ai
    git -C simulator/ns-3.48/contrib/ai checkout b8c9858294b1d6a7f122b5154a3ce25057a54740
    git clone https://github.com/Orange-OpenSource/ns3-iboran.git simulator/ns-3.48/contrib/iboran
    git -C simulator/ns-3.48/contrib/iboran checkout 3ea5046389f0eb993cdf01ef6d6d33017e6921bb
    micromamba create -y -p simulator/envs/cpp -f manifests/cpp-environment-lock.txt
    python3 -m venv simulator/ns-3.48/.venv
    simulator/ns-3.48/.venv/bin/python -m pip install -r manifests/python-environment-lock.txt --extra-index-url https://download.pytorch.org/whl/cpu

From simulator/ns-3.48, configure/build and produce the binding:

    export CPP_PREFIX="$PWD/../envs/cpp"
    export CMAKE_PREFIX_PATH="$CPP_PREFIX"
    export LD_LIBRARY_PATH="$CPP_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    source .venv/bin/activate
    ./ns3 configure --enable-examples --enable-tests
    ./ns3 build ns3iboran_nr -j 2
    ninja -C cmake-cache -j2 proto-objects
    ninja -C cmake-cache -j2 iboran_shm_structure_py_binding
    printf '%s\n' "$PWD/contrib/iboran" > .venv/lib/python3.12/site-packages/iboran.pth

Then run the documented baseline command above from contrib/iboran/model/iboran_campaign. Preserve full output to a new unique directory before runner cleanup if the transient FlowMonitor XML is required. The CPU package lock is specific to Python 3.12/Linux x86_64; adjust only through a separately recorded environment validation if using another platform.
