# HyperFrames adapter

HyperFrames builds the film. When installed, `/hyperframes` and its workflow skills own layout, motion code and rendering; otherwise use the renderer documentation. This skill owns the plan and the review.

**Fixture status: not yet run.** Used in two test films (HyperFrames 0.8.79); the render and snapshot commands below worked as written.

## Handoff: keep HyperFrames' craft

HyperFrames' workflows carry real motion craft: `/motion-graphics` has a director and builder with a motion vocabulary and a catalogue of blocks, and `/general-video` builds each frame with a frame worker. Use them. Do not hand-build `index.html` to avoid their planning step. In testing, that produced a clearer idea with flatter motion than the plain workflow.

The clean handoff is a `BRIEF.md` in the HyperFrames project. When a `BRIEF.md` exists, `/hyperframes` skips its intent interview and runs the named workflow. Write one from the plan:

```markdown
---
workflow: general-video          # use motion-graphics only for a single-shot piece under ~10 s
flow: automation
storyboard: no                   # the plan's score is the storyboard
message: "<proposition>"
angle: "<chosen telling, one line>"
length: <seconds>s
aspect: <16:9 | 4:5 | 9:16>
audience: <audience>
narration: <yes | no>
capture: no
---
# <title>

The plan in ../plan/ is locked for **what and when**: beat order, timing (score.json, in seconds),
every text cue, commitments, brand assets (assets.json) and the evidence limits.
The workflow owns **how**: shot design, layout, motion, blocks, effects and transitions within each beat.
Do not add, remove, reorder or retime beats, and do not rewrite copy. Load fonts from the files in assets.json.
```

Then invoke `/hyperframes`. Check its shot plan or storyboard against the score before it builds. If it retimes or rewrites, correct it there.

**Keep it light.** You do not need to read every HyperFrames reference. Read `/hyperframes-core` for the composition contract and the workflow's own SKILL.md. For audio, use your own mix (`references/sound.md`) if HyperFrames' media tools ask for a HeyGen sign-in you do not have.

**House style.** HyperFrames' creative defaults (radial glows, ghost text, 2–5 decoratives per scene, ambient motion) are defaults, not requirements. When they conflict with the treatment's refusals or references, the treatment wins: say so in `BRIEF.md`.

**First frames.** In HyperFrames 0.8.80, the first frame of a sub-composition could render its raw CSS state before the timeline's t=0 state applied: all lines visible at once, or a blank frame. Set every animated element's initial state in CSS to match its t=0 state, and check the first frame of each sub-composition. A `fidelity.unplanned_cut` one frame into a scene is the tell.

## Mapping

| Score | HyperFrames |
|---|---|
| `duration`, `fps` | root composition `data-duration`, project fps |
| `beats[i]` | one composition or scene per beat, with `data-start = start` and `data-duration = dur` |
| `transition_in: cut` | a hard cut at `start`; no crossfade |
| `transition_in: match:<p>` / `morph:<e>` | match: may be a hard cut preserving `<p>`; morph: interpolate `<e>` as needed; overlap only when the edit calls for it |
| `motion.build` / `motion.hold` | essential content becomes readable after build; camera/secondary motion may continue during the hold |
| `super` | legacy super defaults to start + build; explicit super.start and text_cues start relative to the beat |
| `sound` cues, `events` silences and hits | audio tracks and automation; use available audio tools; `/hyperframes-audio` is optional |

## Renders for each stage

```
# style frames: one still per beat, mid-hold
npx hyperframes snapshot <project-dir> --at <t_b1>,<t_b2>,... --no-end -o <out-dir>
#   then copy each snapshot to renders/style/<beat-id>.png (--no-end stops an extra end frame shifting the order)

# animatic
npx hyperframes render --quality draft   # renders at full size; fast enough for an animatic --output renders/animatic.mp4

# final
npx hyperframes render --quality delivery --output renders/final.mp4
```

For a mid-hold time, use `start + build + (dur − build) / 2`.

Also run `npx hyperframes check` before each render. It catches overflow, collisions and runtime errors that this skill's review does not look for.

Read `transition_in.type` for the edit mechanism and `relationship` for visual continuity. Legacy `match:<property>` means a cut with a relationship, not a compulsory dissolve. Keep total duration fixed when adding overlap. Use the intended delivery size for each composition and review each final format.

**Fonts.** HyperFrames substitutes a font when the family name does not resolve: in testing, a logo's Helvetica Neue rendered as Inter. Declare each brand font with `@font-face` pointing at the file from `assets.json`, and check the style frames for it. HyperFrames' own checks can pass while a font falls back: in testing, an extra face with a weight range and a `unicode-range` stopped the regular weights loading. Before rendering, confirm in the page that every entry in `document.fonts` has status `loaded`.
