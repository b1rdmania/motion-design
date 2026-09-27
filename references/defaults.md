# Defaults

Craft numbers from the research. They give advice only and never block delivery. To break one on purpose, add it to `score.overrides` with a reason:

```json
"overrides": [{"rule": "default.pace_varies", "reason": "metronomic cut; the rhythm is the joke"}]
```

None of these values has been calibrated against real films yet. `check.py` marks them "not calibrated".

| Rule | Default | Why | Source |
|---|---|---|---|
| `default.hold_ge_build` | hold ≥ build | "A one-second static logo reads. A one-second animated logo is a smear." | title-sequence design practice (thelogocreative.co.uk) |
| `default.no_short_animation` | a beat under 1 s does not animate; cut to the resolved state | a sub-second build never resolves in the eye | as above |
| `default.pace_varies` | coefficient of variation of beat lengths ≥ 0.25 | uniform pacing is the most common amateur tell | editing craft; School of Motion |
| `default.cut_on_phrase` | music-led films cut within 2 frames of a beat or phrase | cuts off the grid feel accidental | frames per beat = (60 ÷ BPM) × fps |
| `default.super_speed` | ≤ 17 characters per second | adult subtitle norm | Netflix Timed Text Style Guide |
| `default.super_shape` | ≤ 42 characters per line, ≤ 2 lines | a third line is a second beat | Netflix |
| `default.vo_budget` | ≤ 2.5 VO words per second of film | ~75 words in a 30 s spot | ad practice |
| `default.stock_copy` | none of the stock openers or filler in `copy.md` | the phrases mark the copy as template output | copy research |
| `default.no_silence_at_top` | no planned silence in the first 0.5 s | autoplay starts muted | short-form editing practice |

Defaults that are not scripted, but worth knowing:
- Stagger related elements by 40–80 ms. Newly appearing siblings start no more than about 20 ms apart (Material motion).
- Anticipation runs 50–150 ms before a UI-scale action.
- Hold one to three key moments with effects. Hard cuts everywhere else.
