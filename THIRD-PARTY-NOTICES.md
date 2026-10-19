# Third-Party Notices

## Saira

`fonts/Saira-Variable.ttf` is the original Saira variable font,
`Saira[wdth,wght].ttf`, obtained from the
[Google Fonts Saira directory](https://github.com/google/fonts/tree/main/ofl/saira)
and renamed. Saira is designed by Omnibus-Type; its upstream source is
[Omnibus-Type/Saira](https://github.com/Omnibus-Type/Saira). Its copyright
notice and SIL Open Font License are preserved in
[fonts/Saira-OFL.txt](fonts/Saira-OFL.txt). The license declares no Reserved
Font Name.

The Briosa wordmark, slogan and product labels in the SVG artwork are outlines
made from Saira. They are artwork, not a font or a modified version of Saira.

## Inter

`fonts/Inter-Variable.ttf` is the original Inter variable font, obtained from
the [Google Fonts Inter directory](https://github.com/google/fonts/tree/main/ofl/inter).
Its copyright notice and SIL Open Font License are preserved in
[fonts/Inter-OFL.txt](fonts/Inter-OFL.txt). The license declares no Reserved
Font Name.

Supporting text in the brand preview is outlined from Inter Regular, and the
validation proofs label their panels with it.

## JetBrains Mono

`fonts/JetBrainsMono-Variable.ttf` is the original JetBrains Mono variable
font, `JetBrainsMono[wght].ttf`, obtained from the
[Google Fonts JetBrains Mono directory](https://github.com/google/fonts/tree/main/ofl/jetbrainsmono)
and renamed. JetBrains Mono is designed by JetBrains; its upstream source is
[JetBrains/JetBrainsMono](https://github.com/JetBrains/JetBrainsMono). Its
copyright notice and SIL Open Font License are preserved in
[fonts/JetBrainsMono-OFL.txt](fonts/JetBrainsMono-OFL.txt). The license
declares no Reserved Font Name.

The system proof outlines its deviation steps, meter levels and a specimen from
it.

## Web and Desktop Font Builds

The build makes two sets of fonts from the variable fonts above. Both are
distributed under the same SIL Open Font License as their source font, whose
license file applies to them.

- `fonts/web/*.woff2` are the variable fonts in WOFF2 format, with every table
  and glyph outline unchanged. The signature-less `DSIG` table of Saira and
  JetBrains Mono is dropped, because WOFF2 encoding would invalidate it.
- `fonts/desktop/*.ttf` are static instances made with
  [fontTools](https://github.com/fonttools/fonttools): `Saira 106` and
  `Saira 125` in Medium and SemiBold, `Inter` in Regular, Medium and SemiBold,
  and `JetBrains Mono` in Regular and Medium. They are Modified Versions under
  the license. Each keeps its source font's copyright, trademark and license
  records, takes a family name for its instance, and drops the variation,
  `STAT` and `DSIG` tables. None of the licenses declares a Reserved Font Name.

## Build Tools

Python and Node dependencies are installed separately and retain their own
licenses. They are not vendored or bundled in brand releases.

## Product Names

SpatialAnalyzer and Hexagon product names are governed by the
[existing brand and trademarks policy](https://github.com/spatialanalyzer/governance/blob/main/BRAND_AND_TRADEMARKS.md).
The Briosa artwork includes no SpatialAnalyzer or Hexagon logo.
