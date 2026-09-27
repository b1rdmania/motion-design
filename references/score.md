# Score

`plan/score.json` is the timed plan. All times are in seconds from the start of the film. The renderer turns seconds into its own timeline (see `adapters/`).

## Example

```json
{
  "title": "Repair shop app, 20 s cut",
  "lead": "visual",
  "fps": 24,
  "duration": 20.0,
  "delivery": {
    "formats": [{"name": "landscape", "width": 1920, "height": 1080},
                {"name": "phone", "width": 1080, "height": 1350}],
    "view_width": 375,
    "loudness_lufs": -14,
    "true_peak_dbtp": -1,
    "audio": true
  },
  "music": {
    "track": "assets/score.wav",
    "provenance": "licensed; see audio/PROVENANCE.md",
    "why": "slow piano phrase, one lift at 12 s, clean ending; no percussion to chop"
  },
  "beats": [
    {
      "id": "b1", "start": 0.0, "dur": 4.0,
      "job": "a broken bike waits a week in most shops",
      "proves": "wait-time",
      "super": {"text": "seven days\nfor a puncture.", "hold": 2.5},
      "vo": null,
      "focal": "one bike on a hook, small in a large dark workshop",
      "verb": "Inspect",
      "motion": {"build": 1.5, "hold": 2.5},
      "transition_in": "cut",
      "sound": {"cues": [{"t": 0.0, "what": "workshop room tone", "job": "sets the space"}]},
      "commitments": []
    }
  ],
  "events": [
    {"type": "cut", "t": 4.0},
    {"type": "silence", "t": 11.2, "dur": 0.6},
    {"type": "hit", "t": 12.0}
  ],
  "overrides": [
    {"rule": "default.pace_varies", "reason": "deliberately even, metronomic cut"}
  ]
}
```

## Fields

| Field | Notes |
|---|---|
| `lead` | `music`, `narration` or `visual` |
| `delivery.formats` | Every size you will render. `check.py` fails any other size. |
| `delivery.view_width` | The width the film will be seen at, in CSS px. Use 375 for phone. It is used for the legibility contact sheet. |
| `delivery.audio` | `false` for a deliberately silent film |
| `beats[].job` | What the viewer learns. If you cannot write one, cut the beat. |
| `beats[].proves` | An evidence id, a list of ids, or null |
| `beats[].super` | `{text, hold}`. Use `\n` for a line break. `hold` is how long the full text stays readable. |
| `beats[].motion` | `build` = seconds until essential information is readable; `hold` = its readable interval. Continuing motion is allowed. Optional `ongoing` describes it. |
| `beats[].transition_in` | An edit object `{type, relationship?, duration?}`; types include cut, dissolve, wipe, morph, continuous, custom. Legacy strings remain accepted. |
| `beats[].commitments` | Mandatory items, for example "logo from brand/logo.svg" or "exact copy". Each one is checked by eye. |
| `events[]` | Detectable events only: `cut`, `silence` (with `dur`) and `hit`. A beat with a cut mechanism adds a cut event automatically, including legacy `match:<property>`. Each event can set `tolerance_frames` (default 2). |
| `overrides[]` | Defaults this film breaks on purpose, with a reason |

A match cut can be instantaneous. For example, `{"type":"cut","relationship":"same circular shape"}` declares a cut to detect and a relationship to inspect. A morph need not contain a cut. Detector misses are uncertain, not proof of a timing failure.

## Whole frames

Put every beat start on a whole frame: a multiple of 1 ÷ fps (at 30 fps, 4.3667 is frame 131; 4.367 may round to frame 132). Renderers round differently. `check.py` flags off-frame starts (`plan.frame_aligned`).

## Embedded footage

A beat that plays other footage (a before/after, a screen recording, a clip) declares it:

```json
"footage": {"src": "inputs/before.mp4", "in": 0.0, "rect": [68, 120, 944, 531]}
```

`src` is relative to the project folder. `in` is the source time at the beat's start. `rect` is `[x, y, width, height]` in the render, and the whole frame if you leave it out. `check.py` compares frames from the render with the source (`fidelity.footage`). It skips its own cut and hold heuristics inside footage beats, because those cuts belong to the footage.

## Additional timing and review fields

- `text_cues`: optional list on a beat, each `{text, start, hold}`. `start` is relative to the beat; cues can overlap or appear while the camera keeps moving. Legacy `super` is retained and can also set `start`; otherwise it starts after `motion.build`.
- `sound.cues`: multiple sound cues are allowed; their `t` values are absolute film seconds. `events` also uses absolute film seconds. A musical dropout with ambience is a sound cue, not a measured `silence` event.
- `delivery.max_text_cps`: the planned reading-speed gate. Default 25 characters per second; it blocks when a cue exceeds it. Set it higher or lower with a reason. It checks the plan's timing only; the rendered text is checked on the frames.
- `audio_analysis`: optional `{silence_db: -50, min_silence: 0.25}`. Match these to the material. Silence findings report both detected boundaries.
- `review_hints`: optional list of rhythm prompts (`default.pace_varies`, `default.cut_on_phrase`). No rigid rhythm profile runs by default.
- Explicit `delivery.loudness_lufs`, `loudness_tolerance` and `true_peak_dbtp` govern blocking sound limits. The example's values are illustrative, not mandatory.

Keep cue times inside their beat/film and use positive holds. The example above illustrates one beat, not a complete 20-second film. Every rendered beat and mandatory text interval needs representation in a production score.
