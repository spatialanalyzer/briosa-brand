# Briosa Brand

**SpatialAnalyzer integration, simplified.**

The shared brand assets for the [Briosa product suite](https://github.com/spatialanalyzer/briosa).
**Brand version: v1.**

![Briosa brand overview](preview.png)

[Download the v1 brand pack](https://github.com/spatialanalyzer/briosa-brand/releases/download/v1/briosa-brand-v1.zip)
· [Brand guide](BRAND-GUIDE.md)
· [Release notes](https://github.com/spatialanalyzer/briosa-brand/releases/tag/v1)

## Assets

- `logos/`: horizontal, stacked and wordmark SVGs, with and without the slogan, in color, inverse, black and white.
- `marks/`: the three-plane Briosa symbol.
- `suite/`: matching server, .NET, JS, Python and docs logo lockups.
- `icons/`: application, maskable and favicon SVGs.
- `colors.css` and `colors.json`: exact reusable sRGB colors.
- `source/`: editable vector data, the master SVG, approved concept, and rebuild scripts.
- `fonts/`: Inter variable font and its original license.
- `qa/`: visual proofs and the validation record.
- `manifest.json`: a machine-readable SVG asset inventory.

All SVG artwork consists of vector paths and shapes. No embedded raster logo or font installation is needed.

The release ZIP also includes transparent PNG exports, platform icons, a
multisize ICO and file checksums. Generated raster exports and release archives
are kept out of Git; the overview and visual review proofs are committed.

## Use in Another Repository

Download the approved release and copy only the assets that repository needs.
Record the source as `spatialanalyzer/briosa-brand@v1`, with the original asset
paths. Keep the required license notices with those copies. Builds can then
use their own committed files without fetching this repository at runtime.

This repository is the source of truth for artwork. Brand permissions,
trademarks and ownership remain governed by the
[organization's existing policy](https://github.com/spatialanalyzer/governance/blob/main/BRAND_AND_TRADEMARKS.md).

## Changes and Releases

See [source/README.md](source/README.md) to rebuild and validate the assets.
Use issues and pull requests for changes, and include updated visual proofs
when artwork changes. Keep previously published release tags fixed. Small
refinements can use subsequent tags such as `v1.1`; a new major identity is
not required for a small adjustment.

## License and Attribution

Except where separately identified, repository artwork, documentation and
scripts are provided under [Apache-2.0](LICENSE). Inter is distributed under
its [SIL Open Font License](fonts/OFL.txt); see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
Trademark permissions are separate from these copyright licenses.
