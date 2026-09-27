# Optional review prompts

No craft heuristic blocks delivery. These values are uncalibrated prompts, not research-established universal rules. A creator may retain a deliberate choice without writing an exception for every beat.

| Rule | Prompt |
|---|---|
| `default.super_speed` | Planned text above 17 characters/second: inspect reading effort at intended size. |
| `default.vo_budget` | More than 2.5 planned words/second: time and listen to the actual narration. |
| `default.stock_copy` | Familiar template phrasing: is it useful here or empty? |

Rhythm hints run only when requested via `score.review_hints`:

- `default.pace_varies`: flags beat-duration variation below 0.25 for discussion; uniform rhythm is not a failure.
- `default.cut_on_phrase`: with a supplied audiomap and music-led score, flags cuts more than two frames from a supplied beat/phrase. Off-grid cuts may be intentional; the map does not determine good editing.

`overrides: [{rule, reason}]` remains available to suppress recurring prompts. Existing override records remain valid. Older hints for short animation, silence at the start and hold/build ratios are retired; these are creative choices rather than default faults.
