---
name: motion-design
description: >
  Plan a video or review an existing render against its brief.
  Use for treatments, storyboards, promos, explainers and motion-design critique.
  Writes a treatment, evidence ledger and timed score; hands off to the chosen
  renderer; reviews style frames, moving drafts and final output. Does not render
  or impose a house style. Not for UI micro-interactions or character animation.
license: MIT
---

# motion-design

Decide what the film should communicate, give the renderer a usable plan, and review the result. The treatment and brand set the visual language. This skill supplies decision prompts and verification, not a compulsory aesthetic.

## Start with the requested operation

- **Planning:** read existing positioning, brand and brief first. No renderer, Python package or audio service is needed.
- **Building with an available workflow:** preserve the agent's existing video skills or implementation approach when suitable. Check only the tools actually selected. The named adapters are optional examples, not a required route or an allowlist.
- **Reviewing existing work:** use its existing plan. Do not restart intake or require a new treatment merely to critique a film. If there is no timed plan, give a qualitative review and identify which fidelity checks cannot run.

For automated review setup, read `references/dependencies.md`. After choosing a missing renderer or audio service, consult `references/tool-setup.md` for optional setup links; it is not an installation checklist. Missing review tools do not prevent planning. Report only the affected operation and available fallback; do not introduce a generic approval stop.

`SKILL_DIR` means this directory. A new full project normally uses:

```
plan/       treatment.md  evidence.json  score.json
renders/    style/<beat-id>.png  animatic.mp4  final.mp4
review/     <stage>-r<n>/critique.json + extracted frames + contact sheets + strip.png
DELIVERY.md
```

Reuse an existing project structure when practical. Never report a review that was not performed.

## 1. Intake

Ask only material questions the supplied context does not answer:

1. Who watches, and where?
2. What should they remember and do next?
3. What should they feel, or how should that feeling develop?
4. What should the film avoid showing or claiming?

Resolve brand source, format, duration and delivery requirements from context where possible. Record reasonable assumptions and continue within the user's authorization. Suggest positioning work only when uncertainty about the product genuinely prevents a useful film.

Choose review depth by complexity and uncertainty, not a duration cutoff. A simple clip may need only a treatment, score, representative style frames and final review. A short but intricate sequence may need an animatic. Record the chosen path briefly.

## 2. Treatment and evidence

Use `references/treatment.md`. Establish the proposition, audience, emotional arc, ending, brand boundaries and delivery requirements. Consider different concepts or named references when they resolve a real creative question; do not manufacture a quota of either. A small motion vocabulary can help, but it need not classify every animation.

Use `references/evidence.md` for factual claims, inferences and visual metaphors. A source field is not proof. Keep claim wording and its limits tied to actual supporting evidence.

## 3. Timed score

Use `references/score.md`, with `references/copy.md`, `references/motion.md` and `references/sound.md` as relevant. Select a music-, narration- or visual-led approach. No audio provider or soundtrack is mandatory.

Plan each beat's job, focal element, readable text intervals, movement, transitions and sound. Record mandatory commitments separately from creative intentions. Holds keep essential information readable; they do not automatically freeze the scene.

Present the proposition, ending and beat table. Continue within existing authorization. Pause only for a material unanswered decision or a user-requested approval gate.

## 4. Build with the appropriate workflow, then review

Choose within the user's request and the host's applicable instructions:

1. Honour an explicit tool or workflow choice.
2. Preserve a suitable existing project's toolchain; do not migrate it merely because this skill includes an adapter.
3. Otherwise, let the agent choose among its available video skills, coding capabilities and tools based on the brief, asset needs, editability, runtime and cost. A combination is valid, such as Blender footage with another tool for typography and editing.

This skill does not default to HyperFrames, Remotion or Blender. `adapters/` contains optional integration examples for those tools, not an exhaustive list. Use an adapter only after choosing that tool. A different workflow needs no new adapter before work can proceed: give it the creative decisions, timing and delivery requirements, then review its standard video export.

Complement the chosen workflow's strengths. If it already plans, storyboards or reviews, reuse those artifacts and map the fields needed by these scripts rather than running two intake processes or imposing two competing story structures. Keep one source of truth for the current plan. Do not load or install another skill merely because it is named here.

Preserve the plan's actual commitments; implementation choices belong to the building workflow. Meaningful changes to approved timing, copy or commitments get a short amendment and a new review, rather than silently rewriting the target.

For the full path:

| Stage | Inspect |
|---|---|
| Style frames | Brand, composition, focus and legibility at intended viewing size |
| Moving draft with representative audio | Timing, continuity, holds, transitions and sound |
| Final export | Actual picture and audio, delivery requirements and fidelity |

Use these commands for the stages selected:

```
python3 SKILL_DIR/scripts/check.py --plan plan --stills renders/style --stage style_frames --out review/style-r1
python3 SKILL_DIR/scripts/check.py --plan plan --video renders/animatic.mp4 --stage animatic --out review/animatic-r1
python3 SKILL_DIR/scripts/check.py --plan plan --video renders/final.mp4 --stage final --round 1 --out review/final-r1
```

Read `references/review.md`. Inspect individual frames as well as contact sheets, and moving footage for temporal judgments. Listen to the exported audio when available. If playback/listening is unavailable, record the limitation and leave that judgment unresolved; a timeline or cue list is not equivalent.

Keep original script findings. Record reviewer decisions using `scripts/resolve.py`, which preserves the observation and refreshes counts. The renderer reads the current `critique.json`, not a chat paraphrase. Fix confirmed blocking problems first; craft suggestions are optional. No written exception is needed for every deliberate aesthetic choice.

## 5. Revision and delivery

Default budget: up to two final revision rounds, unless the user requests otherwise. At the budget, deliver with open findings listed; do not label an unresolved film successful. A new render or plan invalidates the previous review receipt.

```
python3 SKILL_DIR/scripts/deliver.py --plan plan --video renders/final.mp4 --critique review/final-r1/critique.json --out DELIVERY.md
```

The report exits non-zero when blocking findings remain or the plan/render hashes do not match. It still writes a report for honest delivery with limitations. Give the user the render and report, explaining material open findings. Describe observed results rather than asserting a professional-quality score.
