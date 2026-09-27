# HyperFrames adapter

HyperFrames builds the film. `/hyperframes` and its workflow skills own layout, motion code and rendering. This skill owns the plan and the review.

**Fixture status: not yet run.**

## Handoff

Give `/hyperframes` the treatment and the score as a locked brief. Tell it:

- The storyboard is decided. Use `plan/score.json` for beat order, timing, copy and transitions. Do not replace it with a workflow's default arc.
- Visual style comes from the treatment's references and brand section. Use a house style or named palette only if the treatment asks for it.
- The music, VO and SFX are the ones named in the score.

## Mapping

| Score | HyperFrames |
|---|---|
| `duration`, `fps` | root composition `data-duration`, project fps |
| `beats[i]` | one composition or scene per beat, with `data-start = start` and `data-duration = dur` |
| `transition_in: cut` | a hard cut at `start`; no crossfade |
| `transition_in: match:<p>` / `morph:<e>` | an overlapping transition that keeps `<p>` or `<e>` continuous |
| `motion.build` / `motion.hold` | the entrance timeline ends at `start + build`; nothing moves until `start + dur` except declared ambient motion |
| `super` | text layer present from `start + build` for `hold` seconds |
| `sound` cues, `events` silences and hits | audio tracks and automation; use `/hyperframes-audio` for ducking and carve |

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
