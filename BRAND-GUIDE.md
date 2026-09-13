# Briosa Brand Assets

**SpatialAnalyzer integration, simplified.**

Brand version: **v1**. [Download the complete release pack](https://github.com/spatialanalyzer/briosa-brand/releases/download/v1/briosa-brand-v1.zip).

![Briosa identity overview](preview.png)

The selected identity combines the three-plane symbol, the custom Briosa wordmark, and a blue/cyan/gray palette. The deliverable logos are vector paths, including the slogan and product labels. They need no installed fonts or external resources.

## Choose an Asset

| Use | File |
| --- | --- |
| General logo on white | [Horizontal color logo](logos/briosa-horizontal-color.svg) |
| General logo on deep blue | [Horizontal inverse logo](logos/briosa-horizontal-inverse.svg) |
| Website hero or presentation with the slogan | [Stacked color logo with slogan](logos/briosa-stacked-tagline-color.svg) |
| Dark hero or cover with the slogan | [Stacked inverse logo with slogan](logos/briosa-stacked-tagline-inverse.svg) |
| Wide introduction with the slogan | [Horizontal color logo with slogan](logos/briosa-horizontal-tagline-color.svg) |
| Wordmark by itself | [Color wordmark](logos/briosa-wordmark-color.svg) |
| Avatar or compact product identity | [Color symbol](marks/briosa-symbol-color.svg) |
| Browser tab | [Favicon SVG](icons/favicon.svg), or the multisize ICO included in the release pack |
| Rounded application icon | [App icon SVG](icons/app-icon.svg) |
| OS-managed icon shape | [Square maskable icon SVG](icons/app-icon-maskable.svg) |

Every general logo arrangement also has `black` and `white` versions for one-color use. PNG counterparts are in `png/` with matching filenames. Transparent white artwork is intended for a dark background. The SVG canvas includes a small safety margin; retain additional clear space in the surrounding layout.

## Color

| Color | Hex | RGB | Intended Role |
| --- | --- | --- | --- |
| Deep blue | `#003875` | 0, 56, 117 | Primary brand, links, dark backgrounds |
| Cyan | `#00BAF1` | 0, 186, 241 | Upper plane, accents on dark backgrounds |
| Graphite | `#585B62` | 88, 91, 98 | Wordmark and body text on white |
| Silver | `#F2F2F2` | 242, 242, 242 | Soft surfaces, lower plane in inverse artwork |
| White | `#FFFFFF` | 255, 255, 255 | Light background, inverse wordmark and left plane |

These values come from [SpatialAnalyzer's public website stylesheet](https://www.spatialanalyzer.com/css/styles.css), inspected on September 13, 2026. They are the selected Briosa palette, not a claim to a vendor-issued brand specification. Reusable values are in [colors.css](colors.css) and [colors.json](colors.json). All artwork uses solid sRGB fills.

Graphite on white is **6.80:1** contrast; deep blue on white is **11.52:1**; deep blue on cyan is **5.10:1**. Use these combinations for normal text. Cyan on white is an accent treatment for the logo, not a normal-text color. See [WCAG contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

The inverse logo is designed for deep blue. Choose the all-white version on other sufficiently dark backgrounds when the cyan or silver would lose contrast. Use the black version for one-color light-background printing. A printer should make any required CMYK or spot-color conversion against a physical proof; the pack does not assign an unverified Pantone match.

## Size and Space

- Keep clear space of at least **half the lowercase `o` height** around a logo lockup. Around a standalone symbol, keep at least **one quarter of the symbol width**. Increase spacing when adjacent content is busy.
- Use a standalone symbol at **24 px wide or larger**. The supplied 16 px, 24 px, and 32 px favicon PNGs use an optical variant with slightly increased gaps between the same three planes.
- Use the horizontal logo without the slogan at **160 px wide or larger** and the standalone wordmark at **96 px wide or larger**.
- For the horizontal logo with the slogan, use at least **440 px width**. For the stacked logo with the slogan, use at least **360 px width**. At smaller sizes, use the version without the slogan and place the slogan separately as readable text.
- Preserve aspect ratio. Keep the three planes separate and in their original orientation. The lower plane is gray on light backgrounds; the upper plane remains cyan.

The size guidance is based on the included visual proof, not a promise that every output medium will reproduce fine detail equally. The artwork uses mathematical 30-degree diagonal directions and a normalized geometry closely matched to the selected concept.

## Typography and Wording

The wordmark is **custom outlined artwork** traced from the approved concept. It is not a font file, and it should not be recreated by typing `briosa` in another typeface. Preserve its distinctive diagonal `i` dot and the open `a` form. The portable source outlines are in [source/wordmark.json](source/wordmark.json).

The slogan and product descriptors use **Inter Regular**, converted to paths in the SVGs. The original variable font and its SIL Open Font License are included in `fonts/`. Inter also works as supporting text in documents and web interfaces. The logo does not require it to be installed.

Use the slogan exactly:

> SpatialAnalyzer integration, simplified.

Use this supporting product description where more explanation is needed:

> An open-source gRPC bridge to the SpatialAnalyzer SDK.

Write **Briosa** in prose and use the lowercase wordmark as supplied. Write **SpatialAnalyzer** as one word, with capital S and A. Product descriptions should explain that SpatialAnalyzer must be separately installed, licensed, and running.

## Product Suite

All products share the same master symbol and wordmark. Their text labels identify the product; different language logos or unrelated color schemes are unnecessary.

| Product | Color Asset | Inverse Asset |
| --- | --- | --- |
| Server | [server](suite/briosa-server-color.svg) | [server inverse](suite/briosa-server-inverse.svg) |
| .NET | [.NET](suite/briosa-dotnet-color.svg) | [.NET inverse](suite/briosa-dotnet-inverse.svg) |
| JavaScript | [JS](suite/briosa-js-color.svg) | [JS inverse](suite/briosa-js-inverse.svg) |
| Python | [Python](suite/briosa-python-color.svg) | [Python inverse](suite/briosa-python-inverse.svg) |
| Documentation | [docs](suite/briosa-docs-color.svg) | [docs inverse](suite/briosa-docs-inverse.svg) |

## Web and Application Use

Use SVG where supported and PNG where a platform requires raster images. PNG and ICO exports are included in the release pack. The PNG exports retain transparency. General logo PNGs are 1600 px wide, suite PNGs are 1200 px wide, and symbol PNGs are 1024 px wide. Application icon PNGs range from 16 to 1024 px. The ICO contains 16, 32, 48, 64, 128, and 256 px frames.

Example markup, with paths adjusted for the consuming site:

```html
<img src="/brand/logos/briosa-horizontal-color.svg" alt="Briosa" width="220">
<link rel="icon" href="/brand/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/icons/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/brand/icons/apple-touch-icon.png">
```

For a decorative repeated logo next to readable product text, use an empty `alt` attribute. For a linked logo that navigates home, use `alt="Briosa home"`. The standalone SVG files also include accessible titles and descriptions.

## Sources and Governance

- [Approved concept](source/approved-concept.png): the user-selected Vector Pulse design in SpatialAnalyzer-derived colors, with the selected slogan. Generated with the built-in ImageGen tool during this design session.
- [Vector master](source/briosa-master.svg): the outlined stacked master with the slogan.
- [Rebuild instructions](source/README.md): reproducible SVG, PNG and icon exports from the local master data.
- [Validation record](qa/VALIDATION.md): asset checks, outline comparison, and rendered size proofs.
- [Inter source](https://github.com/google/fonts/tree/main/ofl/inter) and [font license](fonts/OFL.txt).
- Project brand permissions and trademark questions are governed by [Briosa's existing Brand and Trademarks guidance](https://github.com/spatialanalyzer/governance/blob/main/BRAND_AND_TRADEMARKS.md).

The Briosa logo artwork contains no SpatialAnalyzer or Hexagon logo. The pack establishes no registration, ownership, certification, or official-vendor status. Technical rendering checks are not a trademark clearance search.
