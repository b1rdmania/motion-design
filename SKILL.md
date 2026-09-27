---
name: motion-design
description: >
  Help a user work out what their video should say, then turn that story into
  showreel-quality motion design, the way a creative director, motion designer and
  copywriter would. Use when the user wants a promo, launch film, brand film,
  explainer, social clip or title sequence made in code (for example with Blender,
  HyperFrames or Remotion), says "make a video for my product", "what should our
  video say", "direct this video", "plan the video", "treatment", "storyboard this",
  "review this render", "why does this video look generated" or "make it less AI",
  or wants an existing render critiqued against its brief. It runs discovery and
  narrative development with the user, writes a visual treatment and timed score,
  chooses the strongest toolchain, and reviews style frames, a moving draft and the
  final export. It does not render, and naming a renderer here does not route work
  through it. Not for UI micro-interactions, character animation or AI video generators.
license: MIT
---

# motion-design

This skill helps a user turn a business story, often an unclear one, into a narrative, and that narrative into excellent motion design.

The order matters. First find out what the film should say and to whom. Then decide how it looks, moves and sounds. Then build it with the strongest tools available and check that it lands. You can already animate. What usually goes wrong is the story and the decisions, so this skill spends its effort there.

## The bar

Make every film showreel quality: the piece a senior motion designer would put first in their reel, or send to audition for an A24 trailer. That is a standard of craft, not a look. A calm, minimal film can meet it; a busy one can miss it.

It means:

- one idea, held with conviction
- every frame composed as a still worth printing
- type set with care, not placed
- light, depth, texture or material where the medium allows
- a camera or edit with intent
- sound designed with the picture, not laid under it
- nothing in the film only because it was easy to make.

Competent is not the bar. If the result would pass as a good template, it has not met it.

## The workflow

| Step | Output | Mostly |
|---|---|---|
| 1. Understand the business | `plan/assets.json`, notes | reading |
| 2. Audience and stakes | answers in the treatment | conversation |
| 3. Develop the narrative together | chosen telling, last beat | conversation |
| 4. Visual treatment | `plan/treatment.md`, `plan/evidence.json`, `plan/score.json`, style frames | design |
| 5. Build | draft and final renders | the strongest toolchain |
| 6. Does it land? | `review/*/critique.json`, `DELIVERY.md` | judgement, supported by scripts |

To **review an existing film**, skip to step 6 and use its existing plan. If there is no timed plan, give a qualitative review and say which checks cannot run.

**How much to ask.** The conversation is central when the story is unresolved. When the user arrives with a clear brief, keep it light: confirm what you read, ask only what is missing, and move on. If the user has said to go ahead without them, make the calls yourself and mark them as assumed. Do not skip steps 2 and 3 just because you could guess.

`SKILL_DIR` means this directory. The project folder is wherever the user's film lives; it holds `plan/`, `renders/`, `review/` and `DELIVERY.md`. Run the scripts from there. Never report a review you did not perform.

## 1. Understand the business

Ask: "What are you building? What are you trying to get across? Where can I read about it?" Skip whatever the request already answers. Then read before asking anything else:

- the product, site or repo
- any positioning doc, pitch deck or brief
- the brand system.

Collect the real materials (`references/assets.md`): brand doc, font files, logo SVGs, colours, screenshots, images and footage. If you are given a repo, read its design doc, CSS variables, token or Tailwind config, `@font-face` rules and asset folders. Record everything in `plan/assets.json` with its source and licence. List what is missing. Never invent a brand.

## 2. Audience and stakes

Ask only what the material does not answer, in one conversational message:

1. Who is watching, and where? (feed, launch page, keynote, pitch, phone, sound on or off; length and aspect)
2. Who has to act after watching, and is the film told from their side?
3. **What is at stake?** What is hardest for them, or for the business, right now? What does the whole effort depend on? Always ask this one. The answer is usually where the film's tension is, and users rarely volunteer it.
4. What should change after they watch: what do they remember, and what do they do next?
5. How should it feel, and how should that feeling move? ("intrigue → recognition → confidence")
6. What should the film never show or claim?

Discuss tone and placement. If the positioning itself is unresolved, say so and help the user find one sentence they believe before designing anything.

## 3. Develop the narrative together

Offer two or three **genuinely different** ways to tell the story. Different means a different structure, not a different colour scheme. For each, in plain language:

- **Opening:** what the viewer sees and hears in the first three seconds, and why they keep watching.
- **Progression:** how the tension builds or the argument turns.
- **Ending:** the last image, line and sound, and what the viewer does next.
- **One line** on why it fits this audience.

Recommend one, and let the user choose or steer. Your first idea is usually the average of every video in its category, so push at least one option away from it. If the user supplied a concept, develop it; do not reject it for show.

Write the chosen telling, the proposition (one central idea), the refusal (what the film will not do) and the last beat into the treatment.

## 4. Visual treatment

Complete `plan/treatment.md` from `references/treatment.md`. Decide:

- composition and typography
- named references: what to take from each, and what to leave
- the craft decisions that will make it reel-worthy, including one **signature moment**: the shot someone would screenshot, or cut into a reel. Design it deliberately; a film of competent beats has none
- motion vocabulary, pacing and sound
- the lead: music, narration or visual (`references/sound.md`).

