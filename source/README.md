# Brand Source and Rebuild

The SVGs are editable vector shapes and outlined lettering.

- `wordmark.json` holds the approved custom wordmark outlines. This is the wordmark source of truth for rebuilding.
- `build_brand.py` holds the symbol's exact 30-degree plane geometry, color assignments, lockup dimensions and supporting text. It writes `symbol.json` as a readable geometry record and `briosa-master.svg` as a vector editor entry point.
- `approved-concept.png` records the selected design before vector production.
- `trace_wordmark.py` documents the one-time conversion of that image's lettering. Ordinary rebuilds use `wordmark.json` and do not retrace the image.

The wordmark preserves the approved form, including its custom curves and letter details. The icon uses normalized geometric parallelograms. The slogan and product labels are Inter Regular outlines. No font binary is embedded in any SVG.

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

The build updates the committed SVGs, preview, color tokens and manifest.
Raster exports are written to the ignored `png/` directory and ignored
PNG/ICO files in `icons/`. Validation writes the ICO and the `qa/` proofs.
After all checks pass, it creates `dist/briosa-brand-v1.zip` and a companion
SHA-256 checksum file. The ZIP contains file checksums as well.

The ZIP is assembled from explicit artifact paths; Git metadata, installed
dependencies and local environment files are excluded. It includes sources,
licenses, SVGs, PNGs, icons, the guide and validation records.

Inspect `preview.png`, `qa/source-outline-comparison.png` and
`qa/variant-and-size-proof.png` after every artwork change. Automated checks
do not replace visual review. Commit updated vectors and proofs together.

## Releases

The root `VERSION` file identifies the brand release, currently `v1`.
Keep published tags fixed. To publish a later refinement, update `VERSION`,
the versioned download links and release wording, rebuild, inspect the
proofs, and publish a new tag with the ZIP and checksum from `dist/`.

## Historical Trace

To regenerate the historical trace deliberately:

```text
python -m pip install potracer==0.0.4
python source/trace_wordmark.py source/approved-concept.png
```

Review any new trace before replacing the master paths. Re-run the full build afterwards.
