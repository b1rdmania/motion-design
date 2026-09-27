# Remotion adapter

Remotion builds the film in React. Its agent skills (`remotion-dev/skills`), when installed, can cover component patterns and rendering; otherwise use the renderer documentation. This file maps the score onto a Remotion timeline.

**Fixture status: not yet run.**

## Mapping

Convert seconds to frames once, in one place, and round to whole frames:

```tsx
import score from "../plan/score.json";
const fps = score.fps;
const f = (s: number) => Math.round(s * fps);

export const Film = () => (
  <AbsoluteFill>
    {score.beats.map((b) => (
      <Sequence key={b.id} from={f(b.start)} durationInFrames={f(b.start + b.dur) - f(b.start)}>
        <Beat beat={b} />
      </Sequence>
    ))}
    {/* Add audio only when the score calls for sound and the selected mix is available. */}
  </AbsoluteFill>
);

// Root: <Composition id="Film" component={Film} fps={fps}
//         durationInFrames={f(score.duration)} width={1920} height={1080} />
```

| Score | Remotion |
|---|---|
| `beats[i]` | one `<Sequence>` from `f(start)` for `f(start + dur) - f(start)` frames, avoiding rounding gaps |
| `transition_in: cut` | adjacent Sequences, no overlap |
| `match` / `morph` | match: adjacent Sequences may hard-cut while preserving a relationship; morph/dissolve: overlap or use transitions as the planned mechanism requires |
| `motion.build` / `motion.hold` | clamp only properties meant to settle; independent camera and secondary timelines can continue through readable holds |
| `super` | use explicit cue start/hold relative to the Sequence; legacy super defaults to build |
| each format | one `<Composition>` per delivery size |

## Renders for each stage

```
# style frames: one still per beat, mid-hold (frame number = f(start + build + (dur - build) / 2))
npx remotion still src/index.ts Film renders/style/b1.png --frame=<n>

# animatic: half scale, same aspect ratio
npx remotion render src/index.ts Film renders/animatic.mp4 --scale=0.5

# final
npx remotion render src/index.ts Film renders/final.mp4
```

When sound is planned, use representative audio in the animatic so its timing can be judged. A silent film needs no audio asset. See `references/sound.md`.

Read `transition_in.type` for the edit mechanism and `relationship` for visual continuity. Legacy `match:<property>` means a cut with a relationship, not a compulsory dissolve. Keep total duration fixed when adding overlap. Use the intended delivery size for each composition and review each final format.

## Quality

- Load brand fonts from local files (`@remotion/fonts` `loadFont`, or `@font-face` with `staticFile`), and wait for them before rendering frames. Check the style frames for substitution.
- Use `<OffthreadVideo>` for embedded footage, so frames stay exact. Declare the clip in `beats[].footage` for the sync check.
- `spring()` gives physical weight. `interpolate` with explicit easing gives editorial control. Choose per motion, not one for everything.
- For light and depth, render Blender plates and composite them (`references/toolchain.md`). `@remotion/three` suits simple 3D inside React.
