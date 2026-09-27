# Sound

Sound is an editorial decision. Choose the order that fits the film:

| Lead | Approach |
|---|---|
| Music | Select the track or compose a phrase, then time the picture around its energy. |
| Narration | Establish the argument and spoken pauses, then fit image and music. |
| Visual | Establish the action or reveal, then build sound around it. |

No music bed, narration, sound effect, paid provider or API key is required. Use supplied audio, original recordings/compositions, licensed libraries, local tools, or an available generation provider. In a HyperFrames environment, media-use may help if installed. Otherwise use an available workflow; do not demand that integration or ElevenLabs. Record source, licence/permission and required credits for every asset.

## Editorial choices

Choose music by phrase structure, energy, instrumentation, relevance and ending. Generated music often ignores its prompt: tracks come back the wrong length, stop pulsing early or go silent. Analyse every generated track before timing anything to it, and record the prompt. Tempo alone does not establish mood or quality; no genre is inherently inappropriate. Map beats only when useful. Deliberate silence, ambience, fades and an abrupt expressive stop are valid choices. Avoid unintended clicks, clipped tails, duplication or gaps.

Distinguish **silence** (the whole mix falls below a declared analysis threshold) from a **dropout** (for example, music stops while ambience continues). Do not declare a dropout as a measured silence. Set silence length and re-entry for the scene, not a fixed frame recipe.

Listen to the exported mix when possible. A cue list or assembly log can help diagnose a problem but cannot establish what the file sounds like. If listening is unavailable, leave speech intelligibility and subjective sound review unresolved and report that limitation.

## Audiomap

For a music-led film, map the track before timing the picture:

```
python3 SKILL_DIR/scripts/beatmap.py assets/music.wav --out plan/audiomap.json
```

It writes an estimated tempo, a beat grid, onsets, bass entries (below 150 Hz) and an energy curve. It is heuristic: check the grid and the key moments against the waveform or by ear. On calm or rubato music, write cue points by hand (`{"beats_sec": [...], "phrases": [{"start": ...}]}`). Pass it to `check.py --audiomap` and add `default.cut_on_phrase` to `score.review_hints` to compare cuts with it.

## Mixing

Use the renderer's audio tools or an external mix. HyperFrames audio skills are optional; Remotion and Blender do not have to use FFmpeg if another working mix already exists.

This FFmpeg example ducks music under narration. Values are illustrative; use the chosen delivery spec and measure the final encode. Set `film_duration` from the score, so a short mix cannot truncate the picture:

```sh
film_duration=30
ffmpeg -i music.wav -i vo.wav -filter_complex \
  "[0:a]apad,atrim=duration=${film_duration}[music];[1:a]apad,atrim=duration=${film_duration},asplit=2[side][voice];[music][side]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[m];[m][voice]amix=inputs=2:normalize=0,apad,atrim=duration=${film_duration},loudnorm=I=-14:TP=-1:LRA=11[a]" \
  -map '[a]' mix.wav
ffmpeg -i picture.mp4 -i mix.wav -filter_complex \
  "[1:a]apad,atrim=duration=${film_duration}[a]" \
  -map 0:v -map '[a]' -c:v copy -c:a aac -b:a 192k final.mp4
```

Verify that the picture itself has the planned duration. Do not use `-shortest` to hide a short audio stream. A deliberately silent export can omit the audio stream altogether.

## Integrity

- An explicitly selected loudness/true-peak specification can block delivery when missed. Without explicit targets, −14 LUFS ±1 and −1 dBTP are suggestions only.
- Samples near full scale trigger inspection; they do not prove waveform clipping.
- No gated loudness can mean silence, very quiet audio or an analysis failure. Only a declared silent film is automatically exempt; an unexpectedly zero-valued programme fails and uncertain measurements need review.
- Silence detection uses channel energies, a default −50 dB threshold, 0.25-second minimum and 20 ms windows. Configure `score.audio_analysis` for a different material. Both planned start and end are checked with the event tolerance plus analysis-window allowance; uncertain matches need inspection.
- Repeats and required speech need rendered-audio inspection. Do not mark them passed because the plan looks correct.
