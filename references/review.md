# Review

Scripts measure limited properties and prompt inspection. No metric certifies craft. `pass` means only that the named check found its stated evidence; a detector match is not proof of a successful edit.

## Status and provenance

Findings use `pass`, `fail`, `needs_review` or `not_applicable`, with a `blocking` flag. Only confirmed failures or unresolved blocking review items prevent a clear delivery receipt. An uncertain measurement is not automatically a failure.

Each finding has an ID, rule, source, timestamp/beat, evidence and method. Original `status` and `evidence` remain intact. To resolve an uncertain finding, record what was actually inspected:

```sh
python3 SKILL_DIR/scripts/resolve.py --critique review/final-r1/critique.json \
  --finding f0007 --status pass --method 'frame inspection' \
  --evidence 'Viewed individual frames at 375px; headline fits and remains legible.'
```

The resolution stores its own status, evidence, method and date; the script recomputes counts and verdict. It cannot overwrite a measured failure. Re-render/re-check after correcting those. Leave unsupported judgments open; never invent listening or visual inspection. Delivery recomputes effective statuses rather than trusting cached counts.

## Artifact integrity

Full decode, required dimensions, fps and duration are checked against the plan. Drafts may use smaller dimensions at the same aspect ratio. Planned sound needs an audio stream, but stream presence alone does not prove audible content. Render and plan hashes bind the critique to the reviewed files. A solid frame is a review prompt, not proof of missing media.

## Communication

The planned reading-speed gate (`communication.reading_time_plan`) blocks when a text cue's planned hold gives more than 25 characters per second, or more than `delivery.max_text_cps` when that is set. It checks the **plan**, not the render. Whether the text actually appeared and could be read is a separate judged finding (`communication.rendered_text`, `communication.legible_at_view`).

Inspect actual text, its appearance/disappearance and readable interval in the moving render. Check individual frames at the intended viewing width; an entire contact sheet scaled to fit a window is not a valid phone-size test. Listen to required speech. If playback is unavailable, record that limit and leave the finding open.

## Evidence

See `evidence.md`. Missing required source fields and unknown claim IDs are deterministic ledger errors. Numeric detection is triage: numbers can be labels, and claims can have no numbers. Every beat gets a coverage review for actual words, speech and implied visual claims. The presence of a citation does not establish truth; inspect the source and scope.

## Sound integrity

See `sound.md#integrity`. Loudness/peak targets block only when explicit. Measurement failure is not intentional silence. Repeats and intelligibility require audio inspection; logs alone cannot settle them.

## Fidelity

Compare mandatory commitments with the actual frames. Cut/onset/silence detectors are heuristics. Misses become `needs_review`; inspect the boundary and, where useful, the renderer's timeline. Silence matching checks both start and end. Event tolerance defaults to two frames and can be set per event; audio adds two analysis windows of allowance.

A readable hold can contain camera travel, grain or secondary action. A pixel-difference still-run metric cannot verify readability and does not block delivery. A match cut may be a hard edit: inspect both the edit and its visual relationship.

## Beat review

`beat.review` is one blocking finding per beat, listing everything only eyes can settle there:
- the text cues and their planned timing
- the mandatory commitments
- the claims, including what the images imply about the viewer and their people (for example, a rota whose regulars are replaced by strangers implies Common replaces them).

Inspect the beat, then settle it with one resolution that addresses every item. If any item fails, mark it fail and name the item.

## Embedded footage

`fidelity.footage` compares three frames of each footage beat with its source at the declared in point and crop. A mismatch is `needs_review`: check sync, crop and colour. Honest before/after films depend on it.

## Does it land (judged)

- `judged.cold_viewer` (animatic and final): check each concrete claim a cold reader makes against the frames before acting on it; cold readers also misread. A fresh reader who sees only the frames (a subagent when available) says who the film is for, what it is, what to do next, and the moment they remember. Compare the answers with the treatment's intake. In testing, a blind judge preferred a plainer film that named its viewer in the first second over a better-designed one that did not.
- `judged.story` (final): watching as the viewer would, does the telling chosen in step 3 come through?
- `judged.reel_bar` (style frames and final): would this go first in a senior motion designer's showreel? Name what holds it back. "Competent" is a fail of the bar, not a pass.
- `judged.frame`, `judged.reskin`, `judged.transition`, `judged.pacing`: the craft questions per beat.

These do not block delivery on their own. They are where the film gets better, so settle them honestly.

## Accepted limits

Some limits you judge and accept: a note that is small at phone width, a slightly soft upscale. Record them with `resolve.py --accept-limit "…"`. They go into `DELIVERY.md` separately from open findings.

## Craft

Frame composition, brand fit, transition quality, rhythm and subjective sound are judged. `defaults.md` contains optional prompts. No mandatory quota of effects, stillness, references or variation applies.

## Sampling and stages

Inspect representative style frames before expensive rendering when useful. For moving drafts/finals, extract frame 0 (always: it is the feed thumbnail), hold boundaries, text-cue intervals, both sides of transitions and any flagged moments. Use `frames.py --at <seconds,...>` for additional samples. Review the moving sequence for temporal judgments; stills alone cannot settle them.

Run the chosen stages and preserve each critique separately. The default final revision budget is two rounds. When exhausted, deliver with limitations rather than relabelling unresolved work as successful. A material plan amendment or changed render invalidates the prior receipt.
