---
name: motion-design
description: >
  Plan a video before it is built and review the render after, the way a creative
  director, motion designer and copywriter would. Use when the user wants a promo,
  launch film, brand film, explainer, social clip or title sequence made in code
  (HyperFrames, Remotion or Blender), says "direct this video", "plan the video",
  "treatment", "storyboard this", "review this render", "why does this video look
  generated", "make it less AI", or wants an existing render critiqued against a
  brief. It writes the treatment, evidence ledger and timed score, hands them to
  the renderer, and reviews style frames, an animatic and the final render with
  scripts plus frame inspection. It does not render; the renderer skill does
  (/hyperframes, Remotion, Blender). Not for UI micro-interactions, Lottie/Rive
  assets, character animation or AI video generators.
license: MIT
---

# motion-design

You direct. The renderer builds. Your job is to decide what the film says, how it feels and what it refuses to do, write those decisions down, and then hold the render to them.

You are already good at craft. This skill does not give you a house style. The film's own treatment and references set the style. Two briefs with different references should give two different films. The numbers in `references/defaults.md` are defaults; override any of them in the score with one line and a reason.

`SKILL_DIR` is this skill's directory. Work in the project folder:

```
plan/        treatment.md  evidence.json  score.json   (the contract)
renders/     style/<beat-id>.png  animatic.mp4  final.mp4
review/      <stage>-r<n>/critique.json + contact sheets + motion strip
DELIVERY.md
```

**The rule that makes this work:** each step writes a file, and the next step does not start without it. Do not skip a review because the render "looks fine". A review you did not run is a review you cannot report.

## 1. Intake

First, check that the tools are there: `ffmpeg -version`, `python3 -c "import numpy, PIL"`, and the renderer's CLI. If any are missing, tell the user before doing anything else.

Then read what already exists: a positioning doc, a brand system (`DESIGN.md`, tokens), an existing brief, the product itself. Then ask only what those do not answer. Ask in one message, conversationally:

1. Who watches this, and where? (feed, launch page, keynote, phone, sound on or off)
2. What should they remember, and what should they do next?
3. What should they feel? One word, or a short progression ("intrigue → recognition → confidence").
4. What will this video not do or show?

Also confirm: the brand source, the renderer, the aspect ratios, the length, and the delivery spec.

If the user says "just go", answer the four questions yourself from what you read. Write your answers in the treatment and mark them as assumed.

Do not start a positioning exercise. If the positioning itself is unresolved, say so and suggest fixing that first.

**Sizing.** A clip under 20 s uses the light path: treatment, score, style frames, final review. A longer film uses every step.

## 2. Treatment → `plan/treatment.md`

Use `references/treatment.md`. The fields that matter most:

- **Proposition.** One sentence. If it contains "and", pick one.
- **Tellings considered.** Write at least two structurally different concepts, and one line on why you chose this one. Your first idea is usually the average of every video in its category.
- **Refusal.** At least one thing the film will not show or claim.
- **Last beat.** Write it first. If you cannot write it, you do not have a film yet.
- **References.** 2–4 named, real works. For each: what to take, and what not to take. Do not describe the look with adjectives when a reference could show it.
- **Motion vocabulary.** 2–4 verbs this film uses, each with its meaning (for example: Inspect, Align, Resolve). Every animated beat uses one of them.
- **Lead.** `music`, `narration` or `visual`. This decides what gets timed first (see `references/sound.md`).

Then write `plan/evidence.json` (`references/evidence.md`). Every claim is typed `fact`, `inference` or `metaphor`. A metaphor may be unprovable. It must never be presented as a fact.

## 3. Score → `plan/score.json`

First read `references/copy.md` for on-screen text and VO, and `references/motion.md` for the beat design. Then use `references/score.md`. It is the timed plan in seconds, so any renderer can use it. For each beat, give:

- its job (what the viewer learns)
- the evidence it relies on
- on-screen text and its reading hold
- voiceover
- the focal element
- the verb
- build and hold
- the transition in
- the sound
- any mandatory commitments.

List detectable events (hard cuts, silences, hits) in `events[]`. Fidelity is checked against them.

Show the user the proposition, the last beat and a beat table. This is the cheap place to change the film. Wait for approval. If the user said to go ahead without stopping, show the plan and continue.

## 4. Hand off

Read the adapter for the renderer: `adapters/hyperframes.md`, `adapters/remotion.md` or `adapters/blender.md`. Give the renderer the treatment and the score as the contract. The renderer decides how to build, but it must not change what the plan says. To change the plan, record an amendment (see the budget rule in Step 5).

## 5. Review

There are three stages. Each stage gets its own review folder.

| Stage | Render | Review for |
|---|---|---|
| `style_frames` | one still per beat at final size → `renders/style/<beat-id>.png` | look, brand, one focal point, legibility at viewing size |
| `animatic` | low-res, no polish, with the real audio | timing, cuts, holds, sound continuity |
| `final` | delivery quality | everything, including loudness and evidence |

Run:

```
python3 SKILL_DIR/scripts/check.py --plan plan --stills renders/style --stage style_frames --out review/style_frames-r1
python3 SKILL_DIR/scripts/check.py --plan plan --video renders/animatic.mp4 --stage animatic --out review/animatic-r1
python3 SKILL_DIR/scripts/check.py --plan plan --video renders/final.mp4 --stage final --round 1 --out review/final-r1
```

`check.py` measures what it can and writes `critique.json`. It also lists the `needs_review` items only eyes can settle. Then:

1. Open the contact sheets (`contact.png`, and `contact-<width>px.png` at viewing width) and `strip.png`. Look at them. Do not reason from the JSON alone.
2. For every `needs_review` finding, set `pass` or `fail` and write what you saw in `evidence`. If you truly cannot tell, leave it as `needs_review` and add it to `unresolved`.
3. Fix blocking failures first, then the advice you agree with. Re-render and re-run `check.py` with the next round number.

What blocks and what only advises is in `references/review.md`. In short: integrity, communication, evidence, sound integrity and fidelity to the plan can block delivery. Craft defaults never block.

**Budget.** At most two revision rounds on the final. When the budget is used up, stop and deliver with the open findings listed. Do not declare success. Do not edit the plan to make a failed fidelity check disappear. A real plan change is an amendment: edit the plan, add a dated line under `## Amendments` in the treatment with the reason, and review again.

## 6. Deliver

```
python3 SKILL_DIR/scripts/deliver.py --plan plan --video renders/final.mp4 --critique review/final-r<n>/critique.json --out DELIVERY.md
```

`<n>` is the latest round. The script exits non-zero if the critique was made on another file or an older plan, or if blocking findings are open. Tell the user what it says. Give them:

- the render
- `DELIVERY.md`
- the open findings, in plain words.

Never call the film "professional" or "polished". Say what was checked and what was not.

## Requirements

ffmpeg and ffprobe on PATH, and Python 3 with numpy and Pillow. The optional beat grid for music-led films uses HyperFrames' `analyze-beatgrid.py` (Apache-2.0), which needs librosa. Without it, put cue points in the score by hand.
