# Briosa Brand

**SpatialAnalyzer integration, simplified.**

The shared brand assets for the [Briosa product suite](https://github.com/spatialanalyzer/briosa).
**Brand version: v2.2.0**, the Caliper b identity and its interface system.

![Briosa brand overview](preview.png)

[Download the v2.2.0 brand pack](https://github.com/spatialanalyzer/briosa-brand/releases/download/v2.2.0/briosa-brand-v2.2.0.zip)
· [Brand guide](BRAND-GUIDE.md)
· [Release notes](https://github.com/spatialanalyzer/briosa-brand/releases/tag/v2.2.0)

## Assets

- `logos/`: horizontal, stacked, compact and wordmark SVGs, with and without the slogan, in color, inverse, black and white.
- `marks/`: the Caliper b symbol in its large and small cuts.
- `suite/`: matching server, .NET, JS, Python and docs lockups, plus compact Installer and Control Center logos for desktop app headers.
- `icons/`: dark and light application icons, a maskable icon and the favicon.
- `colors.css` and `colors.json`: exact reusable sRGB colors for dark and light themes, including interface surfaces and text-safe status colors.
- `desktop/`: `BriosaTheme.xaml`, a WPF resource dictionary with both themes' colors and the desktop type families.
- `fonts/`: the Saira, Inter and JetBrains Mono variable fonts and their original licenses, with WOFF2 web builds in `fonts/web/` and static desktop instances in `fonts/desktop/`.
- `source/`: the mark geometry, wordmark outlines, master SVG and rebuild scripts.
- `qa/`: visual proofs, the contrast matrix and the validation record.
- `manifest.json`: a machine-readable inventory of the SVG assets, fonts and token files.

All SVG artwork consists of vector paths and shapes. No embedded raster logo or font installation is needed.

The release ZIP also includes transparent PNG exports, platform icons, a
multisize ICO and file checksums. Generated raster exports and release archives
are kept out of Git; the overview and visual review proofs are committed.

Brand v2 replaces the v1 three-plane symbol and lowercase wordmark. Most files
keep their v1 paths; see [Changes From v1](BRAND-GUIDE.md#changes-from-v1)
before updating a consumer. Brand v2.2 leaves the artwork unchanged and adds
the interface system; see [Changes From v2.1](BRAND-GUIDE.md#changes-from-v21).

## Use in Another Repository

Download the approved release and copy only the assets that repository needs.
Record the source as `spatialanalyzer/briosa-brand@v2.2.0`, with the original
asset paths. Keep the required license notices with those copies. Builds can
then use their own committed files without fetching this repository at runtime.
The desktop theme finds its fonts by relative path, so copy
`desktop/BriosaTheme.xaml` together with `fonts/desktop/`.

This repository is the source of truth for artwork. Brand permissions,
trademarks and ownership remain governed by the
[organization's existing policy](https://github.com/spatialanalyzer/governance/blob/main/BRAND_AND_TRADEMARKS.md).

## Changes and Releases

See [source/README.md](source/README.md) to rebuild and validate the assets.
Use issues and pull requests for changes, and include updated visual proofs
when artwork changes. Keep previously published release tags fixed. Small
refinements can use subsequent tags such as `v2.3.0`; a new major identity is
not required for a small adjustment.

## License and Attribution

Except where separately identified, repository artwork, documentation and
scripts are provided under [Apache-2.0](LICENSE). Saira, Inter and JetBrains
Mono, including their web and desktop builds, are distributed under their SIL
Open Font Licenses, [fonts/Saira-OFL.txt](fonts/Saira-OFL.txt),
[fonts/Inter-OFL.txt](fonts/Inter-OFL.txt) and
[fonts/JetBrainsMono-OFL.txt](fonts/JetBrainsMono-OFL.txt); see
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). Trademark permissions are
separate from these copyright licenses.
