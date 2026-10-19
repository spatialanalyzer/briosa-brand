# Briosa Brand Assets

**SpatialAnalyzer integration, simplified.**

Brand version: **v2.1.0**. [Download the complete release pack](https://github.com/spatialanalyzer/briosa-brand/releases/download/v2.1.0/briosa-brand-v2.1.0.zip).

![Briosa identity overview](preview.png)

The identity is **Caliper b**: a lowercase b drawn as a caliper. Its beam carries vernier ticks, and a cyan jaw slides down the beam and closes on a measured point in the bowl of the b. The wordmark is **BRIOSA** in wide Saira capitals, with an optional vernier rule beneath it. The palette is dark-first: the mark is designed on void, `#040B17`, and has a matched light version for clean-room surfaces, `#F3F7FB`.

Every deliverable is vector paths and shapes, including the wordmark, slogan and product labels. No installed font or external resource is needed.

## Choose an Asset

| Use | File |
| --- | --- |
| General logo on dark | [Horizontal inverse logo](logos/briosa-horizontal-inverse.svg) |
| General logo on light | [Horizontal color logo](logos/briosa-horizontal-color.svg) |
| Navigation bars, app headers, footers, under 250 px wide | [Compact horizontal logo](logos/briosa-horizontal-compact-inverse.svg) ([color](logos/briosa-horizontal-compact-color.svg)) |
| Desktop app navigation header that names the app | [Installer compact logo](suite/briosa-installer-compact-inverse.svg) or [Control Center compact logo](suite/briosa-control-center-compact-inverse.svg) |
| Splash screen, cover or hero | [Stacked inverse logo](logos/briosa-stacked-inverse.svg) |
| Hero or cover with the slogan | [Stacked logo with slogan](logos/briosa-stacked-tagline-inverse.svg) |
| Wide introduction with the slogan | [Horizontal logo with slogan](logos/briosa-horizontal-tagline-inverse.svg) |
| Wordmark by itself | [Wordmark](logos/briosa-wordmark-inverse.svg), or [with the vernier rule](logos/briosa-wordmark-ruled-inverse.svg) |
| Avatar or symbol, 64 px and up | [Symbol, large cut](marks/briosa-symbol-inverse.svg) |
| Symbol below 64 px | [Symbol, small cut](marks/briosa-symbol-small-inverse.svg) |
| Browser tab | [Favicon SVG](icons/favicon.svg), or the multisize ICO in the release pack |
| Application icon | [Dark tile](icons/app-icon.svg) or [light tile](icons/app-icon-light.svg) |
| OS-masked icon shape | [Full-bleed maskable icon](icons/app-icon-maskable.svg) |

`inverse` artwork is for dark backgrounds and `color` artwork for light ones. Every logo, wordmark and symbol also has `black` and `white` one-color versions. PNG counterparts are in the release pack's `png/` folder with matching filenames. Each SVG canvas includes a small safety margin; keep more clear space in the surrounding layout.

## The Mark

The mark is drawn on a 256-unit grid. Its geometry, colors and motion are recorded in [source/mark.json](source/mark.json).

- **Beam**: the stem and foot of the b, a square-ended L in ink.
- **Ticks**: vernier graduations to the left of the beam, in a quieter ink.
- **Jaw**: a cyan L beside the beam that closes on the point.
- **Point**: the measured point, centered in the bowl between the beam, the jaw and the foot.

Strokes are converted to filled outlines, so the artwork scales correctly in tools that do not scale strokes.

### Two Cuts

| Cut | Use | Detail |
| --- | --- | --- |
| Large | 64 px and up | Fifteen fine ticks, 24-unit strokes, a 9.5-unit point inside a soft cyan glow |
| Small | Below 64 px, app icons and favicons | Four heavy ticks, 30-unit strokes, a 15-unit point, no glow |

Sizes refer to the rendered 256-unit canvas. The small cut is designed and checked at 16, 24, 32 and 48 px; at 16 px the point is a soft two-pixel dot. The large cut's fine ticks blur below 64 px, so never use it there. The small cut stays correct at any larger size, which is why the app icons use it.

### Mark Colors

| Part | On dark (`inverse`) | On light (`color`) |
| --- | --- | --- |
| Beam | `#EAF3FF` | `#061A33` |
| Jaw | `#00BAF1` | `#0096D6` |
| Ticks | `#7690B0` large, `#9DB3CF` small | `#536C8C` |
| Point | `#FFFFFF` large, `#8BE7FF` small | `#0096D6` |
| Glow (large cut) | `#00BAF1`, radius 26, 20% opacity | `#00BAF1`, radius 24, 16% opacity |

One-color artwork uses a single color for every part and omits the glow.

### Motion

On screen, the mark can animate: the jaw slides down the beam and closes on the point, then a ring pings outward from the point. At rest the jaw is closed and the ring is invisible, which is why the static files have no ring.

| Element | Specification |
| --- | --- |
| Jaw | Starts 60 grid units up the beam and slides to rest; `1.1s cubic-bezier(.6,0,.3,1)` after `.3s` |
| Ring | Circle on the point: radius 16 and 3-unit stroke on the large cut, radius 15 and 1.25 px stroke on the small cut; `#8BE7FF` on dark, `#0096D6` on light. Fades in to 95% opacity, then grows to 2.7 times while fading out; `.9s cubic-bezier(.2,.8,.2,1)` after `1.2s` |
| Loop | For showcases only: 5 s cycle, jaw closed from 30% to 84%, ring pinging from 32% to 62% |
| Reduced motion | Show the closed mark without animation |

To animate an inlined SVG, target `[data-part="jaw"]` and add the ring as an unfilled circle on the point, at (141, 166) on the large cut or (144, 166) on the small cut:

```css
.briosa-mark [data-part="jaw"] { animation: briosa-jaw 1.1s cubic-bezier(.6, 0, .3, 1) .3s both; }
.briosa-ring { opacity: 0; transform-box: fill-box; transform-origin: center;
  animation: briosa-ping .9s cubic-bezier(.2, .8, .2, 1) 1.2s both; }
@keyframes briosa-jaw { from { transform: translateY(-60px); } }
@keyframes briosa-ping { 0% { opacity: 0; transform: scale(1); } 8% { opacity: .95; } 100% { opacity: 0; transform: scale(2.7); } }
@media (prefers-reduced-motion: reduce) { .briosa-mark *, .briosa-ring { animation: none; } }
```

## Wordmark and Vernier Rule

The wordmark is **BRIOSA** in Saira at weight 600 and width 125, with 0.14 em letter spacing, converted to outlines. Its source path and letter positions are in [source/wordmark.json](source/wordmark.json).

The optional vernier rule hangs below the wordmark like a caliper's scale. At a 60 px wordmark it is a 2 px line in the tick color, with 2 px ticks below it: minor ticks 7 px long, and jaw-colored major ticks 13 px long. The rule spans the wordmark exactly, from the B's stem to the A's foot, in twenty divisions of about 14 px with a major tick at every fifth. Its line sits 23 px below the baseline. It scales with the wordmark.

In the horizontal lockups, the ruled wordmark is centered on the mark's grid and the rule's line runs through the measured point. In the compact lockup, the baseline runs through the point.

## Color

All artwork uses solid sRGB fills, apart from the large cut's glow. Reusable tokens are in [colors.css](colors.css) and [colors.json](colors.json).

### Dark

| Token | Hex | Role |
| --- | --- | --- |
| `void` | `#040B17` | Dark background |
| `dark-ink` | `#EAF3FF` | Beam, wordmark, primary text |
| `dark-ink-2` | `#9DB3CF` | Secondary text, product labels, small-cut ticks |
| `dark-ink-3` | `#7690B0` | Tertiary text, large-cut ticks, vernier rule |
| `dark-jaw` | `#00BAF1` | Jaw, major ticks, links and accents |
| `dark-point` | `#FFFFFF` | Large-cut point |
| `dark-point-small` | `#8BE7FF` | Small-cut point, motion ring |
| `dark-edge` | `#223A53` | Icon tile edge and dividers; `rgba(120,190,255,.26)` over void |

### Light

| Token | Hex | Role |
| --- | --- | --- |
| `clean-room` | `#F3F7FB` | Light background |
| `light-ink` | `#061A33` | Beam, wordmark, primary text |
| `light-ink-2` | `#46607E` | Secondary text, product labels |
| `light-ink-3` | `#536C8C` | Ticks, vernier rule, tertiary text |
| `light-jaw` | `#0096D6` | Jaw, major ticks, point, motion ring |
| `light-link` | `#006DB6` | Links and accent text |
| `light-edge` | `#D6E2EE` | Icon tile edge |
| `light-line` | `#B9C9DB` | Dividers; `rgba(0,56,117,.24)` over clean room |

### Deviation Scale

A five-step scale from a scan's deviation color map, from −2 to +2 standard deviations. Use it for data, status and accent rules, never in the logo.

| Step | Dark | Light |
| --- | --- | --- |
| −2 | `#3E5BFF` | `#2E47D9` |
| −1 | `#00BAF1` | `#0096D6` |
| 0 | `#34F5C5` | `#10A985` |
| +1 | `#FFD23F` | `#D99A00` |
| +2 | `#FF4D6D` | `#DE2F55` |

### Contrast

On void, `dark-ink` is **17.61:1**, `dark-ink-2` **9.18:1**, `dark-ink-3` **5.99:1** and `dark-jaw` **8.72:1**. On clean room, `light-ink` is **16.21:1**, `light-ink-2` **6.03:1**, `light-ink-3` **5.01:1** and `light-link` **5.05:1**. All of these pass for normal text. `light-jaw` is **3.08:1**: use it for artwork and large text only, and `light-link` for links. See [WCAG contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and the [validation record](qa/VALIDATION.md).

The `#00BAF1` cyan carries over from v1. A printer should make any required CMYK or spot-color conversion against a physical proof; the pack assigns no unverified Pantone match.

## Size and Space

| Asset | Canvas | Minimum |
| --- | --- | --- |
| Horizontal logo | 735 × 266 | 250 px wide |
| Horizontal logo with slogan | 735 × 271 | 440 px wide |
| Stacked logo | 375 × 411 | 180 px wide |
| Stacked logo with slogan | 375 × 441 | 320 px wide |
| Compact horizontal logo | 511 × 136 | 100 px wide |
| Wordmark | 630 × 133 | 80 px wide |
| Ruled wordmark | 630 × 208 | 160 px wide |
| Symbol, large cut | 256 × 256 | 64 px |
| Symbol, small cut | 256 × 256 | 16 px; use the large cut from 64 px |
| Suite lockups | 667 to 845 × 136 | 28 px tall |
| Compact product logos | 511 × 142 to 147 | 170 px wide |

The minimums keep the vernier rule at least 1 px, the slogan at about 14 px and product labels at about 9 px. Below the horizontal logo's minimum, use the compact logo, whose small-cut mark stays legible. At smaller sizes, drop the slogan and set it as readable text instead.

- Keep clear space of at least the height of the wordmark's capitals around any lockup. The symbol's 256-unit canvas already includes its clear space; do not crop it.
- Preserve aspect ratio. Do not rotate, skew, recolor or rearrange the beam, jaw, ticks and point, and keep the jaw closed on the point in static use.
- Keep the jaw cyan in full-color artwork; on other backgrounds, choose the black or white one-color version.

## Typography and Wording

| Role | Typeface |
| --- | --- |
| Wordmark | Saira, weight 600, width 125, 0.14 em letter spacing, uppercase, outlined |
| Slogan in logos | Saira, weight 500, width 106, outlined |
| Product labels | Saira, weight 500, width 125, 0.16 em letter spacing, uppercase, outlined |
| Display and headings | Saira |
| Body and interface text | Inter |
| Code | [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) |

Saira and Inter are included in `fonts/` with their SIL Open Font Licenses. JetBrains Mono, also OFL, is not needed by any asset and is not bundled. Use the supplied outlined wordmark rather than typing BRIOSA; web interfaces that load Saira may set live text with the settings above.

Use the slogan exactly:

> SpatialAnalyzer integration, simplified.

Use this supporting product description where more explanation is needed:

> An open-source gRPC bridge to the SpatialAnalyzer SDK.

Write **Briosa** in prose; the capitals belong to the wordmark. Write **SpatialAnalyzer** as one word, with capital S and A. Product descriptions should explain that SpatialAnalyzer must be separately installed, licensed, and running.

## Product Suite

All products share the small-cut mark and the wordmark, followed by a divider and an uppercase product label.

| Product | Color Asset | Inverse Asset |
| --- | --- | --- |
| Server | [server](suite/briosa-server-color.svg) | [server inverse](suite/briosa-server-inverse.svg) |
| .NET | [.NET](suite/briosa-dotnet-color.svg) | [.NET inverse](suite/briosa-dotnet-inverse.svg) |
| JavaScript | [JS](suite/briosa-js-color.svg) | [JS inverse](suite/briosa-js-inverse.svg) |
| Python | [Python](suite/briosa-python-color.svg) | [Python inverse](suite/briosa-python-inverse.svg) |
| Documentation | [docs](suite/briosa-docs-color.svg) | [docs inverse](suite/briosa-docs-inverse.svg) |

Desktop app navigation headers are too narrow for a label beside the wordmark. The compact product logos keep the compact logo intact and set the product label under BRIOSA, right-aligned, in the same label style at half the wordmark's size. A label wider than BRIOSA is set to the wordmark's width, so CONTROL CENTER lines up with both ends. Each also has `black` and `white` versions for high-contrast themes.

| App | Color Asset | Inverse Asset |
| --- | --- | --- |
| Installer | [installer](suite/briosa-installer-compact-color.svg) | [installer inverse](suite/briosa-installer-compact-inverse.svg) |
| Control Center | [control center](suite/briosa-control-center-compact-color.svg) | [control center inverse](suite/briosa-control-center-compact-inverse.svg) |

## Web and Application Use

Use SVG where supported and PNG where a platform requires raster images. The release pack includes transparent PNG exports: logos 1600 px wide, suite lockups 1200 px wide and symbols 1024 px wide. Application icon PNGs range from 16 to 1024 px; the 16, 24 and 32 px files come from the favicon's tighter fit and the rest from the dark app icon. The ICO contains 16, 32, 48, 64, 128 and 256 px frames.

Example markup, with paths adjusted for the consuming site:

```html
<img src="/brand/logos/briosa-horizontal-color.svg" alt="Briosa" width="280" height="101">
<link rel="icon" href="/brand/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/icons/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/brand/icons/apple-touch-icon.png">
```

A Docusaurus navigation bar can use the documentation suite lockup at 32 px tall:

```ts
navbar: {
  logo: {
    alt: 'Briosa home',
    src: 'brand/suite/briosa-docs-color.svg',
    srcDark: 'brand/suite/briosa-docs-inverse.svg',
    width: 179,
    height: 32,
  },
},
```

For a decorative repeated logo next to readable product text, use an empty `alt` attribute. For a linked logo that navigates home, use `alt="Briosa home"`. The standalone SVG files also include accessible titles and descriptions.

Desktop applications should take their window and taskbar icons from the small cut: the [dark tile](icons/app-icon.svg) for an icon that reads on light and dark taskbars, or the [small-cut symbol](marks/briosa-symbol-small-inverse.svg) where a tile-less icon is preferred. Choose the compact logo for in-app headers below 250 px wide, or the app's compact product logo where the header names the app.

## Changes From v1

Brand v2 replaces the three-plane symbol and the traced lowercase wordmark. Most files keep their v1 paths, so consumers can update in place, but proportions and color tokens changed.

| v1 | v2 |
| --- | --- |
| Three-plane symbol in `marks/briosa-symbol-*` | Caliper b large cut at the same paths, plus `marks/briosa-symbol-small-*` |
| Lowercase traced wordmark | BRIOSA in Saira, plus `logos/briosa-wordmark-ruled-*` |
| Horizontal logo, 852 × 238 | 735 × 266, plus `logos/briosa-horizontal-compact-*` for small sizes |
| Stacked logo, 704 × 568 | 375 × 411 |
| Suite lockups, 600 × 192 with slash labels | Content-sized, 136 px tall, with a divider and uppercase labels |
| Deep-blue icon tiles | Void tiles with the small cut, plus `icons/app-icon-light.svg` |
| Color tokens `blue`, `cyan`, `graphite`, `silver`, `white` | Theme tokens; `cyan` continues as `dark-jaw` |
| Inter for the slogan and labels | Saira; Inter remains for body text |
| `fonts/OFL.txt` | `fonts/Inter-OFL.txt` and `fonts/Saira-OFL.txt` |
| `source/symbol.json` and the traced concept | `source/mark.json`; the wordmark is outlined from the font |

Deep blue `#003875`, graphite `#585B62` and silver `#F2F2F2` are retired from the identity.

## Sources and Governance

- Approved design: Caliper b, selected on 2026-10-18 from the Scanline identity explorations, as shown on its identity sheet and in the briosa.dev homepage prototype.
- [Mark geometry](source/mark.json) and [wordmark outlines](source/wordmark.json): readable records, written by the build from [build_brand.py](source/build_brand.py) and the fonts.
- [Vector master](source/briosa-master.svg): the stacked color logo with the slogan, as a vector editor entry point.
- [Rebuild instructions](source/README.md): reproducible SVG, PNG and icon exports.
- [Validation record](qa/VALIDATION.md): asset checks, outline comparison, contrast and rendered size proofs.
- [Saira source](https://github.com/google/fonts/tree/main/ofl/saira) and [license](fonts/Saira-OFL.txt); [Inter source](https://github.com/google/fonts/tree/main/ofl/inter) and [license](fonts/Inter-OFL.txt).
- Project brand permissions and trademark questions are governed by [Briosa's existing Brand and Trademarks guidance](https://github.com/spatialanalyzer/governance/blob/main/BRAND_AND_TRADEMARKS.md).

The Briosa logo artwork contains no SpatialAnalyzer or Hexagon logo. The pack establishes no registration, ownership, certification, or official-vendor status. Technical rendering checks are not a trademark clearance search.
