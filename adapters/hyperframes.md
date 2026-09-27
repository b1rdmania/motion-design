# HyperFrames adapter

HyperFrames builds the film. When installed, `/hyperframes` and its workflow skills own layout, motion code and rendering; otherwise use the renderer documentation. This skill owns the plan and the review.

**Fixture status: not yet run.**

## Handoff

Give the available HyperFrames renderer workflow the treatment and score as the agreed brief. Tell it:

- The storyboard is decided. Use `plan/score.json` for beat order, timing, copy and transitions. Do not replace it with a workflow's default arc.
- Visual style comes from the treatment's references and brand section. Use a house style or named palette only if the treatment asks for it.
- The music, VO and SFX are the ones named in the score.

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
npx hyperframes snapshot --at <t_b1>,<t_b2>,...
#   then copy each snapshot to renders/style/<beat-id>.png

# animatic
npx hyperframes render --quality draft --output renders/animatic.mp4

# final
npx hyperframes render --quality delivery --output renders/final.mp4
```

For a mid-hold time, use `start + build + (dur − build) / 2`.

Also run `npx hyperframes check` before each render. It catches overflow, collisions and runtime errors that this skill's review does not look for.

Read `transition_in.type` for the edit mechanism and `relationship` for visual continuity. Legacy `match:<property>` means a cut with a relationship, not a compulsory dissolve. Keep total duration fixed when adding overlap. Use the intended delivery size for each composition and review each final format.
