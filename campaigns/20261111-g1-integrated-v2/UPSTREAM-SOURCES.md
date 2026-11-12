# Upstream library source map

The simulator dependencies are full upstream source repositories, pinned by the environment manifest. The campaign package carries complete source files for the ib-ORAN files that this work modified, under `source-overrides/model/`; the untouched dependency source remains available from these upstream repositories.

| Component | Pinned commit | Full source |
|---|---|---|
| ns-3.48 | `d2add90b452d600cfb4859baed8e9ea633519447` | [ns-3-dev at the pinned commit](https://gitlab.com/nsnam/ns-3-dev/-/tree/d2add90b452d600cfb4859baed8e9ea633519447) |
| 5G-LENA NR v5.1 | `cedceadda17392c90587fb9400eb9b1f8c236713` | [NR at the pinned commit](https://gitlab.com/cttc-lena/nr/-/tree/cedceadda17392c90587fb9400eb9b1f8c236713) |
| ns3-ai | `b8c9858294b1d6a7f122b5154a3ce25057a54740` | [ns3-ai at the pinned commit](https://github.com/hust-diangroup/ns3-ai/tree/b8c9858294b1d6a7f122b5154a3ce25057a54740) |
| Orange ib-ORAN | `3ea5046389f0eb993cdf01ef6d6d33017e6921bb` | [ns3-iboran at the pinned commit](https://github.com/Orange-OpenSource/ns3-iboran/tree/3ea5046389f0eb993cdf01ef6d6d33017e6921bb) |

The same pins and local checkout location are recorded in `manifests/environment.json`. Local source paths are `simulator/ns-3.48/src/`, `simulator/ns-3.48/contrib/nr/`, `simulator/ns-3.48/contrib/ai/`, and `simulator/ns-3.48/contrib/iboran/`.

## Applying the campaign's complete source files

From the repository root, copy each file under `source-overrides/model/` to the identical relative path under `simulator/ns-3.48/contrib/iboran/`. For example:

```sh
cp campaigns/20261111-g1-integrated-v2/source-overrides/model/iboran_application/iboran-application.cc simulator/ns-3.48/contrib/iboran/model/iboran_application/iboran-application.cc
```

`source-overrides/SHA256SUMS` records the exact copied files. No simulator build products, model weights, notebook data, animation outputs, virtual environments, or campaign run logs are included here.
