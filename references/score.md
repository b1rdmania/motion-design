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
| `beats[].motion` | `build` = seconds until the beat resolves. `hold` = seconds it stays resolved. |
| `beats[].transition_in` | `cut`, `match:<shared property>` or `morph:<shared element>` |
| `beats[].commitments` | Mandatory items, for example "logo from brand/logo.svg" or "exact copy". Each one is checked by eye. |
| `events[]` | Detectable events only: `cut`, `silence` (with `dur`) and `hit`. A beat with `transition_in: "cut"` adds a cut event automatically. |
| `overrides[]` | Defaults this film breaks on purpose, with a reason |

Match cuts and morphs are not events. A scene-cut detector cannot see them, so they are reviewed by eye.
