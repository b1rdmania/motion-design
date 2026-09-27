# Sound

Sound is an editorial decision, not a layer added at the end. Choose the track early and cut the picture to it, not the other way round.

## Lead: what gets timed first

| Lead | Order |
|---|---|
| `music` | Pick the track. Map its phrases, energy and key moments. Time the shots to it. |
| `narration` | Lock the spoken argument and its pauses. Time the picture and music around the VO. |
| `visual` | Lock the key action or reveal. Build the sound around it. |

Beat alignment is available, not required. On calm music a beat tracker imposes a metronome that is not there, so pace by phrase and energy instead.

## Choosing music

Tempo alone does not prevent plodding music. Judge four things:

- **Phrase structure:** where it lifts, where it breathes, how long the phrases are.
- **Energy:** does it build to the film's key moment?
- **Instrumentation:** does it fit the brand? Leo names the usual way a premium film stops feeling premium: people "experiment with too much effects, add unnecessary sound effects and rap music" ([Leo, "Make your product videos look expensive"](https://x.com/leomeethewoo/status/2103529310208606701)).
- **Ending:** a real ending, not a fade because the track ran out.

Leo's tempo bands are a starting suggestion: 60–80 BPM regal and cinematic; 90–110 smooth and effortless; 115–123 kinetic and sophisticated; above that, drive and hype.

Record provenance and credits for every track in the score (`music.provenance`) and in the delivery.

## Sound effects

- Each effect needs a job: a physical action or a meaningful boundary. Write the job in the score.
- When the mix is done, listen through (or read the cue list) and remove anything too loud, out of place, or not helping the viewer understand.
- Keep tails. Never use an abrupt gate that clicks.

## Silence

Silence is a beat, not a gap.

- Drop the bed a beat *before* a reveal, not on it. Hold for 12–25 frames. Bring the bed back over 4–8 frames at or below its previous level.
- Keep low ambience under "silence". True digital silence reads as broken audio.
- Good places: after the hook, before a reveal, before the CTA. Not at the very top, since autoplay often starts muted.
- Declare every planned silence in `score.events` so it is checked, and so it is not flagged as a gap.

## Mix

- **HyperFrames:** `/hyperframes-audio` (ducking, voiceover carve, effect chains).
- **Remotion and Blender:** ffmpeg after the render.

```
# duck music under VO, then normalise to the delivery spec
ffmpeg -i music.wav -i vo.wav -filter_complex \
  "[0:a][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[m];[m][1:a]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=11" \
  mix.wav
ffmpeg -i picture.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

VO and SFX sources: `/media-use` in HyperFrames projects, or ElevenLabs, or your own recordings.

## Integrity

These findings can block delivery:

- Clipping: any sample at full scale.
- Loudness outside the delivery target (default −14 LUFS integrated ±1, true peak ≤ −1 dBTP). Streaming, broadcast and keynote targets differ, so set the target in `score.delivery`. A deliberately silent film is not a loudness failure.
- Unplanned gaps: silences not declared in `score.events` (`needs_review`).
- Repeated or doubled clips. No script measures this. Read the audio timeline or the assembly log.
- Unintelligible required speech.
