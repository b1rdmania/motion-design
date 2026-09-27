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

Reading speed calculations use the **plan**, not observed on-screen timing. More than 25 characters/second prompts review; it is not a universal failure. Only an explicit `delivery.max_text_cps` makes that plan limit blocking.

Inspect actual text, its appearance/disappearance and readable interval in the moving render. Check individual frames at the intended viewing width; an entire contact sheet scaled to fit a window is not a valid phone-size test. Listen to required speech. If playback is unavailable, record that limit and leave the finding open.

## Evidence

See `evidence.md`. Missing required source fields and unknown claim IDs are deterministic ledger errors. Numeric detection is triage: numbers can be labels, and claims can have no numbers. Every beat gets a coverage review for actual words, speech and implied visual claims. The presence of a citation does not establish truth; inspect the source and scope.

## Sound integrity

See `sound.md#integrity`. Loudness/peak targets block only when explicit. Measurement failure is not intentional silence. Repeats and intelligibility require audio inspection; logs alone cannot settle them.

## Fidelity

Compare mandatory commitments with the actual frames. Cut/onset/silence detectors are heuristics. Misses become `needs_review`; inspect the boundary and, where useful, the renderer's timeline. Silence matching checks both start and end. Event tolerance defaults to two frames and can be set per event; audio adds two analysis windows of allowance.

A readable hold can contain camera travel, grain or secondary action. A pixel-difference still-run metric cannot verify readability and does not block delivery. A match cut may be a hard edit: inspect both the edit and its visual relationship.

## Craft

Frame composition, brand fit, transition quality, rhythm and subjective sound are judged. `defaults.md` contains optional prompts. No mandatory quota of effects, stillness, references or variation applies.

## Sampling and stages

Inspect representative style frames before expensive rendering when useful. For moving drafts/finals, extract hold boundaries, text-cue intervals, both sides of transitions and any flagged moments. Use `frames.py --at <seconds,...>` for additional samples. Review the moving sequence for temporal judgments; stills alone cannot settle them.

Run the chosen stages and preserve each critique separately. The default final revision budget is two rounds. When exhausted, deliver with limitations rather than relabelling unresolved work as successful. A material plan amendment or changed render invalidates the prior receipt.