The treatment's refusals and references win over any tool's house style. If a workflow's defaults (glows, ghost text, stock decoratives) conflict with them, turn the defaults off.

Read `references/copy.md` and `references/motion.md` before writing the words and the beats.

Write `plan/evidence.json` (`references/evidence.md`). Every claim is typed `fact`, `inference`, `metaphor` or `sample`. Sample data and mock UI must never be presented as real results.

Write `plan/score.json` (`references/score.md`). This is the timed plan in seconds. For each beat, give:

- its job
- the evidence it relies on
- text cues with a start and a hold
- voiceover
- the focal element
- motion
- the transition in
- sound
- mandatory commitments.

Put beat starts on whole frames. Declare hard cuts, silences and hits in `events[]`, and embedded footage in `beats[].footage`. Set the delivery formats, the viewing width and the loudness target (default −14 LUFS, −1 dBTP).

**Choose the toolchain** (`references/toolchain.md`). Choose for the quality of each shot, not by habit or because a tool happens to be installed:

- Blender for light, material, depth and a real camera.
- HyperFrames or Remotion for type, UI and precise timing.
- ffmpeg for assembly and the mix.
- A combination is often best.

An explicit user choice wins, and a suitable existing toolchain stays. Record each choice and its reason in the treatment. If the best tool is missing, say what it would add, then set it up (`references/tool-setup.md`) or record the compromise.

Show the user representative **style frames** before the expensive build: one still per key beat at final size, checked at viewing width. Make the signature moment one of them. Present the treatment, the beat table and the frames. Wait for approval, unless the user said to go ahead without them.

## 5. Build

Read the adapter for each chosen tool in `adapters/`. **The plan decides what the film says and when. The tools decide how it moves.** Use each tool's own motion craft: its workflow skills, builders, effects, catalogue and physics. Replace only its intake and storyboard with the plan. Never hand-build a film just to avoid a workflow's planning step, because that throws away the renderer's craft.

Load brand fonts from the supplied files, so the renderer cannot substitute them. Build a moving draft (animatic) with the real audio before polishing. Then build the final.

## 6. Does it land?

Judge two things: does the film communicate what step 3 decided, and is the execution at the bar? The scripts support that judgement; they do not replace it.

```
python3 SKILL_DIR/scripts/check.py --plan plan --stills renders/style --stage style_frames --out review/style_frames-r1
python3 SKILL_DIR/scripts/check.py --plan plan --video renders/animatic.mp4 --stage animatic --out review/animatic-r1 [--audiomap plan/audiomap.json]
python3 SKILL_DIR/scripts/check.py --plan plan --video renders/final.mp4 --stage final --round 1 --out review/final-r1 [--audiomap plan/audiomap.json]
```

Pass `--audiomap` for a music-led film (`python3 SKILL_DIR/scripts/beatmap.py track.wav --out plan/audiomap.json` writes one). Then, using `references/review.md`:

1. **Watch it as the viewer would.** Open individual frames at viewing width, starting with frame 0: it is the thumbnail a muted scroller sees. Ask:
   - Does the story from step 3 come through?
   - Would this go first in a showreel (`judged.reel_bar`)?
2. **Get a cold read** (`judged.cold_viewer`). You know the plan, so you cannot see the film as a stranger does. If you can start a subagent, give a fresh one only the frames, sampled at about 4 per second (no plan, no brief, no treatment). Ask it:
   - Who is this for?
   - What is it?
   - What should I do next?
   - What was the one moment you remember?

   If you cannot start one, answer those questions strictly from the frames, as if you had never seen the plan. A film that is well made but unclear fails this: a blind judge preferred a plainer film that said who it was for in its first second.
3. **Settle each `needs_review` finding** with `scripts/resolve.py`, saying what you inspected. If you cannot tell (for example, you cannot listen), leave it open.
4. **Record accepted limits** with `resolve.py --accept-limit "..."`, so they reach the delivery note.
5. **Fix and re-render.** Blocking problems come first. Then, if `judged.reel_bar` fails, spend a revision round lifting the film towards the bar, usually the signature moment, before accepting it. Name what holds it back; do not just record it.

Review volume: when one inspection genuinely covers several findings, settle them together (`resolve.py --rule <rule> [--beat <id>]`). Evidence decisions carry across renders of the same plan (`resolve.py --carry-from <earlier critique.json>`). Never batch-pass what you did not look at.

**Budget:** up to two final revision rounds, unless the user asks otherwise. Then deliver with the open findings listed. Do not call an unresolved film finished. Do not edit the plan to make a failed check disappear. A real plan change is a dated amendment in the treatment, followed by a new review.

```
python3 SKILL_DIR/scripts/deliver.py --plan plan --video renders/final.mp4 --critique review/final-r<n>/critique.json --out DELIVERY.md
```

`<n>` is the latest round. For more formats, add `--also renders/final-16x9.mp4:review/final-16x9-r<n>/critique.json` for each one, so one report covers them all. The script exits non-zero if blocking findings are open, or if the critique does not match the render or the plan. `DELIVERY.md` includes asset and music provenance and the accepted limits. Give the user the render and the report. Say what was checked and what was not.

Planning needs no tools. Automated review needs ffmpeg, Python 3, numpy and Pillow (`references/dependencies.md`). If one is missing, say which operation it blocks and carry on with the rest.
