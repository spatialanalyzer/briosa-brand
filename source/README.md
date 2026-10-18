# Brand Source and Rebuild

The SVGs are editable vector shapes and outlined lettering.

- `build_brand.py` holds the Caliper b geometry in its approved stroke form for both cuts, the color themes, the lockup proportions and the supporting text. It converts the strokes to filled outlines, outlines all lettering from the fonts in `fonts/`, and writes every SVG, the preview, the color tokens and the manifest.
- `mark.json` is the readable record of the mark: the 256-unit grid, both cuts' strokes and ink bounds, the glow, the colors per theme and the motion specification.
- `wordmark.json` records the wordmark outline: BRIOSA in Saira at weight 600 and width 125 with 0.14 em letter spacing, its letter positions, ink box and path, and the vernier rule.
- `briosa-master.svg` is the stacked color logo with the slogan, as a vector editor entry point.

Both JSON records are written by the build. Edit `build_brand.py`, not the records or the generated SVGs.

The mark was selected on 2026-10-18 as "Caliper b" from the Scanline identity explorations; its identity sheet supplied the grid geometry and colors reproduced here. The wordmark, slogan and product labels are Saira outlines, and the preview's supporting text is Inter. No font binary is embedded in any SVG.

## Rebuild

Use Python 3.12 or newer and Node.js 24. Install dependencies from the
repository root, preferably inside a Python virtual environment:

```text
python -m pip install -r source/requirements.txt
npm ci --prefix source
```

From the pack root:

```text
python source/build_brand.py
node source/render_brand.cjs
python source/validate_and_package.py
```

`render_brand.cjs` resolves `sharp` from `source/node_modules/`. The optional
`BRIOSA_SHARP_MODULE` environment variable can point to an existing Sharp
module directory.

The build updates the committed SVGs, preview, color tokens, records and
manifest. Raster exports are written to the ignored `png/` directory and
ignored PNG/ICO files in `icons/`. Validation writes the ICO and the `qa/`
proofs, including a comparison of the outlined wordmark with FreeType's own
rendering of Saira. After all checks pass, it creates
`dist/briosa-brand-v2.0.0.zip` and a companion SHA-256 checksum file. The ZIP
contains file checksums as well.

The ZIP is assembled from explicit artifact paths; Git metadata, installed
dependencies and local environment files are excluded. It includes sources,
fonts, licenses, SVGs, PNGs, icons, the guide and validation records.

Inspect `preview.png`, `qa/wordmark-outline-comparison.png` and
`qa/variant-and-size-proof.png` after every artwork change. Automated checks
do not replace visual review. Commit updated vectors and proofs together.

## Releases

The root `VERSION` file identifies the brand release, currently `v2.0.0`.
Keep published tags fixed. To publish a later refinement, update `VERSION`,
the versioned download links and release wording, rebuild, inspect the
proofs, and publish a new tag with the ZIP and checksum from `dist/`.

## Fonts

`fonts/Saira-Variable.ttf` is `Saira[wdth,wght].ttf` from the
[Google Fonts Saira directory](https://github.com/google/fonts/tree/main/ofl/saira),
renamed, with Git blob `b7e017b39f1b3b82daeeccbd21c6c1f1cc3965b5`. Changing a
font changes the outlines, so rebuild and review the proofs after any update.
