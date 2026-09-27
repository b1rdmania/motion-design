# Assets

Build the film from the project's real materials. An invented brand is a generic brand.

## What to collect

Ask for these, or find them:

- **The project itself:** repo, live site, app build.
- **Brand source:** a design doc (`DESIGN.md`, brand guidelines PDF), colour tokens, type scale.
- **Fonts:** the actual font files (`.woff2`, `.otf`, `.ttf`) and their licence.
- **Logo:** SVG preferred, plus any lockup rules (clear space, minimum size, colour versions).
- **Imagery:** product screenshots, photography, illustration, footage, icons.
- **Sound:** any existing sonic identity, music licences, VO.

## Reading a repo

If you are given a repo, look for:

- `DESIGN.md`, `BRAND.md`, `docs/brand*`, `design/`
- CSS custom properties (`:root { --… }`), Tailwind config (`theme.extend.colors`, `fontFamily`), design-token JSON
- `@font-face` rules and font files in `public/`, `static/`, `assets/fonts/`
- logos and icons: `*.svg` in `public/`, `assets/`, `src/assets/`
- screenshots or marketing images already in the repo

Take exact values: hex colours, font families and weights, the logo file path. Do not paraphrase them.

## plan/assets.json

```json
{
  "assets": [
    {"id": "logo", "path": "brand/logo.svg", "role": "end lockup", "source": "repo: public/logo.svg",
     "licence": "owned by client", "mandatory": true},
    {"id": "font-display", "path": "brand/fonts/Inter-Display.woff2", "role": "headlines",
     "source": "repo: public/fonts", "licence": "SIL OFL 1.1"},
    {"id": "screen-home", "path": "assets/home.png", "role": "b3 product shot",
     "source": "supplied by user", "licence": "owned by client", "sample_data": true}
  ],
  "brand": {"colours": {"ink": "#0e2a38", "paper": "#f4f1ea"}, "type": ["Inter Display 500"],
            "source": "repo: DESIGN.md"},
  "missing": ["no sonic identity; music will be commissioned or generated"]
}
```

`deliver.py` copies the sources and licences into `DELIVERY.md`.

## Rules

- **Load fonts from the files.** Declare every brand font with `@font-face` (or the renderer's equivalent) pointing at the local file. Renderers substitute silently when a font name does not resolve: a HyperFrames render swapped a logo's Helvetica Neue for Inter in testing. Check the style frames for it.
- **Brand items become commitments.** The logo, brand fonts and exact colours go into the relevant beats' `commitments`, so the review checks them.
- **Sample data is labelled.** Mark screens with fake or sample data as `"sample_data": true`, and add a `sample` claim in `evidence.json`.
- **Licence notes do not block the work.** If a licence is unknown, write "unknown" and say so in the delivery. Do not stop.
- **Missing is written down.** If there is no logo SVG or no brand font, list it under `missing` and say what you used instead.
