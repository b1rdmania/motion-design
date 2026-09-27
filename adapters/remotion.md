# Remotion adapter

Remotion builds the film in React. Its own agent skills (`remotion-dev/skills`) cover component patterns and rendering. This file maps the score onto a Remotion timeline.

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
      <Sequence key={b.id} from={f(b.start)} durationInFrames={f(b.dur)}>
        <Beat beat={b} />
      </Sequence>
    ))}
    <Audio src={staticFile("audio/mix.wav")} />
  </AbsoluteFill>
);

// Root: <Composition id="Film" component={Film} fps={fps}
//         durationInFrames={f(score.duration)} width={1920} height={1080} />
```

| Score | Remotion |
|---|---|
| `beats[i]` | one `<Sequence>` from `f(start)` for `f(dur)` frames |
| `transition_in: cut` | adjacent Sequences, no overlap |
| `match` / `morph` | overlap the two Sequences, or use `@remotion/transitions`, keeping the shared element continuous |
| `motion.build` / `motion.hold` | `interpolate(frame, [0, f(build)], …, {extrapolateRight: "clamp"})` inside the beat; no motion after `f(build)` |
| `super` | render from `f(build)`; hold for `f(hold)` |
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

Make the audio mix first (see `references/sound.md`), so the animatic already has the real timing.
