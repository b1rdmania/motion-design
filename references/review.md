# Review

`check.py` measures and lists. You look and decide. A check script cannot certify aesthetic quality, so the report always says which findings were measured and which were judged.

## Statuses

| Status | Means |
|---|---|
| `pass` | Checked, and it holds |
| `fail` | Checked, and it does not hold |
| `needs_review` | A script could not settle it. Look at the frames and set pass or fail. |
| `not_applicable` | The check does not apply to this film (no text, no claims, intended silence) |

An uncertain result is never a pass and never an automatic fail. If you look and still cannot tell, leave it as `needs_review` and add a line to `unresolved`.

Each finding has a `blocking` flag. Only blocking findings can stop delivery.

## Blocking categories

### Artifact integrity
The file decodes. Dimensions match a delivery format. fps and duration match the score (±2 frames). Audio is present when the score plans sound. Every style frame exists. A critique counts only for the render whose sha256 it records.

Flat frames (a solid field) are flagged `needs_review`, not blocking. They usually mean missing media, but a plate can be intended.

### Communication
- Reading time: over 25 characters per second of hold fails (blocking). Between 17 and 25 is advice.
- Legibility at viewing size: judged on `contact-<view_width>px.png`. Check size, contrast and hierarchy.
- Speech intelligibility: judged.

Not applicable when the film has no text and no speech.

### Evidence
See `evidence.md`. Unsupported facts, unknown claim ids and numbers without a claim fail. Metaphor wording and wording that differs from the permitted wording are judged.

### Sound integrity
See `sound.md#integrity`.

### Fidelity
Did the render do what its own plan says?

- Declared events (`cut`, `silence`, `hit`) happen within ±2 frames. Cuts and silences are measured and can fail. Hits use a rough onset detector: a miss is `needs_review`.
- Mandatory commitments are present and exact (judged; blocking).
- Holds: the longest still run in each beat compared with the planned hold. This is `needs_review` when short, because camera drift and grain read as motion.
- Cuts the plan did not declare are `needs_review` (a flash, a pop or an unplanned edit).

## Defaults (advice only)

See `defaults.md`. They never block. A default listed in `score.overrides` is left out of the findings and recorded under `overridden`.

## Judged

These are the questions scripts cannot answer. `check.py` lists them as `needs_review` (non-blocking):

- **Frame** (style frames and final, per beat): does it carry its job, with one focal point, on brand, and following a reference?
- **Reskin** (once): could these frames serve another brand with a text swap?
- **Transition** (animatic and final, per match or morph): does the shared property survive the boundary?
- **Pacing** (animatic and final, once): does the motion strip follow the treatment's feeling? Activity is measured. Good pacing is judged.

## Sampling

- Style frames: one still per beat, plus a sheet scaled to viewing width.
- Animatic and final, for every beat:
  - the start of the hold
  - the end of the hold
  - 3 frames before each transition
  - 2 frames after each transition.
- For anything the strip or a finding points at, run `frames.py --at <t1>,<t2>`.
- Read frames at full size when judging small text. Do not judge legibility from a thumbnail.

## The loop

1. Run `check.py` for the stage.
2. Open the contact sheets and the strip. Look.
3. Resolve every `needs_review` finding: set its status and write what you saw.
4. Fix blocking failures, then the advice you agree with.
5. Re-render and re-run with `--round n+1`.
6. Final stage budget: two revision rounds. Then deliver with `unresolved` filled in.

Never edit `plan/` so that a failed fidelity check passes. If the plan was wrong, amend it on purpose: add an entry under `## Amendments` in the treatment with the reason, then re-run the review. The plan version changes, so older critiques stop counting.
